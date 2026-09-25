from src.generation.models import GeneratedContent


def build_observations(content: GeneratedContent) -> list[str]:
    observations = []
    if not content.conceptos_clave:
        observations.append("No se identificaron conceptos clave explícitos.")
    if not content.prerrequisitos:
        observations.append("No se identificaron prerrequisitos explícitos.")
    return observations
