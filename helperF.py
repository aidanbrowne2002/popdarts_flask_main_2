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

def convert_player_data(player_data_list):
    player_data = []

    for game in player_data_list:
        game_id, rating = game
        player_data.append({'game_sequence': game_id, 'rating': rating})

    return player_data
def getGraphData(user):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT "Matches".game_id, SUM("PlayerInGame".rr_change) as change FROM "PlayerInGame"
                INNER JOIN
                    "Users" ON "PlayerInGame".player_id = "Users".id
                INNER JOIN
                    "Matches" ON "Matches".game_id = "PlayerInGame".game_id
                WHERE player_id = %s
                GROUP BY "Matches".game_id
                order by game_id"""
    cursor.execute(Query,(user,))
    data = cursor.fetchall()
    data = [list(item) for item in data]  # Convert tuples to lists
    for x in range(1, len(data)):
        data[x][1] = data[x][1] + data[x-1][1]

    data = convert_player_data(data)

    return data
