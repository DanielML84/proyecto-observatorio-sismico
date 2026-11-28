# Bitácora · Acceso seguro al cuadro de mando del Observatorio

Una entrada por sesión, la más reciente arriba.
Formato: qué se hizo · decisiones · problemas y solución · commits · dudas · siguiente paso.

---

## Sesión 3 · Sábado 28/11/2026 · Bastión funcionando: túnel, solo lectura y copia cifrada

### Qué se hizo
1. Par de claves `ed25519` en mi PC (`ssh-keygen`, con passphrase) e importación de la pública en AWS (`bastion-observatorio`).
2. Grupo de seguridad `bastion-sg`: SSH (22) solo desde mi IP (/32).
3. EC2 `bastion-observatorio` (t3.micro, Amazon Linux 2023, us-east-1) con esa clave y ese grupo.
4. Primera conexión por SSH: **huella ED25519 del servidor comprobada** contra el registro del sistema de AWS (Actions → Monitor and
   troubleshoot → Get system log) antes de escribir `yes`. Quedó guardada en `known_hosts`.
5. Docker en el bastión y PostgreSQL con `-p 127.0.0.1:5432:5432` (`ss -tlnp` muestra `127.0.0.1:5432`, no `0.0.0.0`).
6. Túnel desde el PC: `ssh -i ~/.ssh/bastion-observatorio -L 5433:127.0.0.1:5432 ec2-user@<IP> -N`; prueba con
   `Test-NetConnection localhost -Port 5433` y con `prueba_conexion.py` (`psycopg`).
7. Usuario `lector` de solo lectura con **dos capas**: `GRANT SELECT` (permisos) y `default_transaction_read_only = on` (sesión).
   Prueba con `prueba_lector.py`: lee; `INSERT` y `DROP` bloqueados; y tras desactivar el modo solo lectura de la sesión,
   `INSERT` sigue bloqueado por `permission denied` → las dos capas funcionan por separado.
8. Copia de la base real: `pg_dump -Fc --no-owner --no-privileges` dentro del contenedor local → `docker compose cp` a
   `C:\Users\Usuario\copias-bd` (fuera del repositorio) → cifrado con GPG.
9. Cifrado **asimétrico**: par GPG creado en el bastión (ed25519 + subclave cv25519), clave pública exportada y traída con `scp`,
   huella comparada en ambos extremos (`F050 C517 ... 8A24`), copia cifrada con la pública, subida con `scp`. En el PC el
   descifrado falla (`No secret key`); en el bastión se descifra y restaura con una sola orden:
   `gpg --decrypt ... | docker exec -i postgres-observatorio pg_restore -U postgres -d observatorio --no-owner --no-privileges`.
10. Comprobación: `evento_actual` 23772, `evento_version` 28059, `cuarentena` 143 (iguales que en local; base de 50 MB, copia de 4,7 MB).
    `consulta_lector.py` lee 23772 eventos reales como `lector` y el `DELETE` queda bloqueado.

### Decisiones
- **Opción A:** una sola EC2 con bastión y PostgreSQL (Docker, solo en 127.0.0.1). La opción B (dos EC2) queda como ampliación.
- PostgreSQL **17-alpine** también en el bastión, igual que el proyecto (un `pg_dump` de una versión más nueva puede no restaurarse en una más antigua).
- Puerto local del túnel 5433, para no chocar con un PostgreSQL local en 5432.
- Cifrado asimétrico: la clave privada GPG nunca sale del bastión; solo viaja la pública (mismo principio que SSH).
- La copia vive fuera del repositorio (`~/copias-bd`) para no subirla a Git por error.
- Contraseñas: se piden con `read -s` o `getpass`, nunca escritas en comandos, scripts ni en el chat.

