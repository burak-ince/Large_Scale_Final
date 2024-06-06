import os
import psycopg2

server = 'finaldatabase.postgres.database.azure.com'
database = 'postgres'
username = 'adminlogin'
password = 'Aa123456'

def conn():
    try:
        cnx = psycopg2.connect(user=username, password=password, host=server, port=5432, database=database)
        return cnx

    except psycopg2.Error as ex:
        sqlstate = ex.args[1]
        return f"Error connecting to the database. SQLState: {sqlstate}"