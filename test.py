#pip install thrift thrift_sasl PyHive
# NOTA: la primera vez será muy lenta la inserción, pero cuando entra en calor es casi inmediata

from pyhive import hive

print("Connecting to Hive...")

conn = hive.Connection(
    host="IP_PUBLIC_EC2",
    port=10000,
    database="historicos"
)

print("Connected to Hive")

cursor = conn.cursor()

cursor.execute("""
INSERT INTO eventos VALUES
('3','api2',300,current_timestamp())
""")