### Problemas y solución
| Problema | Solución |
|---|---|
| En «Source» de la regla escribí «My IP» como texto: error «CIDR block...» | Elegir «My IP» en la lista desplegable (rellena `x.x.x.x/32`) o escribir la IP con `/32` |
| `ssh` avisó de que no encontraba la clave (`C:\Users\Usuario\bastion-observatorio`) | Faltaba `.ssh\` en la ruta: `$HOME\.ssh\bastion-observatorio` |
| Lo que pedía `scp` no era la contraseña que tecleé (la del GPG) | Distinguir las contraseñas (tabla de abajo). Fallar no bloquea nada |
| Local: PostgreSQL 17; bastión: 16 | Borrar contenedor y volumen del bastión y recrear con `postgres:17-alpine`; volver a crear `lector` |
| Tras recrear, `lector` no existía (se saltó el paso) | Repetir el `CREATE ROLE`; comprobar con `\du lector` |
| `findstr` no encontraba `docker-compose.yml` | `docker compose config \| findstr /i "POSTGRES_DB POSTGRES_USER"` |
| GPG: `Wrong key usage` con `ed25519 encr` | ed25519 solo firma; usar `default default` (crea la subclave `cv25519` de cifrado) |
| GPG: `No agent running` (paquete mínimo) | `sudo dnf swap -y gnupg2-minimal gnupg2-full` |
| GPG: `Timeout` al pedir la contraseña; pegué el comando varias veces | Ctrl+C, `clear`, comandos de uno en uno y contraseña tecleada a mano y rápida |

### Las contraseñas (sin escribir su valor)
| # | Contraseña | Quién la pide |
|---|---|---|
| 1 | Clave SSH `bastion-observatorio` | `ssh`, `scp`, túnel (PC) |
| 2 | Usuario `postgres` (admin) del bastión | `psql`, restauración |
| 3 | Usuario `lector` | `prueba_lector.py`, `consulta_lector.py` |
| 4 | Clave privada GPG (bastión) | `gpg --decrypt` en el bastión |
| 5 | Cifrado simétrico del `.gpg` de prueba | `gpg` en el PC (solo ese archivo) |

### Archivos de la sesión (en `docs/practica-acceso-seguro/`)
- `prueba_conexion.py` (conexión como `postgres`), `prueba_lector.py` (4 pruebas de permisos), `consulta_lector.py` (datos reales + `DELETE` bloqueado).

### Commits
- Pendientes (los hace Daniel). Mensaje sugerido: `Práctica acceso seguro: bastión EC2, túnel SSH, usuario de solo lectura y restauración con GPG`.
- Comprobar que **no** entra nada de `C:\Users\Usuario\copias-bd` ni claves (`.ssh`, `.gnupg`) en Git.

### Dudas abiertas
- ¿Basta una EC2 o el profesor quiere dos? ¿El cifrado asimétrico es lo esperado?
- Límite de instancias del Readme (sin leer). ¿Colab? ¿Una URL de ngrok para todo?

### Siguiente paso
- Limpieza (`observatorio.dump` sin cifrar y `.gpg` simétrico del PC) y **parar la instancia** en AWS (la IP cambiará al arrancar).
- Después: Fase 3 (contenedor Jupyter con `lector`), Fase 2 (puerta única con login de Google) y Fase 1 (cuadro de mando).

---

## Sesión 2 · Viernes 27/11/2026 · Reconocimiento de AWS (solo mirar, sin crear nada)

### Qué se hizo
- Cuenta: AWS Academy Learner Lab. Presupuesto 50 $ (gastado 0 $). Sesión de 4 h máximo (se reinicia con Start Lab).
- Región `us-east-1` (N. Virginia). Restricción del Readme: solo `us-east-1` y `us-west-2`.
- Readme (instrucciones del 2025-06-24): superar un límite de servicio puede desactivar la cuenta y borrar recursos.
  Instancias permitidas (apartado Auto Scaling): nano, micro, small, medium y large.
- Consola de EC2: 0 instancias, 0 volúmenes, 0 IP elásticas, 1 grupo de seguridad (`default`), coste 0,00 $.
- Pares de claves: solo `vockey` (RSA, creado el 16/11). El laboratorio también da su PEM/PPK en AWS Details.
- `Actions` ofrece **Import key pair** → se sigue el plan original: crear el par en mi PC e importar solo la pública.

### Decisiones
- Crear el par con `ssh-keygen` en mi PC (en `~/.ssh`, fuera del repositorio), con passphrase.
- Huellas: la de la tabla de Key Pairs es la del par de claves; la del servidor SSH es la que se acepta en la primera conexión.

### Problemas
- Entré en CloudWatch en vez de EC2 (el buscador llevó a «EC2 Resource Health», que es de CloudWatch).
  Solución: buscar el servicio «EC2 · Virtual Servers in the Cloud» o ir a Compute → EC2.

### Dudas abiertas
- Límite de instancias a la vez (apartado Amazon EC2 del Readme, falta leerlo).
- ¿`ed25519` se acepta en Import key pair? Si no, RSA.
- ¿Una EC2 o dos (bastión + datos)?

### Commits
- Ninguno.

### Siguiente paso
- `ssh -V`, crear el par con `ssh-keygen`, importar el `.pub` en AWS.

---

## Sesión 1 · Jueves 26/11/2026 (en clase) · Plan aprobado

### Qué se hizo
- El profesor explicó en la pizarra cómo acceder a una base de datos de forma segura (motivo: ataques de agentes piratas).
  No hay enunciado: quiere ver cómo nos buscamos la vida.
- Lo que Daniel retuvo: Docker + `ngrok http`; Jupyter en Docker (8888); `ngrok tcp 5432` prohibido; AWS EC2 → bastión →
  Docker con PostgreSQL; par de claves SSH; `psycopg` para Colab; PGP tools para generar claves y cifrar.
- **Huella digital** (según el profesor): firma usada en las comunicaciones SSH → la huella del servidor que se comprueba
  en la primera conexión.
- Estudio de opciones (Claude): el cuadro de mando no necesita abrir nada nuevo porque usa la API; lo que falta es el login
  y el acceso para analizar datos.
- «Manipular» = analizar los datos con código (opción b, según Daniel).

### Decisiones
- **Aprobado por el profesor:** PostgreSQL en el PC dentro de Docker sin puertos; una sola puerta `ngrok http` con login de
  Google; detrás, cada uno en su contenedor, panel con cuadro de mando, API de solo lectura y Jupyter con usuario de solo lectura.
- El panel pasará de Netlify a un contenedor, para quedar detrás de la misma puerta.
- **El profesor quiere además el bastión en AWS** para practicar y conocerlo.
- Se trabaja sobre el repositorio del Observatorio (rama nueva) y en esta misma conversación.

### Problemas
- Ninguno técnico todavía.

### Dudas abiertas
- Créditos y límites de la cuenta de AWS del máster.
- Bastión y base de datos: ¿una EC2 o dos?
- ¿Una sola URL de ngrok para panel, API y Jupyter?

### Commits
- Ninguno todavía.

### Siguiente paso
- En casa, con la carpeta conectada: rama nueva y Fase 1 (fichas SMART de los KPIs).
- Daniel: entrar en la cuenta de AWS del máster y ver qué créditos y servicios tiene.
