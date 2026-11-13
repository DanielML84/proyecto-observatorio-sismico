# Bitácora · Observatorio de actividad sísmica

Una entrada por sesión, la más reciente arriba.
Formato: qué se hizo · decisiones · problemas y solución · commits · dudas · siguiente paso.

---

## Sesión 16 · Viernes 13/11/2026 (tarde)

### Avanzado
- La conexión con el ordenador de Daniel falló (error de la sesión, no del proyecto). Solución: Claude descargó el
  repositorio de GitHub (último commit `114fcac`, 11/11), hizo los cambios en esa copia y se los pasa a Daniel para que
  sustituya los archivos en su carpeta.
- `docs/defensa.md`: respuestas modelo de las dos obligatorias y de las fases 1–4 (preparadas el 12/11). Las de los campos
  `ids`, `time` y `updated` se apoyan en la definición de campos de USGS (copia archivada de 2016; la página actual no se pudo abrir).
- Fecha de entrega corregida a **20/11** en `CLAUDE.md`, `prompt-principal.md`, `roadmap.md` y `guia-estudio.md`.
- README, «Cómo se cumple la rúbrica»: columna «Sobresaliente (9–10) pide» en la tabla resumen y, al principio de cada
  criterio, lo que pide el nivel más alto con dónde está la evidencia (en el orden de la rúbrica, enunciado §13).
  Comprobado que la tabla de calidad ya tenía la acción de cada dimensión.
- README, Reflexión: añadidas **limitaciones** y **mejoras propuestas** (el enunciado las pide para ese criterio y no
  estaban en el README; todas salen de la memoria, con su apartado).

### Pendiente de comprobar
- ⚠️ Que el repositorio sea accesible sin iniciar sesión (incógnito): Claude pudo descargarlo, pero desde su entorno no
  se puede asegurar que sea sin credenciales.

### Siguiente paso
1. Daniel copia los 7 archivos actualizados a su carpeta, revisa los cambios (`git diff`) y hace commit.
2. Ensayar con el guion de 5 min y grabar (semana del 16/11).
3. Vie 20/11: subir a YouTube («No listado»), enlace en el README, commit y entregar.

## Sesión 15 · Jueves 12/11/2026 (mediodía, sin el ordenador conectado)

### Cambio anunciado por el profesor (dato de Daniel)
- El vídeo **no necesita más de 5 min**: basta con ir indicando dónde se cumple la rúbrica, de principio a fin.
- Hay que **demostrar con evidencias el nivel más alto de cada criterio**, en el orden de la rúbrica; se puede hacer todo
  desde el README («leer código es aburrido»).
- La entrega es el **viernes 20/11** (Claude había entendido mal que era el 13/11).

### Avanzado
- Nuevo documento «Guion 5 minutos · Observatorio sísmico» (Claude Docs): 7 escenas siguiendo el README en el orden de
  la rúbrica; en cada criterio se dice lo que pide el sobresaliente y dónde está la evidencia. Los guiones largos se quedan como consulta.
- `docs/defensa.md`: las fases 1–4 y las dos obligatorias estaban vacías **a propósito** (las iba a escribir Daniel).
  Decisión de Daniel: que Claude escriba respuestas modelo. Guardadas en el proyecto de Claude (`claude/defensa-respuestas.md`).

### Problemas
- El ordenador no estaba conectado → no se pudo tocar la carpeta local; se dejó todo para la sesión siguiente.

## Sesión 14 · Miércoles 11/11/2026 (tarde)

### Avanzado
- Prueba «desde un entorno limpio»: a Daniel le preocupaba estropear algo → **decisión de Daniel: no arrancar una copia
  limpia**. En su lugar, Claude comprobó solo leyendo que Git contiene todo lo necesario para el arranque: rama `main`
  al día con `origin/main`; compose, `.env.example`, Dockerfile, requirements, SQL, 16/16 `.py` y 28/28 archivos de
  `frontend/src` en Git. Ignorados: `.env` (secreto), `.claude/`, `.vscode/` y `data/tmp/frontend.tgz` (01/11, no lo usa el código).
