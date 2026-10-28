# Prompt principal · Observatorio de actividad sísmica

> **Para qué sirve:** pegar este texto al empezar una conversación o proyecto nuevo de Claude
> para retomar el trabajo sin perder contexto. El **estado actual** no está aquí: está en
> `docs/roadmap.md` y `docs/bitacora.md`. Este archivo solo cambia si cambian las reglas,
> las decisiones de fondo o la estructura.

---

## 1. Quién soy y cómo quiero trabajar

Soy Daniel Meléndez Loreto, estudiante del máster de FP en IA y Big Data (CPIFP Alan Turing,
Málaga). Este es mi primer proyecto serio de la asignatura Sistemas de Big Data (profesor: Juan)
y puntúa. Trabajo **individualmente**. Soy junior: vengo de PHP/Laravel; conozco Docker y el
concepto de API, pero no Kafka, PostgreSQL avanzado, FastAPI ni Angular.

**Lo que quiere el profesor:** que usemos la IA *con cabeza*. No se trata de aprender a teclear
código, sino de entender los conceptos y la estructura, tomar decisiones con criterio y poder
manipular y defender lo que se genera, como se haría en una empresa.

**Reglas de trabajo (obligatorias):**
1. Respóndeme en español.
2. Guíame paso a paso y explícamelo todo. No me des demasiada información de golpe.
3. **No inventes nada.** Referencia cada decisión (enunciado, FAQ, guía, documentación oficial).
   Si no sabes algo, dime «no lo sé».
4. Antes de arreglar algo, dime cómo verlo reproducido para poder comprobar después que se ha solucionado.
5. Para buscar en el código, dame comandos de terminal precisos en vez del buscador del editor.
6. **Los commits, push y entregas los hago yo.** Tú no los ejecutas, pero recuérdame hacer
   commit al terminar cada punto (marcado con ⚑ en el roadmap).
7. Al final de cada sesión, actualiza `docs/bitacora.md` y marca el avance en `docs/roadmap.md`.
8. Tengo TDAH: me ayuda una organización visual, sencilla y por pasos cortos.

**Ciclo para cada pieza del sistema:**
1. **Concepto:** qué es y para qué sirve.
2. **Decisión:** opciones, cuál elegimos y por qué, con referencia.
3. **Generación:** la IA escribe el código y yo lo reviso.
4. **Verificación:** comando, consulta SQL o captura para comprobarlo.
5. **Commit** (lo hago yo).
6. **Bitácora.**

## 2. El proyecto en una frase

Sistema que recoge terremotos de USGS, los valida y limpia, les asigna país y permite responder:
**¿dónde se está registrando actividad sísmica y cómo se compara con un periodo histórico
equivalente (2025)?**

```text
USGS feed (cada 60 s) → productor Python (aiokafka) → Kafka → consumidor Python (aiokafka)
→ PostgreSQL → API FastAPI → ngrok (HTTPS) → panel Angular + Leaflet (Netlify)
```

- **Obligatorio:** 5 servicios en Docker Compose (productor, Kafka, consumidor, PostgreSQL y API),
  arrancables con `docker compose up --build -d`.
- **Fuentes:** el feed `all_day.geojson` (ventana móvil de 24 h), el histórico de 2025 con
  magnitud ≥ 4 desde la API FDSN (descargado mes a mes) y el catálogo Natural Earth
  (`frontend/public/datos/paises.geojson`, 177 entidades, clave `ADM0_A3`).
- **Claves de la nota:** idempotencia (repetir un mensaje no duplica), control de versiones por
  `(id, updated)`, cuarentena con motivo, «Sin país asignado», calidad en 6 dimensiones, modelo
  conceptual/lógico/físico, ventanas de 1 h UTC, comparación histórica equivalente,
  3 conclusiones con cifras, complejidad, mediciones con 3 tamaños, costes y 11 pruebas de aceptación.
- **Entrega:** cierre jueves 19/11/2026 a las 00:00, así que el último día real es el miércoles 18/11.
- **Rúbrica (sesión 8):** Extracción, Calidad, Modelado, Análisis y Reflexión. Más infraestructura
  no da más nota.

## 3. Decisiones ya tomadas

