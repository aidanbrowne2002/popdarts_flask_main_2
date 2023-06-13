import psycopg2
import credentials #database credentials

def getUsernames(): #Currently f_names
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT f_name FROM "Users";"""
    cursor.execute(Query)
    data = (cursor.fetchall())
    result = []
    for x in range (0,len(data)):
        result.append(data[x][0])
    return result

def getIDs():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT id FROM "Users";"""
    cursor.execute(Query)
    data = (cursor.fetchall())
    result = []
    for x in range(0, len(data)):
        result.append(data[x][0])
    return result

def getid(name): #currently f_name
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT id FROM "Users" where f_name = %s"""
    cursor.execute(Query, (name,))
    return (cursor.fetchone()[0])
def addUser(data):
    print(data)
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """INSERT INTO "Users"(F_NAME, L_NAME, DOB) VALUES (%s,%s,%s);"""
    cursor.execute(Query, data)
    conn.commit()
    return


def getname(id): #currently f_name
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT f_name FROM "Users" where id = %s"""
    cursor.execute(Query, (id,))
    return (cursor.fetchone()[0])