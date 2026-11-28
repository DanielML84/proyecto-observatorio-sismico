# Roadmap · Acceso seguro al cuadro de mando del Observatorio

**Objetivo:** ver el cuadro de mando y analizar los datos con código desde cualquier sitio, sin exponer la base de datos.
**Plan aprobado por el profesor (26/11/2026):** una sola puerta (`ngrok http` + login de Google); detrás, cada uno en su
contenedor: panel (cuadro de mando), API de solo lectura y Jupyter con usuario de solo lectura. PostgreSQL sin puertos.
**Además, el profesor pide el bastión en AWS** para practicar y conocerlo.
Sin enunciado escrito: el profesor quiere ver cómo nos buscamos la vida.

Leyenda: `[ ]` pendiente · `[~]` en curso · `[x]` hecho · ⚑ = hacer commit al terminar (lo hace Daniel)

---

## Fase 0 · Preparación
- [x] Esquema y plan presentados al profesor → aprobados (26/11)
- [ ] Rama nueva en el repositorio del Observatorio (`git checkout -b cuadro-de-mando`)
- [ ] Comprobar `.gitignore`: `.env`, `*.pem`, claves y backups fuera de Git ⚑

## Fase 1 · Cuadro de mando (sesiones 10 y 11)
- [ ] Fichas SMART de los KPIs (fórmula, objetivo, umbral, de qué campo de la API sale)
- [ ] Endpoint o campos nuevos en la API si hacen falta ⚑
- [ ] Fila de KPIs en Angular: semáforo (≥100 % / 80–99 % / <80 %), delta y tendencia (±5 %) ⚑
- [ ] Reordenar el panel con el layout de la sesión 10 (KPIs arriba, gráficos, tabla abajo) ⚑
- [ ] 2 visualizaciones nuevas + interactividad ⚑

## Fase 2 · Puerta única con login
- [ ] Contenedor `panel` (Angular compilado servido desde Docker) ⚑
- [ ] Repartir por rutas en una sola URL (`/`, `/api`, `/jupyter`) — por comprobar si hace falta un proxy
- [ ] Login de Google en ngrok (Traffic Policy, OAuth) solo para los correos de la lista ⚑
- [ ] Comprobar: sin login → rechazado; con login → panel y API funcionan

## Fase 3 · Jupyter
- [ ] Contenedor `jupyter` en la red de Docker, sin puerto publicado a internet ⚑
- [x] Usuario de PostgreSQL de solo lectura `lector` (`GRANT SELECT` + sesión en solo lectura) creado en el bastión (28/11) ⚑
- [ ] Notebook de ejemplo con `psycopg` + pandas
- [x] Comprobar: `lector` no puede `INSERT`, `DROP` ni `DELETE` (probado con `psycopg` por el túnel; `permission denied` y `read-only transaction`)

## Fase 4 · Bastión en AWS (práctica pedida por el profesor)
- [x] Revisar la cuenta de AWS del máster: 50 $, `us-east-1`, 0 instancias, `vockey` (27/11)
- [ ] Leer el apartado Amazon EC2 del Readme: límite de instancias a la vez (pendiente; solo se ha lanzado 1)
- [x] 1. Par de claves `ed25519` creado en MI PC (`ssh-keygen`, en `~/.ssh`, con passphrase); la privada no sale del PC (28/11)
- [x] 2. Importada SOLO la clave pública en AWS como `bastion-observatorio` (AWS acepta `ed25519`) (28/11)
- [x] 3. Grupo de seguridad `bastion-sg`: puerto 22 solo desde mi IP (/32). **Opción A elegida: una sola EC2** (bastión + PostgreSQL); la B (dos EC2) queda como ampliación
- [x] 4. EC2 `bastion-observatorio` (t3.micro, Amazon Linux 2023, us-east-1) con esa clave y ese grupo. La IP pública cambia al parar/arrancar
- [x] 5. Primera conexión: huella ED25519 del servidor comprobada con el registro del sistema de AWS y aceptada ⚑ (evidencia)
- [x] 6. PostgreSQL 17 (misma versión que el proyecto) en Docker con `-p 127.0.0.1:5432:5432`; `pg_dump -Fc` en el PC → cifrado con GPG **asimétrico** (par creado en el bastión, solo la pública viaja) → `scp` → descifrado y `pg_restore` en una sola orden. Comprobado: 23772 / 28059 / 143 filas ⚑ (evidencia)
- [x] 7. Túnel `ssh -L 5433:127.0.0.1:5432` y conexión con `psycopg` desde el PC ⚑ (evidencia)
- [ ] 8. (Opcional) VSCode Remote-SSH y pgAdmin por el túnel
- [ ] 9. Apagar/terminar las instancias al acabar para no gastar créditos (cada vez que se termine de trabajar)
- [ ] 10. Limpieza: borrar `observatorio.dump` (sin cifrar) y `observatorio.dump.gpg` (prueba simétrica) de `C:\Users\Usuario\copias-bd`

## Fase 5 · Pruebas de seguridad y documentación
- [ ] El 5432 no responde desde fuera (ni en el PC ni en AWS)
- [ ] README: esquema, decisiones, pasos del bastión en orden y evidencias ⚑
- [ ] Bitácora y roadmap al día

---

## Dudas abiertas
- ¿Una EC2 (opción A, hecha) o dos (bastión público + base de datos privada)? Preguntar al profesor si exige dos. Coste/permiso de NAT por comprobar.
- Cifrado de la copia: se hizo asimétrico (par GPG en el bastión). ¿Es lo que el profesor espera? (Daniel cree que sí).
- ¿El plan gratuito de ngrok permite una sola URL para panel, API y Jupyter?
- Límite de instancias a la vez (apartado Amazon EC2 del Readme, sin leer).
- ¿Cómo se pasa a Colab? (la IP de Colab cambia; haría falta el túnel SSH desde el cuaderno; sin probar).
