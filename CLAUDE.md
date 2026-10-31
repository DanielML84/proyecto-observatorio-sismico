# Instrucciones para Claude Code · Observatorio de actividad sísmica

Trabajas con **Daniel**, estudiante junior del máster de IA y Big Data. Este es su proyecto evaluable de
Sistemas de Big Data (entrega: miércoles 18/11/2026). **Lee primero** `docs/prompt-principal.md`
(contexto completo, reglas y decisiones) y después `docs/bitacora.md` (la entrada de arriba es la última sesión)
y `docs/roadmap.md` (estado por fases).

## Reglas obligatorias
1. **Responde siempre en español.**
2. **Explica a Daniel lo que haces, paso a paso y en lenguaje sencillo**, antes y después de cada cambio:
   qué archivo tocas, para qué sirve y cómo comprobarlo. Es junior y tiene que poder defender el proyecto ante el
   profesor. Mensajes cortos y visuales (tablas, listas breves). No le des demasiada información de golpe.
3. **Comenta el código línea a línea** (o por bloques muy pequeños) en español.
4. **No inventes nada.** Basa cada decisión en el enunciado (`docs/material-profesor/`), en el contrato de la API o
   en la documentación oficial. Si no sabes algo, dilo: «no lo sé».
5. **NUNCA ejecutes `git commit`, `git push` ni nada que publique o borre datos** (`docker compose down -v`, etc.).
   Los commits los hace Daniel. Al terminar cada punto, **recuérdale hacer commit** con un mensaje propuesto.
6. Antes de dar algo por bueno, **verifícalo** (compilar, ejecutar, probar en el navegador o con curl) y enseña la evidencia.
7. Al terminar cada bloque, haz **una pregunta de comprobación corta** a Daniel (le ayuda a entender).
8. Al final de cada sesión actualiza `docs/bitacora.md` (qué se hizo, problemas y solución, siguiente paso),
   marca el avance en `docs/roadmap.md`, añade las decisiones al **Anexo A de `docs/memoria.md`** y las
   preguntas probables con **respuestas modelo** a `docs/defensa.md`.
9. Datos sintéticos de prueba: siempre identificados (prefijo `PRUEBA-`, `source` que empiece por `prueba`).

## Entorno
- Windows; Docker Desktop. Servicios: `docker compose up -d` (ver `docs/chuleta-comandos.md`).
- API en http://localhost:8000 (`/api/eventos`, `/api/estadisticas`, `/api/salud`, documentación en `/docs`).
- Frontend Angular en `frontend/` (`npm start` → http://localhost:4200).

## Tarea actual
Ver `docs/fase9-encargo-panel.md`.
