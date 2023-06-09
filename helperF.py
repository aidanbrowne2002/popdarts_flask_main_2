import datetime, psycopg2, rating
import credentials #database credentials

def tStamp():
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    return timestamp
def convertForm(form):
    data = ((form['name1'],int(form['score1'])),(form['name2'],int(form['score2'])))
    return data
def convertResult(result):
    data = [list(item) for item in result]

    Query = """SELECT id FROM "Users" WHERE f_name = %s"""
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    for x in range (0,2):
        cursor.execute(Query,(data[x][0],))
        data[x][0] = (cursor.fetchone()[0])#str((cursor.fetchone()[0]))

        data[x].append(rating.getRank(data[x][0]))
    return data

