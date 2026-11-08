# Chuleta de comandos · Observatorio sísmico

> Todos se ejecutan en PowerShell **dentro de la carpeta del proyecto**:
> `cd C:\Users\Usuario\Desktop\proyecto-observatorio-sismico`
> Usuario y BD de PostgreSQL: los de tu `.env` (por defecto `observatorio`).

---

## ⭐ Uso diario (lo normal cada vez que te sientas a trabajar)

**Antes de nada:** abre **Docker Desktop** y espera a que diga que está en marcha.

| Paso | Comando | Qué hace |
|---|---|---|
| 1 · **Arrancar** | `docker compose --profile tunel up -d` | Enciende los 7 servicios, **túnel incluido**. `-d` = en segundo plano (te devuelve la terminal) |
| 2 · **Comprobar** | `docker compose --profile tunel ps` | Lista los contenedores. Deben salir **7 en `Up`**, y `api`, `kafka`, `postgres` y `productor` en `(healthy)` |
| 3 · **Ver la recuperación** | `docker compose logs productor --since 5m` | Primera línea `OK`: `eventos − publicados` = los que ya tenía. Si da **0**, probablemente ha quedado un hueco |
| 4 · **Parar** al terminar | `docker compose --profile tunel stop` | Apaga los 8 contenedores **sin borrar nada**. Al volver, el paso 1 los enciende tal cual |

- **¿Por qué `--profile tunel`?** El servicio `tunel` tiene *profile*: sin esa opción, Compose lo ignora y el panel de
  Netlify no llega a tu API. Los demás servicios arrancan y paran igual con o sin ella.
- **Si la terminal se queda sin devolverte el control** al arrancar: pulsa `Ctrl + C`. Solo corta la espera del comando;
  los contenedores siguen en marcha. Compruébalo con el paso 2.
- **Vuelve a encenderlo antes de 24 h.** El feed de USGS solo guarda las últimas 24 h: con paradas más largas queda un
  hueco (no afecta a las conclusiones, que usan periodos ya guardados).
- En `ps`, `kafka-init` aparece como `Exited (0)` cuando usas `ps -a`: es **normal** (crea los topics y termina).

## 1. Arrancar y parar (todas las opciones)

| Quiero… | Comando | ¿Pierdo datos? |
|---|---|---|
| Arrancar **todo con túnel** (lo normal) | `docker compose --profile tunel up -d` | No |
| Arrancar **sin túnel** (solo en local, sin Netlify) | `docker compose up -d` | No |
| Arrancar todo **reconstruyendo** la imagen (tras cambiar código o `requirements.txt`; es el comando que pide el enunciado) | `docker compose up --build -d` | No |
| **Parar todo con túnel** (los contenedores se quedan creados) | `docker compose --profile tunel stop` | No |
| Volver a arrancar lo parado | `docker compose --profile tunel start` | No |
| **Apagar y borrar** los contenedores (los volúmenes se conservan) | `docker compose --profile tunel down` | No |
| ⚠️ **Borrarlo TODO, también los datos** (Kafka y PostgreSQL desde cero) | `docker compose down -v` | ⚠️ **SÍ** |

> ⚠️ **No uses `down -v` antes de la entrega:** perderías el histórico de 2025 y todo lo recogido en vivo
> (README §9). `stop` y `down` sin `-v` **no** borran datos.

## 2. Un servicio concreto (productor, consumidor, kafka, postgres)

| Quiero… | Comando |
|---|---|
| Parar solo uno | `docker compose stop productor` |
| Arrancar solo uno | `docker compose start productor` |
| Reiniciar uno | `docker compose restart consumidor` |
| Reconstruir y recrear uno (tras cambiar su código) | `docker compose up -d --build consumidor` |
| Reconstruir los dos Python | `docker compose up -d --build consumidor productor` |

## 3. Mirar qué pasa

| Quiero… | Comando |
|---|---|
| Ver el estado (`healthy`, `Up`, `Exited`…) | `docker compose ps -a` |
| Ver el log de un servicio | `docker compose logs consumidor` |
| Ver solo las últimas líneas | `docker compose logs consumidor --tail 20` |
| Seguir el log **en directo** (salir con `Ctrl + C`) | `docker compose logs -f productor consumidor` |
| Ver el estado **incluido el túnel** | `docker compose --profile tunel ps` |
| Ver la URL pública del túnel (en el navegador) | http://localhost:4040 |

## 4. Pruebas y scripts

| Quiero… | Comando |
|---|---|
| Enviar 1 terremoto de prueba | `docker compose run --rm productor-prueba` |
| Enviar los casos de la FAQ 12 + calidad | `docker compose run --rm productor-prueba python -m src.pruebas_faq12` |
| Recalcular el país de los eventos guardados | `docker compose run --rm consumidor python -m src.rellenar_paises` |

> `run --rm` = arranca un contenedor temporal, ejecuta el comando y lo borra al terminar.

## 5. Base de datos (PostgreSQL)

| Quiero… | Comando |
|---|---|
| Abrir la consola SQL (salir con `\q`) | `docker compose exec postgres psql -U observatorio -d observatorio` |
| Listar las tablas | `docker compose exec postgres psql -U observatorio -d observatorio -c "\dt"` |
| Ver las columnas de una tabla | `docker compose exec postgres psql -U observatorio -d observatorio -c "\d evento_actual"` |
| Contar los terremotos reales | `docker compose exec postgres psql -U observatorio -d observatorio -c "SELECT COUNT(*) FROM evento_actual WHERE source = 'usgs-feed-all_day';"` |
| Terremotos por país | `docker compose exec postgres psql -U observatorio -d observatorio -c "SELECT COALESCE(p.nombre_es, 'Sin país asignado') AS pais, COUNT(*) FROM evento_actual e LEFT JOIN pais p ON p.country_id = e.country_id WHERE e.source = 'usgs-feed-all_day' GROUP BY 1 ORDER BY 2 DESC;"` |
| Ver la cuarentena | `docker compose exec postgres psql -U observatorio -d observatorio -c "SELECT tipo, motivo, COUNT(*) FROM cuarentena GROUP BY 1, 2;"` |
| Últimas consultas a USGS | `docker compose exec postgres psql -U observatorio -d observatorio -c "SELECT solicitada_at, http_status, ok, n_eventos, n_publicados FROM consulta_ingesta ORDER BY id DESC LIMIT 5;"` |

## 6. Kafka

| Quiero… | Comando |
|---|---|
| Listar los topics | `docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list` |
| Ver el **LAG** del consumidor (comandas pendientes por partición) | `docker compose exec kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe --group consumidor-observatorio` |
| Leer un topic desde el principio (salir con `Ctrl + C`) | `docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic terremotos.live --from-beginning` |

## 7. Git (al terminar cada punto)

```powershell
git add .
git status          # revisar: NUNCA debe aparecer .env ni data/raw
git commit -m "Mensaje claro de lo que se ha hecho"
git push
```
