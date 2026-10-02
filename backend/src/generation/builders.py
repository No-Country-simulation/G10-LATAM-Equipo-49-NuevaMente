"""Builders pedagógicos por formato (GEN-002, GEN-006/GEN-007).

Portados de la demo base de Fase 1 (`backend/main.py`) y tipados contra
`output.schema.ItemContenido`. Cada builder recibe una lista de fragmentos
de la fuente y el perfil, y emite items del formato correspondiente.
"""
from collections.abc import Callable

from src.output.schema import (
    ItemContenido,
    ItemFlashcard,
    ItemGuion,
    ItemQuiz,
    ItemResumen,
    ItemTutorial,
)

# Campos que llevan contenido anclado a la fuente (las palabras de plantilla no cuentan)
CAMPOS_CONTENIDO = {"dorso", "instrucciones", "detalle", "narracion", "respuesta_correcta"}


def _frase(c: str) -> str:
    return c.split(".")[0].strip()


def build_flashcards(f: list[str], perfil: str) -> list[ItemFlashcard]:
    return [
        ItemFlashcard(
            frente=f"¿Qué dice el documento sobre: {_frase(c)[:70]}...?",
            dorso=c[:280],
            pista_didactica=f"Repasa el fragmento {i + 1} de la fuente.",
        )
        for i, c in enumerate(f[:3])
    ]


def build_quiz(f: list[str], perfil: str) -> list[ItemQuiz]:
    items: list[ItemQuiz] = []
    for i, c in enumerate(f[:2]):
        correcta = _frase(c)[:90]
        dist = [
            _frase(x)[:90]
            for j, x in enumerate(f)
            if j != i and _frase(x)[:90] != correcta
        ][:2]
        while len(dist) < 2:
            dist.append("Ninguna de las anteriores")
        items.append(
            ItemQuiz(
                pregunta=(
                    f"Según la fuente, ¿cuál afirmación es correcta sobre: "
                    f"{correcta[:50]}...?"
                ),
                opciones=[correcta] + dist,
                respuesta_correcta=correcta,
                justificacion=f"Anclada literalmente en el fragmento {i + 1} del documento.",
            )
        )
    return items


def build_tutorial(f: list[str], perfil: str) -> list[ItemTutorial]:
    return [
        ItemTutorial(
            paso=i + 1,
            titulo_paso=f"Comprende: {_frase(c)[:60]}",
            instrucciones=c[:250],
            codigo_ejemplo=None,
        )
        for i, c in enumerate(f[:3])
    ]


def build_resumen(f: list[str], perfil: str) -> list[ItemResumen]:
    return [ItemResumen(punto_clave=_frase(c)[:80], detalle=c[:200]) for c in f[:3]]


def build_guion(f: list[str], perfil: str) -> list[ItemGuion]:
    from src.generation.profiles import INTROS

    intro = INTROS.get(perfil, "Introducción.")
    return [
        ItemGuion(seccion=f"Escena {i + 1}", narracion=f"{intro} {c[:200]}",
                  apoyo_visual="Resaltar el fragmento en pantalla")
        for i, c in enumerate(f[:3])
    ]


BUILDERS: dict[str, Callable[[list[str], str], list[ItemContenido]]] = {
    "flashcards": build_flashcards,
    "quiz": build_quiz,
    "tutorial": build_tutorial,
    "resumen_ejecutivo": build_resumen,
    "guion": build_guion,
}


def items_a_texto(items: list[ItemContenido]) -> str:
    """Serializa solo los campos anclados a la fuente (para anclaje_score)."""
    partes = [
        str(v)
        for it in items
        for k, v in it.model_dump().items()
        if k in CAMPOS_CONTENIDO and isinstance(v, str)
    ]
    return " ".join(partes)


def fragmentos_de_contexto(contexto: str) -> list[str]:
    """Divide el contexto ensamblado por `rag.context_builder` en
    fragmentos limpiados de la anotación `[chunk_id (p.N)]`."""
    import re

    frags: list[str] = []
    for bloque in contexto.split("\n\n"):
        limpio = re.sub(r"^\[[^\]]*\]\s*", "", bloque).strip()
        if limpio:
            frags.append(limpio)
    return frags


def build_contexto_items(contexto: str, formato: str, perfil: str) -> list[ItemContenido]:
    """Aplica el builder del `formato` sobre los fragmentos extraídos del
    contexto. Desconocido → flashcard (fallback determinista)."""
    builder = BUILDERS.get(formato, build_flashcards)
    return builder(fragmentos_de_contexto(contexto), perfil)


# Eco para el modo LLM mock (usado por orchestrator cuando no hay items)
class ECHO:
    def __init__(self, contexto: str, provider):
        self.contexto = contexto
        self.provider = provider

    def __call__(self, *_: object) -> str:
        from src.core.config import get_settings

        if get_settings().LLM_PROVIDER == "mock":
            return self.contexto[:400]
        return self.provider.generate(self.contexto)