# Bitácora · Observatorio de actividad sísmica

Una entrada por sesión, la más reciente arriba.
Formato: qué se hizo · decisiones · problemas y solución · commits · dudas · siguiente paso.

---

## Sesión 1 · Miércoles 28/10/2026

### Qué se hizo
- Lectura completa del material: enunciado (Word = «biblia»), guía de entregables, FAQ,
  contrato de la API, validación, fuentes y código Angular de partida.
- Estudio de los repositorios de referencia de Juan:
  - `juanarrow/binance-kafka`: productor Python + aiokafka, Kafka 4.1.2 en modo KRaft,
    healthchecks y reintentos. Hecho con Spec-Driven Development (constitución, spec, plan, tareas).
  - `juanarrow/BigData-notebooks`: sesiones 1–8 (las que consolida este proyecto) y
    `Solucion_modelado_dimensional_ecommerce.ipynb`.
- Organización de la carpeta del proyecto (ver README).
- Creación de roadmap, bitácora y prompt principal.

### Decisiones
| Decisión | Motivo |
|---|---|
| Trabajo individual | Indicado por Daniel (de momento) |
| Memoria en Markdown (`docs/memoria.md`) | Preferencia de Daniel; la guía lo permite |
| Spec y plan escritos a mano en Markdown, sin Spec Kit | Entender cada parte del método SDD paso a paso |
| Material del profesor en `docs/material-profesor/`, sin modificar | Poder demostrar qué es reutilizado y qué es propio (guía §1.1) |
| Primer commit solo con el material del profesor | El historial de Git prueba qué venía hecho |
| Ejemplos renombrados: `feed-all_day-2026-10-28.geojson`, `historico-2025-01-mag4.geojson` | Nombres descriptivos; fecha sacada de `metadata.generated` |

### Problemas y solución
- **Tablas del Word que parecían cortadas:** se leyeron con `python-docx`. Las 5 tablas están
  completas y son idénticas a las de `ENUNCIADO.md`. Solo era la visualización de Word.
- **FAQ duplicada:** `FAQ-observatorio-sismico .md` era idéntica a `FAQ-ALUMNADO.md` → borrada.
- **Archivos ocultos:** solo había `frontend/.gitignore`, que sigue en su sitio. La huella SHA-256 de
  `paises.geojson` coincide con la de `FUENTES-Y-LICENCIAS.md` → catálogo íntegro.
- **Carpeta renombrada** a `proyecto-observatorio-sismico` (nombre elegido por Daniel, igual que el repo).
- **Avisos `LF will be replaced by CRLF` al hacer `git add`:** no son errores. Git en Windows convierte
  los finales de línea. Se añade `.gitattributes` con `eol=lf` para que todo quede en formato Linux,
  porque un script con CRLF puede fallar dentro de un contenedor Docker.
- **El terminal de Claude en el escritorio es un Linux aislado sin Docker:** Docker, npm y git
  se ejecutan en el Windows de Daniel (terminal de VS Code o Claude Code).

### Hallazgos en los datos (primeras observaciones, a confirmar en la Fase 1)
- Feed de ejemplo: 187 eventos; al menos 2 tienen `type = "explosion"`.
- Hay profundidades negativas (p. ej. −2,31 km y −0,54 km): no rechazar sin estudiar.
- Histórico de enero 2025 (mag ≥ 4): 1.413 eventos, muy por debajo del límite de 20.000.

### Commits
- `5c052ff` Material inicial del profesor sin modificar
- `d792b78` Organización del proyecto: README, .gitignore, roadmap, bitácora y prompt principal
- Push a https://github.com/DanielML84/proyecto-observatorio-sismico (rama `main`)

### Dudas abiertas
- Ninguna por ahora.

### Fase 1 · Mapa demo (FAQ paso 1) ✅
- `npm ci` + `npm start` en `frontend/`; el panel abre en http://localhost:4200.
- Resultado: catálogo de países cargado, 4 eventos dibujados, 0 omitidos; la ficha, el zoom y las capas funcionan.
- Evidencia: `docs/evidencias/fase1-mapa-demo.png`.
- Angular CLI preguntó si se comparten estadísticas de uso y se respondió «y». **Corrección:** sí modificó
  `frontend/angular.json` (añadió `"cli": {"analytics": "<id>"}`); la primera comprobación se hizo antes
  de que se escribiera. Se revierte para dejar el archivo del profesor intacto y se desactiva a nivel global.
- Problema: un `git status` lanzado desde el terminal de Claude dejó un `.git/index.lock` huérfano, que
  bloquearía los commits. Se borró. Solución para el futuro: Claude usa `git --no-optional-locks`.
- Qué demuestran los 4 puntos ficticios (`terremotos-demo.geojson`), y cómo dibuja el mapa:
  | id | Profundidad | Mag | País | Cómo se ve |
  |---|---|---|---|---|
  | demo-1 | 12 km | 3,2 | España | amarillo (< 70 km) |
  | demo-2 | 95 km | 5,1 | Japón | naranja (70–300 km) |
  | demo-3 | 350 km | 6,0 | Chile | morado (≥ 300 km), el más grande |
  | demo-4 | 8 km | **null** | **null** (océano) | círculo mínimo; ficha «ND» y «Sin país asignado» |

### Siguiente paso
1. Commit de la evidencia de la Fase 1.
2. Fase 1: explorar el JSON del feed (campos, tipos, unidades, opcionales).
