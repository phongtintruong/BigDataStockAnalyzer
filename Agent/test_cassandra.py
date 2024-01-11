from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory

cluster = Cluster(contact_points=['localhost'], port=9042, auth_provider=PlainTextAuthProvider(username='cassandra', password='cassandra'))
session = cluster.connect()
session.execute("CREATE KEYSPACE IF NOT EXISTS test WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")
session.execute("CREATE TABLE IF NOT EXISTS test.info (id UUID PRIMARY KEY, name TEXT, age INT);")
session.execute("INSERT INTO test.info(id, name, age) VALUES (uuid(), 'John', 25)")
result = session.execute("SELECT * FROM test.info")

for row in result:
    print(row)

cluster.shutdown()

print('Complete')
