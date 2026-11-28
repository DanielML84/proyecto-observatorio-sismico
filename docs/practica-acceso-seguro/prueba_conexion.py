# Importamos getpass para pedir la contraseña sin mostrarla en pantalla
import getpass
# Importamos psycopg, la librería que habla con PostgreSQL
import psycopg

# Pedimos la contraseña al ejecutar, así no queda escrita en el código
password = getpass.getpass("Contraseña de PostgreSQL: ")

# Abrimos la conexión; "with" la cierra solo al terminar
with psycopg.connect(
    host="127.0.0.1",      # nuestro PC: la entrada del túnel SSH
    port=5433,             # el puerto local que abrimos con -L
    dbname="observatorio", # la base que creamos en el contenedor
    user="postgres",       # usuario de prueba (luego usaremos uno de solo lectura)
    password=password,     # la contraseña que tecleaste
) as conn:
    # Un cursor es el "mando" con el que lanzamos consultas
    with conn.cursor() as cur:
        # Preguntamos a la base qué versión es
        cur.execute("SELECT version();")
        # Mostramos la primera columna de la primera fila
        print(cur.fetchone()[0])