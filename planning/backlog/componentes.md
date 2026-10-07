# Componentes

## Diagrama
```mermaid
graph TD
    COMP_01["COMP-01<br/>Ingestion Service"]
    COMP_02["COMP-02<br/>Processing Service"]
    COMP_03["COMP-03<br/>Embedding Service"]
    COMP_04["COMP-04<br/>Vector Store"]
    COMP_05["COMP-05<br/>RAG / Retrieval Service"]
    COMP_06["COMP-06<br/>Generation Service"]
    COMP_07["COMP-07<br/>Validation Service"]
    COMP_08["COMP-08<br/>Output Service"]
    COMP_09["COMP-09<br/>Storage Service"]
    COMP_10["COMP-10<br/>Interfaz web"]
    COMP_11["COMP-11<br/>API pública"]
    COMP_01 --> COMP_09
    COMP_02 --> COMP_01
    COMP_03 --> COMP_02
    COMP_04 --> COMP_03
    COMP_05 --> COMP_03
    COMP_05 --> COMP_04
    COMP_06 --> COMP_05
    COMP_07 --> COMP_06
    COMP_08 --> COMP_06
    COMP_08 --> COMP_07
    COMP_10 --> COMP_11
    COMP_11 --> COMP_01
    COMP_11 --> COMP_05
    COMP_11 --> COMP_06
    COMP_11 --> COMP_07
    COMP_11 --> COMP_08
    COMP_11 --> COMP_09
```

## Detalle
| ID | Nombre | Tipo | Tecnología | Responsabilidad |
|---|---|---|---|---|
| `COMP-01` | Ingestion Service | Backend | Python, PyPDF, parsers MD/TXT | Recibir archivo, detectar tipo, extraer texto, normalizar y validar tamaño/formato |
| `COMP-02` | Processing Service | Backend | LangChain RecursiveCharacterTextSplitter | Limpieza de texto y chunking con metadata de posición/sección |
| `COMP-03` | Embedding Service | Backend / IA | EmbeddingProvider + Gemini (pendiente) + mock | Generar vectores para cada chunk vía proveedor configurable |
| `COMP-04` | Vector Store | Persistencia | ChromaDB embebido | Persistir embeddings + metadata y realizar búsqueda semántica |
| `COMP-05` | RAG / Retrieval Service | Backend | Python | Construir query desde perfil/nicho, recuperar top-k y ensamblar contexto |
| `COMP-06` | Generation Service | Backend / IA | LLMProvider + Gemini (pendiente) | Adaptar contenido por perfil/formato/nicho/nivel de detalle |
| `COMP-07` | Validation Service | Backend / IA | LLM juez + agregación determinista | Extraer claims, contrastarlos con la fuente y calcular score de fidelidad |
| `COMP-08` | Output Service | Backend | Pydantic v2 | Ensamblar el JSON final según schema formal (NuevaMenteOutput) |
| `COMP-09` | Storage Service | Cloud | OCI SDK (Object Storage Always Free) | Upload/download de originales y resultados, naming y verificación |
| `COMP-10` | Interfaz web | Frontend | Streamlit | Permitir a un usuario no técnico ejecutar todo el flujo |
| `COMP-11` | API pública | Backend | FastAPI + Pydantic | Exponer el monolito vía REST y orquestar COMP-01..COMP-09 |
