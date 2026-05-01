#pip install thrift thrift_sasl PyHive
# NOTA: la primera vez será muy lenta la inserción, pero cuando entra en calor es casi inmediata

from pyhive import hive

print("Connecting to Hive...")

conn = hive.Connection(
    host="44.220.169.106",
    port=10000,
    database="gaia"
)

print("Connected to Hive")

cursor = conn.cursor()

cursor.execute("""
show tables
""")

print(cursor.fetchall())

cursor.close()
conn.close()