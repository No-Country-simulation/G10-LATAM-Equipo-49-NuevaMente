"""Cargador de prompts versionados (PROMPT-001, PROMPT-002).

Los prompts se almacenan en `src/generation/prompts/` con versionado semántico
(`generacion_v1.txt`, `verificacion_v1.txt`) siguiendo la convención del
Plan Técnico Fase 15.
"""
import re
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """Carga un archivo de prompt desde `src/generation/prompts/`.

    Lanza:
        FileNotFoundError: si el archivo no existe.
    """
    path = PROMPTS_DIR / prompt_name
    if not path.exists():
        raise FileNotFoundError(f"Prompt no encontrado: {prompt_name}")
    return path.read_text(encoding="utf-8")


def parse_generation_prompt(raw: str) -> tuple[str, str]:
    """Parsea `generacion_v1.txt` y devuelve (system_prompt, user_template).

    El archivo tiene formato:
        SYSTEM:
        <texto del system prompt>

        CONTEXTO:
        <template del user prompt con variables {contexto}, {perfil}, etc.>

    Devuelve:
        (system_prompt, user_prompt_template)
    """
    # Dividir por la cabecera CONTEXTO:
    parts = re.split(r"\nCONTEXTO:\n", raw, maxsplit=1)
    if len(parts) != 2:
        raise ValueError("Formato de prompt inválido: no se encontró cabecera 'CONTEXTO:'")

    system_part = parts[0]
    user_part = parts[1]

    # Remover la cabecera "SYSTEM:" si existe
    if system_part.startswith("SYSTEM:\n"):
        system_prompt = system_part[len("SYSTEM:\n"):].strip()
    else:
        system_prompt = system_part.strip()

    user_template = user_part.strip()

    return system_prompt, user_template


def build_generation_prompt(
    contexto: str,
    perfil: str,
    formato: str,
    nicho: str,
    nivel: str = "estandar",
) -> tuple[str, str]:
    """Construye el prompt completo para generación.

    Carga `generacion_v1.txt`, parsea system/user, rellena las variables y
    devuelve (system_prompt, user_prompt).

    Variables disponibles en el template:
        {contexto}, {perfil}, {formato}, {nicho}, {nivel}
    """
    raw = load_prompt("generacion_v1.txt")
    system_prompt, user_template = parse_generation_prompt(raw)

    user_prompt = user_template.format(
        contexto=contexto,
        perfil=perfil,
        formato=formato,
        nicho=nicho,
        nivel=nivel,
    )

    return system_prompt, user_prompt


def strip_markdown_fences(text: str) -> str:
    """Remueve encuadramientos ```json ... ``` o ``` ... ``` devueltos por LLMs."""
    text = text.strip()
    if text.startswith("```"):
        # Remover ```json o ``` al inicio
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        # Remover ``` al final
        text = re.sub(r"\s*```$", "", text)
    return text.strip()