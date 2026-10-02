"""Catálogo declarativo de opciones de adaptación según la propuesta ONE G10."""
from typing import Literal

PerfilDestinatario = Literal[
    "Principiante / Transición de Carrera",
    "Desarrollador Junior / Semi Senior",
    "Líder Técnico / Arquitecto",
    "Gestor / Ejecutivo (No Técnico)",
]

FormatoSalida = Literal[
    "Guía Práctica Paso a Paso (Tutorial)",
    "Flashcards de Memorización",
    "Quiz Interactivo con Justificaciones",
    "Resumen Ejecutivo (TL;DR)",
    "Guion de Clase / Video",
]

NichoSector = Literal["Fintech", "Salud", "E-commerce", "General"]

PERFILES_MVP: list[PerfilDestinatario] = [
    "Principiante / Transición de Carrera",
    "Desarrollador Junior / Semi Senior",
    "Líder Técnico / Arquitecto",
    "Gestor / Ejecutivo (No Técnico)",
]

FORMATOS_MVP: list[FormatoSalida] = [
    "Guía Práctica Paso a Paso (Tutorial)",
    "Flashcards de Memorización",
    "Quiz Interactivo con Justificaciones",
    "Resumen Ejecutivo (TL;DR)",
    "Guion de Clase / Video",
]

NICHOS_MVP: list[NichoSector] = ["Fintech", "Salud", "E-commerce", "General"]
