# Chuleta de comandos · Observatorio sísmico

> Todos se ejecutan en PowerShell **dentro de la carpeta del proyecto**:
> `cd C:\Users\Usuario\Desktop\proyecto-observatorio-sismico`
> Usuario y BD de PostgreSQL: los de tu `.env` (por defecto `observatorio`).

---

## 1. Arrancar y parar

| Quiero… | Comando | ¿Pierdo datos? |
|---|---|---|
| Arrancar **todo** | `docker compose up -d` | No |
| Arrancar todo **reconstruyendo** la imagen (tras cambiar código o `requirements.txt`) | `docker compose up -d --build` | No |
| **Parar** todo (los contenedores se quedan creados) | `docker compose stop` | No |
| Volver a arrancar lo parado | `docker compose start` | No |
| **Apagar y borrar** los contenedores (los volúmenes se conservan) | `docker compose down` | No |
| ⚠️ **Borrarlo TODO, también los datos** (Kafka y PostgreSQL desde cero) | `docker compose down -v` | ⚠️ **SÍ** |

> Usa `down -v` **solo** si quieres empezar de cero, por ejemplo tras cambiar `sql/01_esquema.sql`.

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
| Leer un topic desde el principio (salir con `Ctrl + C`) | `docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic terremotos.live --from-beginning` |

## 7. Git (al terminar cada punto)

```powershell
git add .
git status          # revisar: NUNCA debe aparecer .env ni data/raw
git commit -m "Mensaje claro de lo que se ha hecho"
git push
```
