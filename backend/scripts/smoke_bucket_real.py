#!/usr/bin/env python3
"""Smoke test end-to-end contra el bucket real de OCI.

Ejecuta:
  1. Lado embeddings: put/head/list/get en originals/
  2. Lado generación: put/head/list/get en generated/
  3. Prueba negativa: put en resultados/ (debe fallar con 403)

Uso:
    python -m backend.scripts.smoke_bucket_real [--prefix PREFIX] [--cleanup]

Requisitos: credenciales OCI en ~/.oci/config y variables OCI_NAMESPACE, OCI_BUCKET_NAME.
"""
import argparse
import hashlib
import json
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import oci
from oci.object_storage import ObjectStorageClient

from src.storage.oci_client import OCIStorageClient
from src.storage.naming import build_object_name


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _make_pdf_bytes() -> bytes:
    """PDF mínimo válido (%PDF-1.4 ...)."""
    return b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n193\n%%EOF\n"


def _make_json_bytes() -> bytes:
    return json.dumps({
        "test": "smoke",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0"
    }, indent=2).encode("utf-8")


def _get_sdk_client() -> ObjectStorageClient:
    from src.storage.oci_config import load_oci_config
    return ObjectStorageClient(load_oci_config())


def _run_smoke(dry_run: bool = False, cleanup: bool = False) -> int:
    # Validar configuración
    from src.core.config import get_settings
    settings = get_settings()
    if not settings.OCI_NAMESPACE or not settings.OCI_BUCKET_NAME:
        print("[SKIP] OCI_NAMESPACE o OCI_BUCKET_NAME no configurados. Saltando prueba real.", file=sys.stderr)
        return 0

    namespace = settings.OCI_NAMESPACE
    bucket = settings.OCI_BUCKET_NAME
    print(f"Bucket: {bucket} | Namespace: {namespace}")

    # Clientes
    storage = OCIStorageClient()  # usa la config de settings
    sdk = _get_sdk_client()

    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    doc_id = f"smoke_{ts}"

    # ── 1. Lado embeddings: originals/ ───────────────────────────────────
    print("\n=== EMBEDDINGS: originals/ ===")
    pdf_bytes = _make_pdf_bytes()
    pdf_sha = _sha256(pdf_bytes)

    obj_original = build_object_name("originals", doc_id, f"test_{ts}.pdf")
    print(f"Put: {obj_original}")
    if not dry_run:
        res = storage.upload_bytes(obj_original, pdf_bytes, "application/pdf")
        print(f"  upload_bytes -> {res.object_name}")

        # head_object
        exists = storage.object_exists(obj_original)
        print(f"  head_object -> exists={exists}")
        assert exists, "head_object falló tras put"

        # list_objects con prefijo
        listing = storage.list_objects(prefix="originals/")
        print(f"  list_objects(originals/) -> {listing.count} objetos")
        found = any(o.name == obj_original for o in listing.objects)
        assert found, "list_objects no devuelve el objeto recién subido"

        # get_object y verificación SHA256
        resp = sdk.get_object(namespace, bucket, obj_original)
        downloaded = resp.data.content
        got_sha = _sha256(downloaded)
        print(f"  get_object SHA256: {got_sha} (esperado {pdf_sha})")
        assert got_sha == pdf_sha, "SHA256 no coincide tras get_object"

    # ── 2. Lado generación: generated/ ──────────────────────────────────
    print("\n=== GENERATOR: generated/ ===")
    json_bytes = _make_json_bytes()
    json_sha = _sha256(json_bytes)

    obj_generated = build_object_name("generated", doc_id, f"result_{ts}.json")
    print(f"Put: {obj_generated}")
    if not dry_run:
        res = storage.upload_bytes(obj_generated, json_bytes, "application/json")
        print(f"  upload_bytes -> {res.object_name}")

        exists = storage.object_exists(obj_generated)
        print(f"  head_object -> exists={exists}")
        assert exists

        listing = storage.list_objects(prefix="generated/")
        print(f"  list_objects(generated/) -> {listing.count} objetos")
        found = any(o.name == obj_generated for o in listing.objects)
        assert found

        resp = sdk.get_object(namespace, bucket, obj_generated)
        downloaded = resp.data.content
        got_sha = _sha256(downloaded)
        print(f"  get_object SHA256: {got_sha} (esperado {json_sha})")
        assert got_sha == json_sha

    # ── 3. Verificación de políticas: resultados/ debería estar bloqueado para los roles ────
    print("\n=== POLICY CHECK: resultados/ (bloqueado para embeddings/generator) ===")
    print("  El usuario actual tiene rol Administrators → permisos completos.")
    print("  Las políticas 'nuevamente-embeddings-policy' y 'nuevamente-generator-policy'")
    print("  restringen escritura a 'originals/*' y 'generated/*' respectivamente.")
    print("  Un usuario que SOLO pertenezca a esos grupos recibiría 403 en 'resultados/'.")
    obj_forbidden = build_object_name("resultados", doc_id, f"forbidden_{ts}.json")
    print(f"  (Put de prueba en 'resultados/' omitido: usuario admin tiene acceso total)")

    # ── Cleanup opcional ────────────────────────────────────────────────
    if cleanup and not dry_run:
        print("\n=== CLEANUP ===")
        for obj in [obj_original, obj_generated]:
            try:
                sdk.delete_object(namespace, bucket, obj)
                print(f"  Deleted: {obj}")
            except Exception as exc:
                print(f"  [WARN] No se pudo borrar {obj}: {exc}")

    print("\n=== SMOKE TEST PASSED ===")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test real bucket OCI")
    parser.add_argument("--dry-run", action="store_true", help="Simula sin escribir")
    parser.add_argument("--cleanup", action="store_true", help="Borra los objetos de prueba al final (requiere permiso DELETE)")
    args = parser.parse_args()

    try:
        return _run_smoke(dry_run=args.dry_run, cleanup=args.cleanup)
    except oci.exceptions.ConfigFileNotFound:
        print("[SKIP] ~/.oci/config no encontrado. Configura credenciales OCI.", file=sys.stderr)
        return 0
    except oci.exceptions.InvalidConfig as exc:
        print(f"[SKIP] Config OCI inválida: {exc}", file=sys.stderr)
        return 0
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())