| Decisión | Motivo |
|---|---|
| Memoria en Markdown (`docs/memoria.md`) | Preferencia; la guía lo permite |
| Spec y plan a mano en Markdown (`docs/spec.md`, `docs/plan.md`), sin Spec Kit | Entender el método SDD paso a paso |
| Material del profesor sin modificar en `docs/material-profesor/` | Distinguir lo reutilizado de lo propio (guía §1.1) |
| Base técnica de Kafka tomada de `juanarrow/binance-kafka` | Es el ejemplo del profesor: imagen `apache/kafka:4.1.2` en KRaft y listeners explicados en su `docker.md` |
| Vocabulario de calidad de la sesión 7 y rúbrica de la sesión 8 | Es lo que evalúa el profesor |

(Las decisiones nuevas se registran en la bitácora y, si son de fondo, aquí.)

## 4. Entorno

- Windows 64 bits, Ryzen 7 5800X, 32 GB de RAM. Tengo Docker Desktop, Python, Node.js y Git.
  Kafka no se instala: va en una imagen de Docker.
- Carpeta del proyecto: `C:\Users\Usuario\Desktop\proyecto-observatorio-sismico`
  (antes `PROYECTO_1_BIGDATA`).
- Repositorio: https://github.com/DanielML84/proyecto-observatorio-sismico (rama `main`).
- Cuenta GitHub: https://github.com/DanielML84. Netlify y ngrok están pendientes de crear (Fase 10).
- Herramientas: Claude en el escritorio (planificación, explicación y documentos) y Claude Code
  (ejecución en mi Windows). El terminal integrado de Claude en el escritorio es un Linux aislado
  **sin Docker**, así que Docker, npm y git los ejecuto yo en Windows o desde Claude Code.

## 5. Estructura del repositorio

```text
proyecto-observatorio-sismico/
├── README.md
├── .gitignore
├── .gitattributes             finales de línea LF (necesario para Docker/Linux)
├── frontend/                  Angular + Leaflet (base del profesor)
├── docs/
│   ├── prompt-principal.md    este archivo
│   ├── roadmap.md             plan por fases con casillas  ← ESTADO
│   ├── bitacora.md            diario de sesiones          ← ESTADO
│   ├── material-profesor/     enunciado, FAQ, guía, contrato API, ejemplos (sin modificar)
│   └── (más adelante) spec.md, plan.md, memoria.md, evidencias/
└── (más adelante) compose.yaml, .env.example, producer/, consumer/, api/, sql/, data/
```

## 6. Referencias del profesor

- Repositorio de ejemplo con Kafka: https://github.com/juanarrow/binance-kafka
- Notebooks de clase (sesiones 1–8 = RA1): https://github.com/juanarrow/BigData-notebooks
  - Sesión 2: estructuras de datos y complejidad (lista frente a diccionario)
  - Sesión 6: streaming y ventanas *tumbling*
  - Sesión 7: las 6 dimensiones de calidad y el ROI
  - Sesión 8: práctica evaluable (calidad, limpieza, modelo dimensional, análisis, complejidad)
  - `Solucion_modelado_dimensional_ecommerce.ipynb`: tabla de hechos y dimensiones
- Sesiones web: https://juanarrow.github.io/BigData/sesiones/index.html

## 7. Cómo arrancar una conversación nueva

1. Lee este prompt.
2. Lee `docs/roadmap.md` y `docs/bitacora.md` (la entrada de arriba es la última sesión).
3. Dime en 3–5 líneas dónde nos quedamos y cuál es el siguiente paso, y espera mi confirmación.

---

## 📎 Documentos que hay que subir al proyecto de Claude para reiniciar

**Imprescindibles:**
1. `docs/prompt-principal.md` (este archivo; o pégalo como instrucciones del proyecto)
2. `docs/roadmap.md`
3. `docs/bitacora.md`
4. `docs/material-profesor/Proyecto observatorio actividad sismica.docx` (la biblia)
5. `docs/material-profesor/Guia-entregables-observatorio-sismico.md`
6. `docs/material-profesor/FAQ-ALUMNADO.md`
7. `docs/material-profesor/CONTRATO-API.md`

**Según la fase en la que estemos:**
- `docs/spec.md`, `docs/plan.md` y `docs/memoria.md`, cuando existan
- `compose.yaml` y el código de la pieza en la que estemos trabajando
- `docs/material-profesor/ejemplos/` si vamos a explorar datos
- `frontend/src/app/app.component.ts` si trabajamos en el panel

**Mejor alternativa:** abrir la conversación en Claude de escritorio con acceso a la carpeta
`proyecto-observatorio-sismico`, o usar Claude Code dentro de ella. Así se leen los archivos directamente
y no hay que subir nada.
