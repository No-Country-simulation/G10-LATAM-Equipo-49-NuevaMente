#!/usr/bin/env python3
"""Bootstrap idempotente de roles IAM para el bucket de NuevaMente.

Uso:
    python -m backend.scripts.bootstrap_iam_roles [--dry-run|--apply] [--verbose]

Por defecto hace dry-run. Con --apply escribe en OCI.
"""
import argparse
import sys

import oci
from oci.identity import IdentityClient
from oci.identity.models import (
    CreateGroupDetails,
    CreatePolicyDetails,
    UpdatePolicyDetails,
)

from src.storage.oci_config import load_oci_config

# ── Constantes de configuración ──────────────────────────────────────────
TENANCY_ID: str = ""  # se resuelve desde el config
COMPARTMENT_NAME: str = "Nuevamente"
BUCKET_NAME: str = "bucket-20260921-2152-nuevamente-docs-test"

GROUP_EMBEDDINGS: str = "nuevamente-embeddings"
GROUP_GENERATOR: str = "nuevamente-generator"
GROUP_RUNNER: str = "nuevamente-runner"

POLICY_EMBEDDINGS: str = "nuevamente-embeddings-policy"
POLICY_GENERATOR: str = "nuevamente-generator-policy"

# Usuario actual (el que ejecuta el script, para añadirlo a runner)
# Se resuelve desde la config de OCI.
CURRENT_USER_NAME: str = ""

# Statements de política (idempotentes: mismos textos = no drift)
STATEMENTS_EMBEDDINGS = [
    f"Allow group {GROUP_EMBEDDINGS} to read objects in compartment "
    f"{COMPARTMENT_NAME} where target.bucket.name = '{BUCKET_NAME}'",
    f"Allow group {GROUP_EMBEDDINGS} to manage objects in compartment "
    f"{COMPARTMENT_NAME} where all {{target.bucket.name = '{BUCKET_NAME}', "
    f"target.object.name = 'originals/*', "
    f"any {{request.permission = 'OBJECT_CREATE', "
    f"request.permission = 'OBJECT_OVERWRITE'}}}}",
]

STATEMENTS_GENERATOR = [
    f"Allow group {GROUP_GENERATOR} to read objects in compartment "
    f"{COMPARTMENT_NAME} where target.bucket.name = '{BUCKET_NAME}'",
    f"Allow group {GROUP_GENERATOR} to manage objects in compartment "
    f"{COMPARTMENT_NAME} where all {{target.bucket.name = '{BUCKET_NAME}', "
    f"target.object.name = 'generated/*', "
    f"any {{request.permission = 'OBJECT_CREATE', "
    f"request.permission = 'OBJECT_OVERWRITE'}}}}",
]


def _get_identity_client() -> IdentityClient:
    config = load_oci_config()
    return IdentityClient(config)


def _resolve_compartment_id(client: IdentityClient) -> str:
    """Busca el compartment OCID por nombre (Nuevamente) en la tenancy."""
    global TENANCY_ID
    TENANCY_ID = client.get_tenancy(config["tenancy"]).data.id
    compartments = oci.pagination.list_call_get_all_results(
        client.list_compartments, TENANCY_ID, compartment_id_in_subtree=True
    ).data
    for c in compartments:
        if c.name == COMPARTMENT_NAME and c.lifecycle_state == "ACTIVE":
            return c.id
    raise RuntimeError(f"Compartment '{COMPARTMENT_NAME}' no encontrado en la tenancy")


def _resolve_current_user_name(client: IdentityClient) -> str:
    """Obtiene el nombre del usuario autenticado (quien ejecuta el script)."""
    global CURRENT_USER_NAME
    user = client.get_user(config["user"]).data
    CURRENT_USER_NAME = user.name
    return user.name


def _get_group_id(client: IdentityClient, tenancy_id: str, name: str) -> str | None:
    groups = oci.pagination.list_call_get_all_results(
        client.list_groups, tenancy_id
    ).data
    for g in groups:
        if g.name == name and g.lifecycle_state == "ACTIVE":
            return g.id
    return None


def _create_group(
    client: IdentityClient, tenancy_id: str, name: str, description: str, dry_run: bool
) -> str:
    if dry_run:
        print(f"[DRY-RUN] Crear grupo: {name}")
        return "ocid1.group.dryrun"
    details = CreateGroupDetails(
        compartment_id=tenancy_id,
        name=name,
        description=description,
    )
    resp = client.create_group(details)
    print(f"[OK] Grupo creado: {name} ({resp.data.id})")
    return resp.data.id


def _ensure_group(
    client: IdentityClient, tenancy_id: str, name: str, description: str, dry_run: bool
) -> str:
    gid = _get_group_id(client, tenancy_id, name)
    if gid:
        print(f"[EXISTS] Grupo: {name} ({gid})")
        return gid
    return _create_group(client, tenancy_id, name, description, dry_run)


def _get_policy_id(client: IdentityClient, compartment_id: str, name: str) -> str | None:
    policies = oci.pagination.list_call_get_all_results(
        client.list_policies, compartment_id
    ).data
    for p in policies:
        if p.name == name and p.lifecycle_state == "ACTIVE":
            return p.id
    return None


def _create_policy(
    client: IdentityClient,
    compartment_id: str,
    name: str,
    statements: list[str],
    dry_run: bool,
) -> str:
    if dry_run:
        print(f"[DRY-RUN] Crear política: {name}")
        for s in statements:
            print(f"  Statement: {s}")
        return "ocid1.policy.dryrun"
    details = CreatePolicyDetails(
        compartment_id=compartment_id,
        name=name,
        description=f"Política de mínimo privilegio para {name}",
        statements=statements,
    )
    resp = client.create_policy(details)
    print(f"[OK] Política creada: {name} ({resp.data.id})")
    return resp.data.id


