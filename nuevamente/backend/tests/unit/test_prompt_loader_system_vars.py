"""El prompt de generación debe recibir perfil/formato/nicho/nivel en la parte SYSTEM."""
from src.generation.prompt_loader import build_generation_prompt


def test_system_recibe_las_variables_y_desescapa_las_llaves():
    system, user = build_generation_prompt(
        "TEXTO {x}", "Líder Técnico / Arquitecto", "Quiz Interactivo con Justificaciones", "Fintech"
    )
    assert "FORMATO: Quiz Interactivo con Justificaciones" in system
    assert "PERFIL: Líder Técnico / Arquitecto" in system
    assert "{formato}" not in system and "{perfil}" not in system
    assert "{{" not in system and "}}" not in system  # las llaves del JSON quedan sueltas
    assert "TEXTO {x}" in user  # el contexto no se reinterpreta
