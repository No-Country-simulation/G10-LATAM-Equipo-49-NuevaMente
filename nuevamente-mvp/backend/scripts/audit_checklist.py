"""
Ejecuta: python scripts/audit_checklist.py
Verifica automáticamente los ítems comprobables del Checklist Final (Fase 20).
Los ítems no comprobables por código (roles del equipo, proveedor LLM
confirmado formalmente) se listan aparte como recordatorio manual.
"""
import importlib
import pathlib
import subprocess
import sys

CHECKS_OK = []
CHECKS_FAIL = []


def check(name: str, condition: bool):
    (CHECKS_OK if condition else CHECKS_FAIL).append(name)


# --- Código ---
try:
    importlib.import_module("src.api.main")
    check("Backend importa sin errores", True)
except Exception:
    check("Backend importa sin errores", False)

check(".env.example existe", pathlib.Path("../.env.example").exists())

# --- Componentes (COMP-01..COMP-11) ---
components = {
    "COMP-01 Ingestion": "src/ingestion/service.py",
    "COMP-02 Processing": "src/processing/chunking.py",
    "COMP-03 Embeddings": "src/embeddings/factory.py",
    "COMP-04 VectorStore": "src/vectorstore/store.py",
    "COMP-05 RAG": "src/rag/retrieval_service.py",
    "COMP-06 Generation": "src/generation/orchestrator.py",
    "COMP-07 Validation": "src/validation/fidelity_checker.py",
    "COMP-08 Output": "src/output/assembler.py",
    "COMP-09 Storage": "src/storage/upload.py",
    "COMP-10 UI": "../ui/app.py",
    "COMP-11 API": "src/api/main.py",
}
for name, path in components.items():
    check(f"{name} implementado", pathlib.Path(path).exists())

# --- Tests ---
result = subprocess.run(["pytest", "tests/", "-q"], capture_output=True, text=True)
check("Suite de tests en verde", result.returncode == 0)

# --- Reporte ---
print("\n=== CHECKS AUTOMÁTICOS ===")
for c in CHECKS_OK:
    print(f"  [OK] {c}")
for c in CHECKS_FAIL:
    print(f"  [FALLO] {c}")

print("\n=== RECORDATORIOS MANUALES (no verificables por código) ===")
print("  - Proveedor de LLM/embeddings confirmado formalmente por el equipo (🔴 bloqueante)")
print("  - Roles Scrum reconciliados (Data/RAG Engineer, AI/LLM Engineer) — sección 10.1")
print("  - Prueba 8 (Fidelidad) ejecutada y documentada, no solo la Prueba 5 (Trazabilidad)")
print("  - Demo reproducible por un integrante distinto de quien la construyó")

if CHECKS_FAIL:
    sys.exit(1)
