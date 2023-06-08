import psycopg2
import credentials #database credentials

def getUsernames(): #Currently f_names
    conn = credentials.conn
    cursor = conn.cursor()
    Query = """SELECT f_name FROM "Users";"""
    cursor.execute(Query)
    data = (cursor.fetchall())
    result = []
    for x in range (0,len(data)):
        result.append(data[x][0])
    return result


def getid(name): #currently f_name
    conn = credentials.conn
    cursor = conn.cursor()
    Query = """SELECT id FROM "Users" where f_name = %s"""
    cursor.execute(Query, (name,))
    return (cursor.fetchone()[0])
