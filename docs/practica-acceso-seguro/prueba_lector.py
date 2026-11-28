# Pedimos la contraseña sin mostrarla en pantalla
import getpass
# Librería para hablar con PostgreSQL
import psycopg

# Contraseña del usuario "lector" (la que inventaste en el paso 11)
password = getpass.getpass("Contraseña de lector: ")

# Conectamos como "lector" por el túnel; autocommit para que cada sentencia sea independiente
with psycopg.connect(
    host="127.0.0.1",       # nuestro PC: entrada del túnel
    port=5433,              # puerto local del túnel
    dbname="observatorio",  # base de datos
    user="lector",          # usuario de solo lectura
    password=password,      # su contraseña
    autocommit=True,        # evita que un error bloquee las pruebas siguientes
) as conn:
    # Abrimos un cursor para lanzar consultas
    cur = conn.cursor()

    # Prueba 1: LEER debe funcionar
    cur.execute("SELECT * FROM prueba_eventos;")
    # Mostramos las filas obtenidas
    print("LEER ->", cur.fetchall())

    # Prueba 2: INSERTAR debe fallar
    try:
        cur.execute("INSERT INTO prueba_eventos (source, place) VALUES ('x', 'x');")
        print("INSERTAR -> ¡FUNCIONÓ! (esto sería un problema de seguridad)")
    except psycopg.Error as e:
        # Si falla, mostramos el motivo que da PostgreSQL
        print("INSERTAR -> bloqueado:", e)

    # Prueba 3: BORRAR LA TABLA debe fallar
    try:
        cur.execute("DROP TABLE prueba_eventos;")
        print("DROP -> ¡FUNCIONÓ! (esto sería un problema de seguridad)")
    except psycopg.Error as e:
        print("DROP -> bloqueado:", e)
        
    # Prueba 4: nos quitamos el modo solo lectura de la sesión e intentamos insertar otra vez
    try:
        # El usuario puede desactivar el modo solo lectura de SU sesión
        cur.execute("SET default_transaction_read_only = off;")
        # Ahora solo le frena que no tiene permiso de INSERT
        cur.execute("INSERT INTO prueba_eventos (source, place) VALUES ('x', 'x');")
        print("INSERTAR sin modo solo lectura -> ¡FUNCIONÓ! (problema de seguridad)")
    except psycopg.Error as e:
        print("INSERTAR sin modo solo lectura -> bloqueado:", e)