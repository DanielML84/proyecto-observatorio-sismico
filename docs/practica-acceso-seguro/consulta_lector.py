# Pedimos la contraseña sin mostrarla en pantalla
import getpass
# Librería para hablar con PostgreSQL
import psycopg

# Contraseña del usuario "lector"
password = getpass.getpass("Contraseña de lector: ")

# Conectamos como "lector" por el túnel SSH
with psycopg.connect(
    host="127.0.0.1",       # nuestro PC: entrada del túnel
    port=5433,              # puerto local del túnel
    dbname="observatorio",  # base de datos del bastión
    user="lector",          # usuario de solo lectura
    password=password,      # su contraseña
    autocommit=True,        # cada sentencia es independiente
) as conn:
    # Abrimos un cursor para lanzar consultas
    cur = conn.cursor()

    # Prueba 1: contar los eventos actuales (debe salir 23772)
    cur.execute("SELECT count(*) FROM evento_actual;")
    print("Eventos actuales:", cur.fetchone()[0])

    # Prueba 2: ver 3 filas reales para comprobar que hay datos
    cur.execute("SELECT * FROM evento_actual LIMIT 3;")
    for fila in cur.fetchall():
        print(fila)

    # Prueba 3: intentar borrar datos reales (debe fallar)
    try:
        cur.execute("DELETE FROM evento_actual;")
        print("DELETE -> ¡FUNCIONÓ! (problema grave de seguridad)")
    except psycopg.Error as e:
        print("DELETE -> bloqueado:", e)