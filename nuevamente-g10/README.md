# NuevaMente 🧠

> Sistema Inteligente de Adaptación y Generación de Contenido Educativo  
> Hackathon ONE · Grupo 10 · NoCountry × Oracle Cloud Infrastructure

## 🎯 Problema

La documentación técnica es densa y única para todas las audiencias. NuevaMente la convierte automáticamente en contenido educativo personalizado según el perfil del destinatario.

## 🏗️ Arquitectura
┌──────────────┐ webhook ┌─────────────┐
│ Streamlit │ ───────────────► │ n8n │
└────────────── └──────┬──────┘
│
┌──────────▼──────────┐
│ FastAPI + RAG │
└──────┬─────────┬────┘
│ │
┌──────▼───┐ ┌──▼────────┐
│ ChromaDB │ │ OCI Store │
──────────┘ └───────────┘

## 🚀 Instalación

```bash
git clone https://github.com/NoCountry-simulation/G10-LATAM-Equipo-49-NuevaMente.git
cd G10-LATAM-Equipo-49-NuevaMente/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
##  Documentación

- [Arquitectura del sistema](docs/arquitectura.md)
- [Contrato de la API](docs/contrato-api.md)
- [Glosario técnico](docs/glosario.md)
- [Manual completo (Google Docs)](PEGAR_LINK_AQUI)

## 👥 Equipo

| Rol | Integrante |
|-----|------------|
| Orquestación / Backend | Rodrigo Reyes |
| Cloud Developer | Pedro Orozco |
| Backend Developers | Miguel, Fernando, Osvaldo |
| UX/UI Designer | Viviana Hurtado |
| QA / Testing | Eduardo C |
| Scrum Lead | Diana |

## 📋 Estado del Proyecto

- ✅ **Fase 1:** Backend demo + contrato Pydantic + n8n operativo
- ⏳ **Fase 2:** RAG real (Gemini + ChromaDB) + OCI Storage
- ⏳ **Fase 3:** Interfaz Streamlit
- ⏳ **Fase 4:** Despliegue en OCI Always Free

## 🏆 Requisitos del Hackathon

| Requisito | Estado |
|-----------|--------|
| Ingesta PDF/MD/TXT | ⏳ Fase 2 |
| RAG + Vector Store | ⏳ Fase 2 |
| Adaptación por perfil/formato |  Fase 2 |
| Control de fidelidad (anti-alucinación) | ✅ Operativo |
| JSON estructurado (Pydantic) | ✅ Operativo |
| OCI Object Storage | ⏳ Fase 2 |
| 3 escenarios de demo |  Fase 2 |
