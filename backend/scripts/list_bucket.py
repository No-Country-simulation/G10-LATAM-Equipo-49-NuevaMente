"""Script de diagnóstico OCI: lista los objetos del bucket configurado.

Uso (desde backend/)::
    python scripts/list_bucket.py [--prefix PREFIX] [--limit N]
"""
import argparse

from src.storage.oci_client import OCIStorageClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Lista objetos del bucket OCI configurado")
    parser.add_argument("--prefix", default=None, help="Prefijo opcional para filtrar")
    parser.add_argument("--limit", type=int, default=100, help="Máximo de objetos por página")
    args = parser.parse_args()

    client = OCIStorageClient()
    query = client.list_objects(prefix=args.prefix, limit=args.limit)

    print("--- Lista de Objetos en el Bucket ---")
    for obj in query.objects:
        print(f"Object: {obj.name}")
        print(f"  Size: {obj.size}")
        estampa = obj.time_modified or "desconocida"
        print(f"  Last Modified: {estampa}\n")

    print(f"Total: {query.count}")
    if query.next_start:
        print(f"Hay más objetos. Usa start={query.next_start}")


if __name__ == "__main__":
    main()