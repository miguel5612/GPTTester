import psycopg2
conn = psycopg2.connect(
    dbname="testdb",
    user="postgres",
    password="@bcd1234.*",
    host="localhost",
    port="5432"
)
print("¡Conexión exitosa!")
conn.close()