- Limitación declarada en `docs/revision-enunciado.md` (#7): no se ha ejecutado el arranque desde cero.
- Guion del vídeo: Daniel lo revisa y lo edita (sobre todo la escena 5); se añaden indicaciones [▶ …] de dónde ir en cada momento.
- Nuevo documento aparte **«Guion narrado · Observatorio sísmico»** (Claude Docs), a petición de Daniel: misma estructura de 11 escenas,
  con **Pantalla** (qué abrir) y subsecciones numeradas (1.1, 1.2…) con texto en primera persona que describe lo que se ve, para
  grabar primero la voz y después la imagen. Cifras de las escenas 8–11 comprobadas contra el README y la memoria §7bis.
- ⚠️ Escena 10: las cifras de ejemplo (19 frente a 351, −94,6 %) son las de la memoria; en el panel de hoy pueden salir otras.
  Comprobar antes de grabar que el aviso «Recuento incompleto» sigue apareciendo con 24/10–01/11.

### Siguiente paso
1. Commit de los cambios pendientes (README, bitácora, roadmap, revision-enunciado).
2. Ensayar con el guion narrado, comprobar en el panel los datos de reproducción y grabar.
3. Viernes 13/11: subir a YouTube («No listado»), añadir el enlace al README, commit y entregar.

## Sesión 13 · Lunes 09/11/2026 (tarde) · Cambio de entrega

### Cambio anunciado en clase (dato de Daniel)
- Entrega **adelantada al viernes 13/11**. **Sin defensa en clase**: vídeo en YouTube (sin duración fijada) explicando el
  programa y cómo se cumple la rúbrica; Daniel prefiere grabarlo navegando por los archivos y leyendo un guion.
- El README es lo que va a leer el profesor: técnico y completo, con las **fotos dentro del repositorio** y con el
  **ciclo de desarrollo con IA** (Proyecto de Claude con archivos de contexto + Claude Code).
- Se valoraría un toque personal en el panel. **Decisión de Daniel:** sin cambios en el panel (ni siquiera de color):
  habría que recompilar y republicar, y las 19 capturas dejarían de coincidir con lo publicado.

### Avanzado
- Comprobado: las 19 capturas `.png` están en Git; el README no mostraba ninguna.
- README ampliado: índice, vista del panel (2 imágenes), **cómo se cumple la rúbrica** (5 criterios → evidencias),
  **las 3 conclusiones**, **pruebas de aceptación** (2 imágenes), **ciclo de desarrollo con IA** (herramientas, reglas,
  ciclo por pieza, fases, errores de la IA detectados y decisiones del alumno). Imágenes y enlaces verificados (0 rotos).
- La sección «Activar el sistema» pasa a llamarse «para la demostración». `CLAUDE.md` actualizado con la nueva entrega.
- Capturas existentes revisadas: sirven de apoyo pero no tienen los filtros exactos de cada conclusión → Daniel hace 4
  capturas nuevas (`conclusion1-2025-ventanas.png`, `conclusion2-pais-sin-filtro.png`, `conclusion2-pais-m4.png`,
  `conclusion3-comparacion.png`).
- Guía y roadmap replanificados: lun README + capturas · mar guion + entorno limpio · mié grabación · vie entrega.

### Visita guiada al panel + capturas de las conclusiones
- Recorrido: estado del sistema (último acceso, respuesta generada y última ingesta: «respuesta reciente ≠ datos
  recientes»), filtros, mapa (tamaño = magnitud, color = profundidad, ficha) y estadísticas.
- Problema: el campo de fecha conserva la hora actual (16:26) si no se cambia → 18.258 en vez de 18.302 y aviso de
  «Recuento incompleto». Solución: poner la hora `00:00` a mano. Daniel envía las capturas por el chat y Claude las guarda.
- Cifras de las capturas (09/11) frente a la memoria:
  - C1 (2025, M ≥ 4): 18.302 ✅; máximo horario 30/07/2025 01:00 UTC, 49 terremotos.
  - C2 (30/10–01/11): sin filtro 608 (memoria 550), EE. UU. 75,0 % (75,1 %); con M ≥ 4 71 (61), EE. UU. 2 = 2,8 % (3,3 %).
    Suben los totales por los terremotos de la noche del 01/11, que llegaron después; la conclusión se mantiene.
  - C3 (30/10 09:28 → 31/10 09:28, M ≥ 4): 27 (= base del 03/11), −46,2 %, 5,5 % de los días de 2025 con ≤ 27.
- Capturas enlazadas en el README y en la memoria §7 con sus filtros y la explicación de las diferencias.
  Revisión del enunciado: **103 ✅ · 0 ⚠️ · 0 ❌ · 1 ⏳** (+ 2 ❓: entorno limpio y acceso al repositorio).

### Guion y README autosuficiente
- Guion del vídeo creado como documento de Claude (11 escenas: preparación, 5 criterios de la rúbrica, demostración en
  directo de la reproducción, reflexión, ciclo con IA, decisión propia D32/D39 y cierre).
- Petición de Daniel: el README no debe obligar al profesor a buscar por el proyecto → las secciones «Cómo se cumple la
  rúbrica» y «Pruebas de aceptación» incluyen ahora la explicación y los **resultados reales** (código, logs, salidas
  SQL, tablas de mediciones, LAG); los enlaces quedan solo como detalle. Imágenes y enlaces verificados (0 rotos).

### Siguiente paso
- Martes 10/11: prueba desde un entorno limpio; Daniel lee el guion y pregunta lo que no entienda.

## Sesión 12 · Domingo 08/11/2026 (mañana) · Colchón + revisión del enunciado

### Repaso de los ⚠️ de los bloques 1–5 (7 preguntas, sin mirar)
- ✅ Contar filas: 4 terremotos (1+2+3+1 versiones) + repetición → 4 y 7. **Resuelto** (era lo prioritario).
- ✅ Excluido / inválido / guardado: 4/4 (quarry blast, lon 200, mag nula, mag «cinco»). **Resuelto.**
- ✅ Quién guarda qué (Kafka 7 días) y LAG alto con el consumidor parado · ✅ la API lee PostgreSQL; `exec` para Kafka.
- ⚠️ «¿Ha quedado hueco?»: atribuyó la línea del productor a Kafka; la resta eventos − publicados (0 = sin solape) la aplica bien.
- ❌ Latido: pensó que seguiría `healthy` → sin líneas nuevas en el log = sin ciclos = `unhealthy`. **Repasar el 15/11.**
- ❌ Libreta: dijo `id` + `time` y «original y copia» → `id` + `updated`; RAM (`publicadas`) + PostgreSQL (`version_publicada`). **Repasar el 15/11.**

### Revisión del enunciado (`docs/revision-enunciado.md`) → 102 ✅ · 1 ⚠️ · 0 ❌ · 1 ⏳
- Daniel decide: Claude aplica las correcciones; él lo estudiará después.
- Hueco 1 ❌ → ✅: memoria §5.2bis, párrafo «Limitación: lo que sale de la ventana no se reconcilia». Comprobado antes que el
  código no tiene `DELETE` sobre datos reales (solo el esquema `bench` y el `TRUNCATE` manual de `replay`).
- Hueco 4 ⚠️ → ✅: memoria §4, índice de dónde está cada aspecto de la fuente reciente (enunciado §4.1).
- Hueco 3 ⚠️ → ✅ (documentado): `docker compose exec tunel ngrok version` falla con `openat etc/passwd: path escapes from
  parent` (causa: no lo sé). Con `docker image inspect`: huella `sha256:ff3b5c36…993ef`, sin etiqueta de versión, fecha
  1970 (imagen hecha con Nix). **Decisión de Daniel: documentar, no fijar** (menos cambios). README §1 y memoria D43.
- Roadmap: tareas de la Fase 1 ya hechas marcadas; `spec.md` y `plan.md` descartados (no los pide el enunciado).
- Pendiente: hueco 2 (capturas de los filtros de cada conclusión) → visita al panel del 09/11.

### Guía de entregables y FAQ (revisadas enteras a petición de Daniel)
- `ENUNCIADO.md` = Word (98 % de coincidencia palabra a palabra; solo añade un párrafo de contexto sin requisitos).
- Guía §3.2: faltaba un procedimiento breve para la defensa → **añadida** la sección «Activar el sistema para la defensa»
  al principio del README.
- FAQ: todo cubierto. `contrato-mensaje.md` aún decía que la carga del histórico «se decidirá» → actualizado (D29, por Kafka).
- **Sin comprobar (❓):** arrancar desde un entorno limpio (nunca probado → bloque 10, 14/11) y acceso al repositorio
  (Daniel, en incógnito). Detalle en `docs/revision-enunciado.md`.
- `docs/chuleta-comandos.md`: nuevo apartado «⭐ Uso diario» (arrancar, comprobar, ver hueco, parar, con túnel), y el
  comando del LAG.

### Siguiente paso
- Lunes 09/11: visita guiada al panel + capturas de las 3 conclusiones (hueco 2) + bloque 6.
- Sábado 14/11: prueba desde un entorno limpio (con Claude) además del bloque 10.

## Sesión 11 · Sábado 07/11/2026 (mañana) · Estudio: bloque 5 ✅

### Avanzado
- Arranque 10:28: `eventos=179 publicados=66`; 113 ya publicados → solapamiento, **sin hueco**. Estado cargado: 1798.
- **Bloque 5 · PostgreSQL**, en 6 pasos: (1) grano de las 7 tablas; hecho `evento_actual`, dimensiones `pais` y `fecha`
  · (2) contar en `evento_actual` (en `evento_version` un terremoto con 33 versiones contaría 33 veces; enunciado §8)
  · (3) claves: PK `event_id`, PK compuesta `(event_id, updated_ms)`, UNIQUE de cuarentena; la clave no compara fechas
  · (4) UPSERT con `WHERE evento_actual.updated_ms < EXCLUDED.updated_ms` · (5) transacción (o todo o nada) + offset
  después · `country_id` NULL = «Sin país asignado» (14 465, 76,7 %) · (6) los 8 casos de la FAQ 12: 5/8 acertados.

### ⚠️ Para repasar (prioritario el domingo)
- **Contar filas de `evento_version`**: falló 3 veces (1 fila por versión distinta que entra; los `ignorado` no añaden).
  Acabó acertando 5 terremotos × 2 versiones = 5/10 y la revisión de E2 = 3/5.
- Casos de calidad de la FAQ 12: magnitud nula → `insertado` (no cuarentena); latitud 145 → `cuarentena` (inválido,
  no excluido: **segunda vez**); explosión → `excluido` (no `ignorado`, que es solo para versiones repetidas o viejas).
- Decía «la clave compara la fecha» → la clave solo impide repetir; compara el `WHERE` del UPSERT.

### Problemas
- `docker compose --profile tunel up -d` se quedó sin devolver el control de la terminal, aunque los 8 contenedores
  arrancaron bien (`ps -a`). Causa: **no lo sé**. Solución: Ctrl + C (no para los contenedores).

### Siguiente paso
- Domingo 08/11: colchón (⚠️ de los bloques 1–5, sobre todo el recuento de versiones y excluido/inválido) + revisión de
  `docs/revision-enunciado.md`.

## Sesión 10 · Jueves 05/11/2026 (tarde)

### Avanzado
- Arranque a las ~20:00 tras ~21 h 50 min parado (< 24 h): `eventos=208 publicados=194`; los 14 restantes ya estaban
  publicados → la ventana se solapa con lo recogido, **sin hueco**. Estado cargado: 1317 versiones.
- **Revisión del enunciado punto por punto** preparada por Claude: `docs/revision-enunciado.md`. 104 requisitos del Word
  (revisión 2) cruzados con código, memoria y evidencias: **99 ✅ · 3 ⚠️ · 1 ❌ · 1 ⏳**.
  - ❌ §5: falta documentar la limitación de eventos eliminados/fusionados/revisados fuera del feed.
  - ⚠️ §12: las conclusiones no enlazan capturas del panel con sus filtros (encaja con la visita al panel del 09/11).
  - ⚠️ §9: `ngrok/ngrok:latest` sin versión fija (el resto de dependencias sí lo está).
  - ⚠️ §4.1: documentación de la fuente reciente completa pero repartida en varias secciones.
  - ⏳ §12: explicación individual (semana de estudio).

### Siguiente paso
- Domingo 08/11: revisar `docs/revision-enunciado.md` con Daniel y decidir cómo resolver cada hueco.
- Daniel: bloque 5 (viernes o sábado).

## Sesión 9 · Miércoles 04/11/2026 (tarde) · Estudio: bloques 3 y 4 ✅

### Avanzado
- Arranque tras ~19 h 40 min parado (< 24 h): primera consulta `eventos=169 publicados=131`, después 1 y 0. Estado
  cargado: 1119 versiones. Los 38 restantes ya estaban en `version_publicada` (ocurridos ayer con el sistema encendido).
- Detalle visto en el log: una consulta con `publicados=0` guardó copia porque salieron terremotos del tablón (169 → 167)
  y cambió la huella de `features`.
- **Bloque 3 · Kafka**, en 6 pasos con la cocina: (1) topic = barra, partición = gancho; 3 particiones (D14) para
  repartir entre varios consumidores; orden solo dentro de cada partición · (2) clave = `id` → mismo gancho → versiones
  en orden (con la magnitud como clave, la vieja podría pisar a la buena) · (3) offset = número de comanda por gancho;
  identificar un mensaje = topic + partición + offset (UNIQUE de `cuarentena`) · (4) grupo de consumidores y offset
  confirmado (marcapáginas), confirmar después de guardar = «al menos una vez» · (5) LAG = LOG-END − CURRENT ·
  (6) Kafka sin publicar (PLAINTEXT, sin contraseña ni cifrado; enunciado §2 y §9).
- Práctica real: `kafka-consumer-groups.sh --describe --group consumidor-observatorio` → LAG 0 en las 3 particiones
  (offsets 12 738 / 12 947 / 12 832; 38 517 mensajes en total, histórico 2025 incluido). Un solo CONSUMER-ID para las 3.

### ⚠️ Para repasar
- Pensaba que en la recuperación «se borraron» 38 del tablón → no: eran los que ya estaban en la libreta.
- Leyó los ~12 000 offsets como pendientes y CONSUMER-ID como el DNI de un terremoto → offset = posición;
  pendientes = LAG; CONSUMER-ID = el consumidor (uno para las 3 particiones).
- Dijo que con el consumidor parado «el LAG no aumenta» → sí aumenta: es la resta LOG-END − CURRENT.
- Pensaba que el comando del LAG llega a Kafka «por la API» → `docker compose exec` ejecuta dentro del contenedor;
  **la API nunca habla con Kafka** (solo lee PostgreSQL).
- Defensa: decir el caso concreto («la versión vieja pisaría a la buena»), no «se complicaría».

### Problemas
- Al volver, el enlace con el PC estaba cortado (app de escritorio cerrada). Solución: abrir la conversación en la app.
- Arranque con `docker compose up -d` sin `--profile tunel`: el túnel no arrancó. Corregido con `--profile tunel up -d`.

### Bloque 4 · Consumidor, validación y cuarentena ✅ (misma tarde, 20:31–21:47)
- Pasos: (1) qué hace el consumidor con cada mensaje (validar → guardar o cuarentena → transacción → offset), con el log
  real (`nc75462502`: insertado + 3 actualizado seguidos) · (2) salidas: insertado, actualizado, ignorado, excluido,
  cuarentena; `excluido` e `invalido` en la misma tabla con tipo distinto · (3) las 15 reglas de `validacion.py`
  (`f"type={tipo_evento}"`, `geometria_no_point`; sin `id` no se controlan duplicados) · (4) profundidad negativa
  (geoide WGS84, D3) y magnitud nula (NULL ≠ 0) · (5) `MODO_ESPERADO` como segunda barrera · (6) SQL de cuarentena.
- Resultado real (04/11): excluido `type=explosion` 12 (1 de prueba) · `type=quarry blast` 12 · invalido
  `lat_fuera_de_rango` 1 (`PRUEBA-LAT145`). **0 inválidos reales de USGS.**

### ⚠️ Para repasar (bloque 4)
- Atribuyó las explosiones a volcanes → son provocadas por personas (voladuras, canteras); excluidas porque no son `earthquake`.
- Latitud 145: dijo «excluido por ser erróneo» → erróneo = **inválido**. Excluido = «no es de mi carta».
- Pensaba que la magnitud 0 «no sería un terremoto» → M0 y negativas existen (7 en la base); por eso NULL no se rellena con 0.
- Respuestas aún genéricas («no se puede comprobar», «por si entrara») → dar el caso concreto.

### Decisiones (Daniel, 04/11)
- **Revisión exhaustiva del enunciado punto por punto** (requisito → dónde se cumple → evidencia): la prepara Claude; se revisa
  el domingo 08/11. Motivo: si aparece un hueco, quedan días para arreglarlo.
- **Visita guiada al manejo del panel** el lunes 09/11, antes del bloque 6. Apuntado en la guía y el roadmap.

### Siguiente paso
- Claude: preparar la tabla de revisión del enunciado (con el PC y la app de escritorio encendidos).
- Daniel: **Bloque 5 · PostgreSQL: modelo e idempotencia** (calendario: sábado 07/11; jueves 05/11 descanso).

## Sesión 8 · Martes 03/11/2026 (tarde) · Estudio: bloques 1 y 2 ✅

### Avanzado
- **Cambio de enfoque a petición de Daniel:** al empezar el bloque 1 dijo que del proyecto «solo le suenan cosas».
  Se volvió a la base: 6 pasos cortos, una pregunta por paso y la **analogía de la cocina** (USGS = proveedor,
  productor = el que recibe, Kafka = barra de comandas, consumidor = cocinero, PostgreSQL = despensa, API = camarero,
  panel = carta, túnel = puerta a la calle). Funciona: mantener este formato en los siguientes bloques.
- Pasos hechos: (1) el viaje de un terremoto · (2) imagen, contenedor y servicio; `command` decide qué programa
  ejecuta la imagen común `observatorio-backend` · (3) comentarios de `compose.yaml` (`kafka-init`) · (4) los 5
  obligatorios y los 6 ayudantes · (5) `stop` → `up -d` → `ps` → panel de Netlify con datos · (6) por qué una
  parada < 24 h no pierde terremotos.
- Práctica real: `docker compose --profile tunel stop` (8 contenedores parados) → `up -d` → `ps`: los 7 en marcha,
  `tunel` incluido; `kafka-init` en `Exited` (normal). El panel de Netlify muestra terremotos y el estado de ingesta.
- Comprobado en el código (no de memoria): el histórico 2025 entró por `terremotos.live`
  (`historico_cargar.py`, línea 5); `terremotos.replay` es solo para la demostración.

### ⚠️ Para repasar el domingo (colchón)
- Confundió `kafka` con `kafka-init` al nombrar los 5 obligatorios → `kafka` es la barra; `kafka-init` la monta y termina.
- Atribuyó el almacenamiento a los trabajadores → **no guardan** el productor ni el consumidor: guarda Kafka
  (7 días o 512 MB) y USGS solo enseña las últimas 24 h (ventana móvil, no «lo que tarda en publicar»).
- Pensó que `kafka-init` crea réplicas (`--replication-factor 1` = una sola copia), que «se queda a la espera»
  (TERMINA) y que crea la imagen (la construye Compose desde el `Dockerfile`).
- Dirección de la API: **recibe** las preguntas del panel y responde con datos de PostgreSQL.

### Problemas y dudas
- Al hacer `up -d`, `productor`, `consumidor`, `consumidor-replay` (y `api`, según `ps`) salieron como `Recreated`.
  Causa: **no lo sé** (sospecha no comprobada: cambio de imagen hoy). Sin pérdida de datos (los datos están en volúmenes).
- Aviso `No services to build` al hacer `up -d`: causa exacta no confirmada; no impidió arrancar.
- Falsa alarma: parecía que el comando `Select-String` de la guía solo devolvía una línea; era la terminal demasiado
  pequeña. El comando de la guía es correcto.

### Bloque 2 · Productor y mensaje ✅ (misma tarde, 20:01–20:50)
- Pasos: (1) el ciclo de cada minuto, con los logs reales (`eventos=` baja de 216 a 213: ventana móvil) · (2) `id` +
  `updated` y los 4 casos · (3) el mensaje: sobre (`schema_version`, `source`, `mode`, `ingested_at`, `replayed_at`)
  + carta (`event` sin modificar); `time` = cuándo ocurrió, `ingested_at` = cuándo lo descargamos · (4) publicar →
  confirmación de Kafka → marcar (perder frente a duplicar) · (5) errores reintentables (espera 2/4/8 s) y definitivos
  · (6) memoria: diccionario en RAM + tabla `version_publicada`. Extra: huella solo de `features` y latido.
- Dato real del log: `estado cargado: 1091 versiones ya publicadas` (1 fila por terremoto en `version_publicada`,
  con su último `updated`; comprobado en `db.py` y `01_esquema.sql`).

### ⚠️ Para repasar (bloque 2)
- No sabía por qué `eventos=` baja: entran los nuevos y salen los de más de 24 h; el número es el neto.
- Qué guarda la «libreta» del productor: solo `id → updated` de la última versión publicada, no el terremoto.
- Sin la libreta en PostgreSQL no se «pierde» nada: se **republican** como nuevos (duplicados que el consumidor tolera).
- Latido: describió el mecanismo, pero no el caso → `Up` = el proceso existe; latido = completa ciclos (detecta un productor colgado).
- Defensa: decir «para no perder datos» en vez de «por seguridad» al explicar el orden publicar → marcar.

### Siguiente paso
- **Bloque 3 · Kafka** (topic, partición, clave, offset, grupo, LAG). Con los bloques 1 y 2 hechos el 03/11,
  el calendario de la guía vuelve a ir al día.

## Sesión 7 · Martes 03/11/2026

### Avanzado
- **Contraste de la Conclusión 3 con el catálogo** (`backend/src/contrastar_fdsn.py`, probado antes por Claude con datos
  simulados): feed el 31/10 = 25 → nuestra base hoy = 27 → catálogo FDSN hoy = 28. Falta 1 (M4,7 Vanuatu, nunca en el
  feed), 0 cambios de magnitud. Recalculado: −44,2 % frente a la media; 27 días de 2025 (7,4 %) con ≤ 28.
  **La conclusión se mantiene.** Memoria §7 y §5.4 (exactitud) actualizadas. **Trabajo técnico terminado.**

### Problemas
- Ninguno técnico. Daniel aún no maneja el panel con soltura: se trabajará en los bloques de estudio.

### Siguiente paso
- Lista final de comprobación de la guía de entregables. Después, estudio desde cero con `docs/guia-estudio.md`.

## Sesión 6 · Lunes 02/11/2026

### Avanzado
- Arranque tras la noche: `docker compose --profile tunel up -d`. Parada de **20 h 16 min** (< 24 h): la primera
  descarga recuperó **212** novedades sola. Evidencia añadida a `recuperacion-parada-nocturna.txt` y memoria §5.2bis.
- Indicaciones para dejarlo recogiendo datos de continuo: PC sin suspensión, Docker Desktop arrancando al iniciar
  sesión, y no hacer `stop` (los servicios tienen `restart: unless-stopped`).
- Docker Desktop avisa de «Outdated version»: no se actualiza hasta después de la entrega.

### Problemas
- No se había explicado que, para seguir ingiriendo, el sistema tiene que quedarse encendido. Explicado hoy.

### Siguiente paso
- 03/11: re-descarga FDSN del periodo de la Conclusión 3 y comparar con el feed.
- Bloque 1 de la guía de estudio.

## Sesión 5 · Domingo 01/11/2026

### Avanzado
- Arranque en frío tras apagarlo todo por la noche: Docker Desktop → `docker compose up -d` → `docker compose ps`
  → `/api/salud` correcto.
- **Recuperación automática comprobada:** el sistema estuvo parado de 31/10 15:27 UTC a 01/11 08:16 UTC
  (~16 h 49 min). La primera descarga publicó **175 novedades** y las siguientes 0–1. Como la parada fue menor
  de 24 h, el feed las cubría. Evidencia: `docs/evidencias/recuperacion-parada-nocturna.txt`. Añadido en
  memoria §5.2bis y en defensa.

- **Fase 10 · túnel:** servicio `tunel` (imagen oficial `ngrok/ngrok`) en `compose.yaml`, apuntando a
  `http://api:8000`, con profile `tunel` y token en `.env`. URL pública:
  https://unbolted-decorated-heaving.ngrok-free.dev → `/api/salud` responde OK desde internet.
- **Fase 10 · Netlify:** repo conectado (base `frontend`), `config.json` con la URL de ngrok, origen de Netlify
  añadido a `CORS_ORIGINS` en `.env` → https://adorable-zabaione-a69bde.netlify.app/ muestra datos reales.

### Problemas
- No se pudo instalar ngrok en Windows: Microsoft Store en blanco; `winget -s msstore` → `0x8a15005e`
  (certificate pinning); con el bypass temporal (desactivado después) → `0x8007041d` al instalar; el .exe directo,
  bloqueado por Defender (falso positivo que la propia ngrok reconoce).
  **Solución:** ngrok en contenedor (opción B del README del profesor). Causa exacta del fallo de la Store: no lo sé.
- Desde el móvil, la web de Netlify pedía login («This site is private»): los proyectos nuevos de Netlify son
  privados por defecto. **Solución:** Project visibility → Public. Prueba con datos móviles OK (224 eventos),
  captura `fase10-movil-netlify.png`.

- CORS comprobado con curl: el origen falso no recibe `access-control-allow-origin`; el de Netlify sí. **Fase 10 cerrada.**

- **Fase 11 · reproducción:** esquema `replay` (`sql/02_reproduccion.sql`), servicio `consumidor-replay` (mismo código),
  `productor_replay.py` (Kamchatka, 96 eventos + 3 casos), API `?mode=replay`, panel con selector y banda
  «REPRODUCCIÓN». Resultado: 96/97/0; el evento de prueba vale 4,3 en replay y sigue 4,2 en public.
  Antes de pasarlo, Claude lo probó con un PostgreSQL local y compiló el panel.

- Captura del panel en REPRODUCCIÓN. Descubierto al verla: la ventana de 3 h trae terremotos de todo el mundo
  (90 de 96 en Kamchatka). Corregidos los textos («ventana del M8,8», no «secuencia»), que decían más de la cuenta.
- **Prueba «reiniciar consumidor»:** parado → LAG 99; arrancado → LAG 0, recuentos iguales (96/97/0).
- **Prueba «cerrar/reabrir túnel»:** aviso rojo conservando la última lectura; al reabrir, misma URL de ngrok y
  recuperación automática sin recargar. **Las 11 pruebas de aceptación tienen evidencia (memoria §9). Fase 11 cerrada.**

- **Fase 12 · mediciones** (tarde, 18:05 UTC): `backend/src/medir.py` + servicio `medir` (profile). Probado antes por
  Claude con un PostgreSQL local (detectó que con pocos puntos la tabla B «mentiría» → ahora se detiene y avisa).
  Resultados: diccionario ≈23 000× más rápido que la lista con 100 000 ids; STRtree ≈8× (8 000/8 000 iguales);
  ventanas de 1 h de todo 2025 en 12,6 ms; índice por id ≈2 000× con 3 M filas sintéticas (esquema `bench`, borrado).
  Recursos medidos: base 34 MB, Kafka 55 MB, ≈1,4 GB de RAM, feed ≈140 KB por consulta. Memoria §8 redactada.
- Sin explicación: Kafka marcaba 122 % de CPU en la única lectura de `docker stats`.

- Costes completados: PC ≈1 000 € (dato de Daniel; DxDiag: Ryzen 7 5800X, 32 GB, RTX 5060 Ti, Windows 11 Pro),
  ≈6–7 h de desarrollo en total (dato de Daniel), luz con el PVPC de octubre de 2026 (0,194 €/kWh, Selectra) y
  100 W supuestos. Resumen ≈46 €/mes + ≈90–105 € de desarrollo. **Fase 12 cerrada.**

- **Fase 13 · memoria:** diccionario de datos (§2); análisis de calidad por las 6 dimensiones con
  `analisis/calidad.sql` (§5.4, evidencia `fase13-calidad.txt`); Conclusión 2 redactada (EE. UU.: 75,1 % sin filtro →
  3,3 % con M ≥ 4); secciones viejas actualizadas. Todas las secciones en ✅.
- Descubierto en calidad: la «ocurrencia → ingesta» (mediana 453 min) engañaba por las cargas de golpe; medido bien
  (solo con el productor en marcha): mediana 61 s. Un terremoto de Alaska con 33 versiones. La única consulta fallida
  fue un error DNS al reconstruir el contenedor; el reintento funcionó.
- Hueco de 1,3 h sin consultas el 01/11 (15:46–17:05 UTC): el PC estuvo **suspendido** durante el descanso (dato de Daniel).

- README reescrito siguiendo los 9 puntos de la guía §1.4 + estructura + mapa de evidencias.

- `docs/guia-estudio.md`: 12 bloques del 02/11 al 17/11 (sin jueves, 2 días de colchón) + comprobación final el 18/11.
- `docs/prompt-principal.md` actualizado (estructura, enlaces y estado).

### Siguiente paso
- 03/11: re-descarga FDSN del periodo de la Conclusión 3 y comparar con el feed.
- Estudiar con `docs/guia-estudio.md`. Checklist final el 18/11.
- ~03/11: re-descarga FDSN del periodo de la Conclusión 3.

## Sesión 4 · Sábado 31/10/2026

### Qué se hizo
- **Fase 9 · panel Angular** con Claude Code, en 6 bloques. El mapa del profesor se conserva y se amplía; sin dependencias nuevas.
  1. **Conexión y estado:** `config.json` en modo `api`; `api.service.ts` es el único archivo que habla con la API; componente
     `estado-sistema/`. Si la API falla: aviso rojo, se conserva la última lectura y se marca como antigua.
  2. **Filtros:** fecha UTC, magnitud y país (`filtros/`), con validación. Si cambian durante una consulta, esta se repite al
     terminar, sin peticiones solapadas. «Filtros de esta lectura» sale de la respuesta, no del formulario.
  3. **Tabla:** `tabla-eventos/`, ordenable y paginada (50 filas), con los mismos datos que el mapa.
  4. **Estadísticas:** `estadisticas/`, ventanas de 1 h UTC (SVG), país, subregión, magnitud y profundidad (tablas HTML con barras).
  5. **Comparación con 2025:** recuento, esperado, variación, mediana, P10–P90, % de días y nota de la API.
  6. **Revisión final:** repetidas las pruebas sobre el código final, build de producción, CORS real, móvil y fichas.
- **Cambios de Daniel en la API:** `sin_valor.magnitud_excluidos_por_filtro` (D31), `cobertura_feed_desde` y `periodo_cubierto` (D32).
- Decisión de Daniel: lista de países fija desde el catálogo (177 + «Sin país asignado»), no `por_pais` como decía el encargo (D33).
  Antes de cambiarla se comprobó que el catálogo y la tabla `pais` coinciden: 177 códigos y los mismos nombres.
- Decisión de Daniel: el porcentaje se muestra con aviso (D39) y el umbral `BASE_MINIMA = 1` queda como criterio nuestro (D40).
- Evidencia: `docs/evidencias/fase9-panel.txt` y capturas `fase9-bloque*.png`.

### Resultados
- Últimas 24 h (31/10, ~11:30 UTC): **24 frente a 50,14 con M≥4 (−52,1 %)**; el 1,4 % de los días de 2025 tuvo 24 o menos. Mediana 43, P10–P90 31–69.
- Sumas por país, subregión, magnitud, profundidad y hora = total de la API (218). Todo 2025: 8.760 ventanas, 18.302 eventos, ~0,66 s.
- Caída real de la API: aviso, datos conservados y recuperación sola sin recargar.

### Problemas y solución
- **Lista de países que encogía:** `por_pais` con `country_id=USA` devuelve 1 fila. Primero se pidió sin ese filtro; después Daniel
  decidió usar el catálogo, porque tampoco se podía elegir un país sin eventos en el periodo aplicado.
- **Fechas invertidas:** la API responde 200 con 0 eventos; parecería que no hubo terremotos → el panel valida antes de enviar.
- **Tramos de magnitud vacíos:** la API no envía los tramos con 0, y dibujar solo lo recibido escondía el hueco 3,5–4,0 → se rellenan.
- **Porcentajes engañosos:** semana 24–31/10 = −94,6 % solo porque no había datos antes del 30/10. Primero se avisó con un apaño de
  25 h; Daniel añadió la cobertura a la API y el panel usa ahora esos campos. Se añadieron también los avisos de periodo dentro de 2025,
  fin en el futuro y base muy pequeña.
- **`periodo_cubierto = false` tiene dos causas** (empieza antes de los datos o termina en el futuro): el panel las separa con `cobertura_feed_desde`.
- **Errores de Claude encontrados al probar:** barras estrechas (`table-layout: fixed` tomaba el ancho de encabezados ocultos, y además la
  rejilla salía a 3 columnas); fecha equivocada en el aviso de estadísticas antiguas; texto «0 no coincide con el total de 0»; el desplegable
  de país ensanchaba la página a 353 px en pantallas de 320 px. Corregidos.
- **Falsos positivos de los guiones de prueba** (el panel estaba bien): EE. UU. no se podía elegir porque el escenario previo lo dejaba fuera
  de la lista entonces vigente; «Limpiar» parecía hacer 4 peticiones porque el guion mezclaba las del escenario siguiente.

### Observaciones
- **Desfase de reloj:** Docker va unos 6,8 s por detrás de Windows. No afecta a los avisos, porque la antigüedad se calcula solo en el servidor.
- **Consultas cada ~55 s, sigue sin explicar:** en una prueba de 2 min el reloj de la API avanzó al ritmo del navegador, así que su hora no
  parece la causa; las ingestas siguieron saliendo a ~55 s (109 s en dos ciclos). No se ha investigado más.
- Aviso de compilación de `leaflet` («not ESM»): viene de la base del profesor y no se oculta, para no tocar `angular.json`.
- Subregiones en inglés: es como vienen del catálogo; no se traducen.

### Commits
- `656791c` Bloque 1 · `ef2ab80` y `f695320` Bloque 2 · `b0f81c0` Bloque 3 · `087aa53` Bloque 4 · `a16ce1b` Bloque 5. Bloque 6 pendiente de commit de Daniel.

### Siguiente paso
1. ~03/11: volver a descargar del catálogo las 24 h del 30/10 09:28 → 31/10 09:28 UTC y compararlas con el feed.
2. Fase 10: cuentas de ngrok y Netlify, túnel, `apiUrl` HTTPS en `config.json`, origen de Netlify en `CORS_ORIGINS` y prueba desde otro dispositivo.

---

## Sesión 3 · Sábado 31/10/2026

### Qué se hizo
- **Consumidor → PostgreSQL (idempotente):**
  - `validacion.py`: reglas con motivos fijos (schema, id, updated, time, type, geometría, rangos, profundidad, magnitud, fecha).
  - `db.py`: versión con `ON CONFLICT DO NOTHING`; UPSERT en `evento_actual` con `WHERE updated_ms <` y
    `RETURNING (xmax = 0)` para distinguir insertado/actualizado; cuarentena con UNIQUE (topic, partición, offset);
    todo en una transacción.
  - `consumidor.py`: valida → guarda → confirma el offset.
  - Imagen única `observatorio-backend`; `psycopg[binary]==3.2.3`.
  - Comprobado antes en el entorno de Claude: los 8 casos clasificados bien; muestra real del 28/10 = 185 válidos + 2 excluidos (explosion); SQL validado con pglast.
- **Prueba FAQ 12 + calidad** (`pruebas_faq12.py`, datos sintéticos `PRUEBA-*`): 8 mensajes → 3 actuales
  (E1 = 4,6), 4 versiones y 2 en cuarentena. Evidencia: `docs/evidencias/fase5-faq12-idempotencia.txt`.
  - Observación: el consumidor intercala particiones; dentro de la partición 0 el orden de E1 se mantiene.

### Problemas y solución
- Una consulta de verificación pedía `updated_at` en `evento_version` (no existe esa columna): error de Claude.
  Corregida con `to_timestamp(updated_ms / 1000.0)`.

- **Productor real** (`productor.py`): diccionario en memoria + `version_publicada` en PostgreSQL; publicar →
  confirmación de Kafka → marcar como publicada; reintentos 2/4/8 s (timeout, red, 429, 5xx, JSON); cada intento
  en `consulta_ingesta`; originales `.geojson.gz` en `data/raw/` con retención de 24 h; healthcheck por latido.
  - Simulación previa con la muestra (sin red): ciclo 1 → 187 publicados; ciclo 2 → 0; revisión simulada → 1.
  - **Con datos reales (31/10, 06:48–06:53 UTC):** 220 eventos por respuesta; tras la primera carga, 0 publicados
    por minuto; cuarentena: `type=explosion` (1), **`type=quarry blast` (1, tipo nuevo no visto en la muestra)** y el caso sintético `lat_fuera_de_rango`.
- **Problema:** se guardaba un original por minuto aunque no hubiera cambios, porque USGS cambia
  `metadata.generated` en cada respuesta y el hash del archivo completo siempre era distinto.
  **Solución:** huella calculada solo sobre `features`. Probado: si solo cambia `generated` → no se guarda; si cambia un terremoto → sí.
- **Observación sin explicar:** las consultas salen cada ~55 s en lugar de 60 s (diferencias entre
  `solicitada_at`). Causa no confirmada (¿reloj de la VM de Docker Desktop?). Pendiente de medir.

- Productor reconstruido: `estado cargado: 222 versiones` → `publicados=0` (confirma la persistencia del estado).
- **Conciliación (Consistencia):** 222 publicados = 221 actuales + 1 cuarentena real; 0 ids perdidos.
  Primero pareció un descuadre: Claude contó `PRUEBA-EXPLOSION` como real. Los datos sintéticos se separan por el prefijo.
  Evidencia: `docs/evidencias/fase5-conciliacion.txt`.
- Duda de Daniel: ¿`up -d --build productor` duplica servicios? No: recrea el contenedor. Y aunque hubiera
  dos productores, la idempotencia del consumidor evitaría duplicar datos.

- **Fase 6 · país:** `geografia.py` (Shapely 2.0.6, STRtree, `covered_by`, desempate alfabético, None = sin país);
  el consumidor carga los 177 países al arrancar y asigna el país; `rellenar_paises.py` para los ya guardados;
  catálogo montado en solo lectura.
  - **Hallazgo:** las geometrías de USA y SDN no son válidas (autointersección); se reparan en memoria con
    `make_valid` (el área no cambia).
  - **Error de Claude detectado por su propia prueba:** con `predicate="covers"` todo salía sin país (el sentido
    del predicado está invertido en `STRtree.query`). Corregido a `covered_by`. Verificado frente a un bucle simple:
    mismo resultado en 185/185; STRtree ~10 veces más rápido.
  - Resultado real: 225 eventos → 181 con país, 44 sin país, 0 coincidencias múltiples. Por país (reales):
    EE. UU. 170, sin país 44, Puerto Rico 2…
  - **Observación para el análisis:** el 77 % de los eventos son de EE. UU. porque el feed incluye magnitudes muy
    pequeñas que solo detectan las redes densas de EE. UU. Es un sesgo de **cobertura de detección**, no de actividad (enunciado §8).
  - Reproducibilidad: `numpy` (dependencia de shapely) no estaba fijado → `numpy==2.5.4`.

- **Fase 7 · histórico 2025:** `historico_descargar.py` (count previo, división si > 20.000, archivos tal cual,
  `manifest.json`, `consulta_ingesta`, reutiliza lo ya descargado) y `historico_cargar.py` (deduplica por id con el
  `updated` mayor y publica por Kafka con `source='usgs-fdsn'`). El productor monta ahora `./data:/data`;
  `data/historico/` fuera de Git.
  - Comprobado en la muestra de enero: `minmagnitude=4` incluye mag = 4,0 (70 eventos) → filtro `mag >= 4`.
  - Deduplicación probada con un caso sintético de frontera (se queda la versión con el `updated` mayor).
  - Real: 12 consultas, 18.302 eventos (13 MB), count = descargados en todos los meses, 0 repetidos entre meses;
    máximo mensual 2.684 (julio). Primera media diaria provisional (mientras el consumidor seguía procesando): 41,16.
  - **Llama la atención:** julio (2.684) y agosto (2.222) casi duplican al resto de meses (~1.200–1.600). Pendiente de
    investigar con datos (¿réplicas de un gran terremoto?).

  - Carga completa: 18.302 guardados + 0 en cuarentena = 18.302 ✓. **Media diaria 2025 (mag ≥ 4) = 50,14.**
  - Pico de julio y agosto: el terremoto más fuerte del periodo es el **M8,8 de Kamchatka del 29/07/2025**, más otro
    M7,4 en el este de Kamchatka (20/07). Hipótesis: réplicas → pendiente de confirmar con la distribución espacial.
  - La pregunta de por qué se divide entre 365 no la sabía → explicada (los días con cero eventos también cuentan).
  - Evidencia: `docs/evidencias/fase7-historico.txt`.

  - **Hipótesis confirmada:** en la zona de Kamchatka (lat 45–60, lon 150–170) se pasa de 19,3 eventos/mes (ene–jun)
    a 1.375 en julio y 1.254 en agosto, y luego baja; el resto del mundo es estable. La zona = 21,7 % del año. La media
    diaria sin la zona sería 39,25 (frente a 50,14). → **Primera conclusión redactada** (memoria §7).

- **Fase 8 · API:** `api.py` (FastAPI 0.115.6, Uvicorn): `/api/eventos` (GeoJSON, filtros start/end/min_mag/country_id,
  `SIN_PAIS`, paginación, máximo 5.000), `/api/estadisticas` (totales, nulos, país, subregión, ventanas de 1 h UTC con
  `generate_series`, tramos de magnitud de 0,5, clases de profundidad, comparación con 2025 usando `mag >= max(4, min_mag)`),
  `/api/salud`. Una sola función de filtros para todas las rutas. Excluye las fuentes `prueba…`. Si la BD falla → 503.
  CORS por variable de entorno. Puerto publicado solo `127.0.0.1:8000`.
  - Probada antes en el entorno de Claude con un **PostgreSQL embebido (pgserver)** y el mismo `01_esquema.sql`: filtros,
    nulos, SIN_PAIS, paginación, estadísticas, CORS (permitido/rechazado), 422 y 503 → todo correcto.
  - Real (31/10 09:28 UTC): 208 terremotos en 24 h (156 EE. UU., 45 sin país); **comparación mag ≥ 4: 25 frente a la
    media de 2025 de 50,14 → −50,1 %**.
  - **Hipótesis:** la diferencia se debe sobre todo a que el feed en tiempo real está incompleto para M4–4,5 fuera de
    EE. UU. (el catálogo de 2025 ya está revisado). Por comprobar: (1) comparación con `min_mag=4.5`; (2) volver a descargar
    del catálogo ese mismo periodo dentro de unos días.
  - Observación sin explicar: 0 eventos entre 3,5 y 4,0 en esas 24 h (13 entre 4,0 y 4,5).
  - Pregunta generated/last_ingestion: Daniel las tenía al revés (generated cambia siempre; last_ingestion se congela). Corregido.

  - Con mag ≥ 4,5: 13 frente a 23,45 (−44,6 %) → la hipótesis de que faltan sobre todo M4,0–4,5 **no se confirma**.
  - Distribución diaria de 2025 (dimensión fecha): mediana 43, p10 31, máximo 645; solo 10/365 días ≤ 25 (sin Kamchatka:
    mediana 37, p10 26, 29/365). → **Conclusión 3 redactada**: bajo, pero no excepcional; la media exagera.
  - API mejorada: `dias_2025` (mediana, p10, p90, % de días ≤ recuento reciente cuando el periodo es de 24 h). Probado con pgserver.

### Siguiente paso
- Commit Fase 8; Fase 9: panel Angular.

---

## Sesión 2 · Viernes 30/10/2026

### Qué se hizo
- Comprobado que los documentos «nuevos» del profesor (guía y FAQ) y la carpeta de `Downloads` son idénticos
  a los del repositorio → no hay versión nueva del enunciado.
- Notebook `01_exploracion_feed.ipynb` reescrito con explicación conceptual por apartado y comentarios
  línea a línea (Daniel se agobiaba con el pandas sin comentar).
- Creados `docs/memoria.md` (memoria que se rellena por fases, con un registro de decisiones en el Anexo A) y
  `docs/defensa.md` (preguntas probables del profesor; las responde Daniel).
- **Fase 3, paso 1:** `compose.yaml` solo con Kafka (`apache/kafka:4.1.2`, KRaft, volumen `kafka-data`,
  retención de 7 días o 512 MB, sin publicar puertos al host, topics sin creación automática).
  - `docker compose up -d kafka` → healthy.
  - Topic `pruebas` creado a mano.
  - Productor de consola → consumidor de consola: los mensajes «hola terremoto» y «bienvenido kafka» llegan.
  - Evidencias: `docs/evidencias/fase3-docker-desktop-kafka.png`, `fase3-productor-consola.png`,
    `fase3-consumidor-consola.png`.
  - Tras cerrar y volver a abrir los contenedores, los mensajes siguen ahí.

### Problemas y solución
- Docker Desktop avisa de que su versión ya no tiene soporte. No impide trabajar; se actualizará más adelante,
  en un momento en que no haya contenedores con datos importantes.

- **Persistencia confirmada:** `docker compose down` + `up` → los mensajes del topic `pruebas` siguen ahí (volumen `kafka-data`).
- Explicado dónde ver `(healthy)`: columna STATUS de `docker compose ps`.
- **Fase 2:** creado `docs/contrato-mensaje.md` (v1): topics `terremotos.live` y `terremotos.replay`;
  clave = id del evento; valor = `schema_version`, `source`, `mode`, `ingested_at`, `replayed_at` y `event`
  (el Feature original sin modificar). El productor no filtra ni transforma.

- **Fase 3, paso 2:** imagen Python común (`backend/Dockerfile`, `aiokafka==0.12.0`), `src/mensajes.py`
  (construye mensajes según el contrato), `src/productor_prueba.py` (envía us7000ttlm y termina) y
  `src/consumidor.py` (muestra cada mensaje; `enable_auto_commit=False` y commit DESPUÉS de procesar).
  `compose.yaml`: `kafka-init` crea `terremotos.live` y `terremotos.replay` (3 particiones, `--if-not-exists`);
  `productor-prueba` con perfil `pruebas` (se lanza con `docker compose run --rm productor-prueba`).
  - Resultado: publicado en partición 1, offset 0; el consumidor lo recibe en partición 1, offset 0.
  - Evidencia: `docs/evidencias/fase3-pipeline-python.txt`.
  - Aviso de Kafka sobre mezclar «.» y «_» en los nombres de topics: sin impacto (solo usamos «.»).
- **Experimento clave:** al reenviar el mismo evento, Kafka lo guarda otra vez (offset 1). Kafka es un
  registro de mensajes y **no deduplica**. Con un INSERT simple habría 2 filas del mismo terremoto; con el
  feed cada 60 s, 187 × 60 × 24 = 269.280 inserciones al día de eventos repetidos.
  Daniel lo dedujo él solo. → Motiva las dos defensas: productor con estado `(id, updated)` y consumidor idempotente.

### Mejora pendiente (menor)
- `docker compose` construye dos imágenes iguales (`…-consumidor` y `…-productor-prueba`) desde el mismo
  Dockerfile. Se puede dar un nombre común con `image:` para construir una sola.

- **Fase 4 (conceptos, sin código):** niveles conceptual/lógico/físico, entidades (Terremoto, Versión, País,
  Día, Cuarentena, Estado de ingesta), el **grano** de cada tabla y la relación con el modelo dimensional
  (hecho = terremoto; dimensiones = país y día).
  - Confusión trabajada: Daniel pensaba que para contar terremotos se usa la tabla de versiones. Se corrigió
    (estado actual = 1 fila por terremoto; versiones = historial, como `git log`). Segundo ejercicio con la
    FAQ 12: razonamiento correcto (estado actual = 2 y la magnitud es la de la última versión), pero contó
    «3 versiones por terremoto» en lugar de 3 en total → hay que repasar la tabla de la FAQ 12.

- **Fase 4 · base de datos levantada:** `sql/01_esquema.sql` (7 tablas, 3 índices, dimensión fecha con
  1.461 días de 2024 a 2027), `.env.example` y servicio `postgres:17-alpine` en compose (volumen `pg-data`,
  `sql/` montado en `/docker-entrypoint-initdb.d`, healthcheck `pg_isready`, sin puertos publicados).
  - Sintaxis del SQL validada antes con `pglast`.
  - En el equipo de Daniel: 7 tablas creadas; `\d evento_actual` muestra PK, índices, CHECK y FK; fecha = 1461 filas.
  - Prueba: el segundo INSERT del mismo `event_id` falla con `duplicate key value violates unique constraint`.
  - Evidencia: `docs/evidencias/fase4-postgres-esquema.txt`.
- ⚠️ Recordatorio: el SQL de `/docker-entrypoint-initdb.d` solo se ejecuta con el volumen vacío. Si se cambia
  el esquema: `docker compose down -v` (borra los volúmenes) o una migración.

### Cambio de método (decisión de Daniel, 30/10)
«Construir primero, estudiar después»: terminar el proyecto completo y funcionando en bloques grandes,
y dedicar los últimos días a estudiarlo de principio a fin con una guía de estudio. Registrado en el
prompt principal. Objetivo: tener todo funcionando hacia el 12–13/11 y dejar unos 5 días de estudio.

### Siguiente paso (próxima sesión)
1. Consumidor → PostgreSQL: UPSERT en `evento_actual` condicionado por `updated_ms` + INSERT en
   `evento_version` (ON CONFLICT DO NOTHING), todo en una transacción; commit del offset después.
2. Probar la secuencia completa de la FAQ 12 (5 mensajes → 3 versiones → 2 terremotos; E1 = 4,6).
3. Pendientes menores: dar un nombre común a la imagen Python (`image:`); responder en `defensa.md` las preguntas de las Fases 1–4.

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

### Fase 1 · Exploración del feed (en curso)
- Creado `analisis/01_exploracion_feed.ipynb` (pandas): estructura, tipos, completitud, unicidad,
  `type`, magnitud, coordenadas, profundidades negativas, tiempos, `status` e `ids`.
- **Problema:** al aplanar con `json_normalize` aparecen **dos columnas `type`** (la del Feature, siempre
  "Feature", y `properties.type`). Provocaba `ValueError: Grouper for 'type' not 1-dimensional`.
  **Solución:** renombrar a `feature_type` y `geom_type` antes de quitar el prefijo `properties.`.
- Resultados (muestra del 28/10, 187 eventos): 187 id únicos; 185 earthquake y 2 explosion; mag de 0,22 a 6,0,
  sin nulos en esta muestra; 28 con mag ≥ 4; 3 profundidades negativas (2 explosiones y 1 terremoto de
  −2,31 km); `updated − time` con mediana de 3,6 min y máximo de 925,8 min; 120 automatic y 67 reviewed;
  8 eventos con más de un id asociado.
- **Documentación oficial FDSN (API del histórico)** aportada por Daniel. Datos útiles:
  - `limit` máximo 20.000: si se supera, la API responde **HTTP 400** (no trunca en silencio).
  - Método `count`: permite saber cuántos eventos hay **antes** de descargarlos.
  - `starttime` = «on or after» y `endtime` = «on or before» → **los dos extremos son inclusivos**,
    por eso hay que deduplicar los eventos que caen en el límite entre meses.
  - `mindepth`/`maxdepth` admiten de −100 a 1000 km → la propia API contempla profundidades negativas.
  - `updatedafter`: permite pedir solo lo actualizado después de una fecha → candidato para recuperar
    un hueco tras una parada de más de 24 h.
  - `eventtype=earthquake` filtra los eventos que no son terremotos; `includedeleted` y el HTTP 409 tienen que ver con los eventos borrados.
- Pregunta de comprobación (misma versión en dos consultas seguidas): Daniel respondió bien
  (0 terremotos nuevos). Matiz: no es porque «no haya terminado», sino porque el feed devuelve toda la
  ventana de 24 h en cada consulta; mismo `id` + mismo `updated` = misma versión, ya publicada.

### Dudas abiertas
- Significado oficial de la profundidad negativa y si `mag` puede ser nula o negativa: pendiente de la
  descripción por campo de https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

### Siguiente paso
1. Instalar la extensión Jupyter en VS Code y ejecutar el notebook.
2. Rellenar las conclusiones del notebook y hacer commit.
