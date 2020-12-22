import psycopg2
import config

def connect():
    connection = psycopg2.connect(
        user=config.user,
        password=config.password,
        host=config.host,
        port=config.port,
        database=config.database)
    cursor = connection.cursor()
    return connection, cursor