def _update_policy_if_drift(
    client: IdentityClient,
    policy_id: str,
    current_statements: list[str],
    desired_statements: list[str],
    dry_run: bool,
) -> bool:
    if current_statements == desired_statements:
        print(f"[OK] Política {policy_id}: sin drift")
        return False
    print(f"[DRIFT] Política {policy_id}: actualizando statements")
    if dry_run:
        for s in desired_statements:
            print(f"  Nuevo: {s}")
        return False
    details = UpdatePolicyDetails(statements=desired_statements)
    client.update_policy(policy_id, details)
    print(f"[OK] Política actualizada: {policy_id}")
    return True


def _ensure_policy(
    client: IdentityClient,
    compartment_id: str,
    name: str,
    statements: list[str],
    dry_run: bool,
) -> str:
    pid = _get_policy_id(client, compartment_id, name)
    if pid:
        # fetch current statements
        policy = client.get_policy(pid).data
        _update_policy_if_drift(client, pid, policy.statements, statements, dry_run)
        return pid
    return _create_policy(client, compartment_id, name, statements, dry_run)


def _add_user_to_group_if_missing(
    client: IdentityClient,
    group_id: str,
    user_ocid: str,
    dry_run: bool,
    tenancy_id: str,
) -> None:
    if dry_run:
        print(f"[DRY-RUN] Añadir usuario {user_ocid} al grupo {group_id}")
        return
    memberships = oci.pagination.list_call_get_all_results(
        client.list_user_group_memberships, tenancy_id, group_id=group_id
    ).data
    user_ocids = [m.user_id for m in memberships]
    if user_ocid in user_ocids:
        print(f"[OK] Usuario {user_ocid} ya es miembro del grupo {group_id}")
        return
    client.add_user_to_group(
        oci.identity.models.AddUserToGroupDetails(
            group_id=group_id,
            user_id=user_ocid,
        )
    )
    print(f"[OK] Usuario {user_ocid} añadido al grupo {group_id}")


def _print_rollback_instructions(
    embeddings_gid: str,
    generator_gid: str,
    runner_gid: str,
    embeddings_pid: str,
    generator_pid: str,
) -> None:
    print("\n=== COMANDOS DE ROLLBACK ===")
    print("# Eliminar membresías del runner")
    print(f"oci iam group remove-user --group-id {runner_gid} --user-id <OCID_DEL_USUARIO>")
    print("# Eliminar políticas")
    print(f"oci iam policy delete --policy-id {embeddings_pid} --force")
    print(f"oci iam policy delete --policy-id {generator_pid} --force")
    print("# Eliminar grupos")
    print(f"oci iam group delete --group-id {embeddings_gid} --force")
    print(f"oci iam group delete --group-id {generator_gid} --force")
    print(f"oci iam group delete --group-id {runner_gid} --force")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap IAM roles para el bucket de NuevaMente"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simula sin escribir (por defecto)",
    )
    parser.add_argument(
        "--apply",
        action="store_false",
        dest="dry_run",
        help="Aplica los cambios en OCI",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Salida detallada"
    )
    args = parser.parse_args()

    global config
    config = load_oci_config()

    client = _get_identity_client()
    compartment_id = _resolve_compartment_id(client)
    _resolve_current_user_name(client)

    print(f"Tenancy: {TENANCY_ID}")
    print(f"Compartment: {COMPARTMENT_NAME} ({compartment_id})")
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Usuario actual: {CURRENT_USER_NAME}")
    print(f"Modo: {'DRY-RUN' if args.dry_run else 'APPLY'}")
    print()

    # 1. Grupos (en tenancy)
    embeddings_gid = _ensure_group(
        client,
        TENANCY_ID,
        GROUP_EMBEDDINGS,
        (
            "Rol del agente de embeddings: lee todo el bucket, "
            "escribe solo en originals/"
        ),
        args.dry_run,
    )
    generator_gid = _ensure_group(
        client,
        TENANCY_ID,
        GROUP_GENERATOR,
        (
            "Rol del agente de generación: lee todo el bucket, "
            "escribe solo en generated/"
        ),
        args.dry_run,
    )
    runner_gid = _ensure_group(
        client,
        TENANCY_ID,
        GROUP_RUNNER,
        (
            "Runner de pruebas: hereda ambos roles "
            "(embeddings + generator)"
        ),
        args.dry_run,
    )

    # 2. Políticas (en compartment)
    embeddings_pid = _ensure_policy(
        client,
        compartment_id,
        POLICY_EMBEDDINGS,
        STATEMENTS_EMBEDDINGS,
        args.dry_run,
    )
    generator_pid = _ensure_policy(
        client,
        compartment_id,
        POLICY_GENERATOR,
        STATEMENTS_GENERATOR,
        args.dry_run,
    )

    # 3. Membresía: runner pertenece a ambos roles
    _add_user_to_group_if_missing(
        client, embeddings_gid, config["user"], args.dry_run, TENANCY_ID
    )
    _add_user_to_group_if_missing(
        client, generator_gid, config["user"], args.dry_run, TENANCY_ID
    )

    # 4. Rollback info
    _print_rollback_instructions(
        embeddings_gid, generator_gid, runner_gid, embeddings_pid, generator_pid
    )

    if args.dry_run:
        print("\n[DRY-RUN] No se escribieron cambios. Ejecuta con --apply para aplicarlos.")
    else:
        print(
            "\n[OK] Bootstrap completado. Espera ~1-5 min a que "
            "las políticas se propaguen en OCI."
        )
        print(
            "Después: crea objetos marcadores 'originals/' y "
            "'generated/' (0 bytes) y ejecuta smoke_bucket_real.py"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())