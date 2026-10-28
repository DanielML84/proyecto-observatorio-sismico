# Observatorio de actividad sísmica

Proyecto de Sistemas de Big Data (máster IA y Big Data, CPIFP Alan Turing).
Autor: Daniel Meléndez Loreto. Estado: **en construcción**.

Pregunta que responde: **¿dónde se está registrando actividad sísmica y cómo se
compara con un periodo histórico equivalente?**

```text
USGS → productor (Python) → Kafka → consumidor (Python) → PostgreSQL → API (FastAPI) → ngrok → panel (Angular, Netlify)
```

## Estructura del repositorio

| Ruta | Contenido | Origen |
|---|---|---|
| `frontend/` | Panel Angular + Leaflet | Material del profesor (se modificará) |
| `docs/material-profesor/` | Enunciado, FAQ, guía, contrato API y ejemplos de datos | Material del profesor, sin modificar |
| `docs/roadmap.md` | Plan de trabajo por fases | Propio |
| `docs/bitacora.md` | Diario de cada sesión | Propio |
| `docs/prompt-principal.md` | Contexto para retomar el proyecto con IA | Propio |

Las instrucciones de instalación y ejecución se completarán según avance el proyecto.
