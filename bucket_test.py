import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.oci_storage import OciStorageService

if __name__ == "__main__":
    service = OciStorageService()
    result = service.list_objects()

    print("--- Lista de Objetos en el Bucket ---")
    for obj in result["objects"]:
        print(f"Object: {obj['name']}")
        print(f"  Size: {obj['size']}")
        print(f"  Last Modified: {obj['time_modified']}\n")

    print(f"Total: {result['count']}")
    if result["next_start"]:
        print("Hay más objetos. Usa start=" + result["next_start"])