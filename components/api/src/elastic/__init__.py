from elasticsearch_dsl import async_connections

async_connections.create_connection(hosts=["http://wegwijs-elasticsearch:9200"])
es = async_connections.get_connection()
