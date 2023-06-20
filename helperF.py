import datetime, psycopg2, rating
import credentials #database credentials
import users
from werkzeug.security import check_password_hash, generate_password_hash
# CompVision Stuff
import cv2
import os

camera = cv2.VideoCapture(0) # Probs will need to change this from 0 to something else (Global)

def tStamp():
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    return timestamp
def convertFormMatch(form):
    try:
        temp1 = int(form['score1'])
        temp2 = int(form['score2'])

    except ValueError:
        return ("error")
    data = ((form['name1'],int(form['score1'])),(form['name2'],int(form['score2'])))
    return data
def convertFormUser(form):
    data = (form['first_name'], form['last_name'], form['dob'])
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

def newgraphdata():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    user_ids = users.getIDs()  # Example user ids

    all_players_data = {}
    for user_id in user_ids:
        Query = """SELECT "Matches".game_id, SUM("PlayerInGame".rr_change) as change FROM "PlayerInGame"
                            INNER JOIN
                                "Users" ON "PlayerInGame".player_id = "Users".id
                            INNER JOIN
                                "Matches" ON "Matches".game_id = "PlayerInGame".game_id
                            WHERE player_id = %s
                            GROUP BY "Matches".game_id
                            order by game_id"""
        cursor.execute(Query, (user_id,))
        data = cursor.fetchall()
        data = [list(item) for item in data]  # Convert tuples to lists
        for x in range(1, len(data)):
            data[x][1] = data[x][1] + data[x - 1][1]

        player_name = users.getname(user_id)  # Use your function to get the user's name
        all_players_data[player_name] = data  # Store each player's data using their name as the key

    return all_players_data

# Computer Vision Stuff
def generate_frames(capture):
    while True:
        success, frame = camera.read()
        if not success:
            break
        if capture:
            capture=0
            p = os.path.sep.join(['rounds', f"rounds_{get_next_round_number()}.jpg"])
            cv2.imwrite(p, frame)
        try:
            ret, buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') # generates the next frame
        except Exception as e:
            pass

def get_next_round_number():
    saved_files, temp_files = os.listdir('all_rounds'), os.listdir('rounds')
    if saved_files:
        round_numbers = get_files(saved_files)
    else:
        round_numbers = get_files(temp_files)
    if round_numbers:
        return max(round_numbers) + 1
    return 1

def get_files(dir):
    round_numbers = []
    for file in dir:
        round_number = int(file.split('_')[1].split('.')[0])
        round_numbers.append(round_number)
    return round_numbers

def getScoreMA(userID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT p.game_id,
       AVG(p.score)
       OVER(ORDER BY p.game_id ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
       AS avgscore
       FROM "PlayerInGame" p
        WHERE p.player_id = %s;"""
    cursor.execute(Query, (userID,))
    data = cursor.fetchall()
    x = [0]
    y = [0]
    for i in range(0, len(data)):
        x.append(data[i][1])
        y.append(data[i][0])
    for p in range(0, len(x)):
        x[p] = float(x[p])
    x.remove(0)
    y.remove(0)
    data = (x, y)
    return data

def getPreviousGames(userID):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT "PlayerInGame".player_id, "PlayerInGame".score, "PlayerInGame".game_id
    FROM "PlayerInGame"
    WHERE game_id in (SELECT "PlayerInGame".game_id from "PlayerInGame" where player_id = %s order by game_id desc limit 5)
    order by game_id, player_id"""
    cursor.execute(Query, (userID,))
    data = cursor.fetchall()
    print (data)
    games = []
    for x in range (0,5):
        games.append([data[x*2][2],users.getname(data[x*2][0]),data[x*2][1],users.getname(data[x*2+1][0]),data[x*2+1][1]])
    print(games)
    return games