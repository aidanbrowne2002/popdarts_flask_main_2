import datetime, psycopg2, rating
import credentials #database credentials
import users
from werkzeug.security import check_password_hash, generate_password_hash
# CompVision Stuff
import cv2, os
from compVision import helper as hp, warp_img as wImg, round_score as rs, score_tracker as st


def connect_database():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    return cursor

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
    cursor = connect_database()
    for x in range (0,2):
        cursor.execute(Query,(data[x][0],))
        data[x][0] = (cursor.fetchone()[0]) # str((cursor.fetchone()[0]))

        data[x].append(rating.getRank(data[x][0]))
    return data

def convert_player_data(player_data_list):
    player_data = []

    for game in player_data_list:
        match_id, rating = game
        player_data.append({'game_sequence': match_id, 'rating': rating})

    return player_data
def getGraphData(user):
    cursor = connect_database()
    Query = """SELECT "Matches".match_id, SUM("PlayerInGame".rr_change) as change FROM "PlayerInGame"
                INNER JOIN
                    "Users" ON "PlayerInGame".player_id = "Users".id
                INNER JOIN
                    "Matches" ON "Matches".match_id = "PlayerInGame".match_id
                WHERE player_id = %s
                GROUP BY "Matches".match_id
                order by match_id"""
    cursor.execute(Query,(user,))
    data = cursor.fetchall()
    data = [list(item) for item in data]  # Convert tuples to lists
    for x in range(1, len(data)):
        data[x][1] = data[x][1] + data[x-1][1]

    data = convert_player_data(data)

    return data

def newgraphdata():
    cursor = connect_database()
    user_ids = users.getIDs()  # Example user ids

    all_players_data = {}
    for user_id in user_ids:
        Query = """SELECT "Matches".match_id, SUM("PlayerInGame".rr_change) as change FROM "PlayerInGame"
                            INNER JOIN
                                "Users" ON "PlayerInGame".player_id = "Users".id
                            INNER JOIN
                                "Matches" ON "Matches".match_id = "PlayerInGame".match_id
                            WHERE player_id = %s
                            AND complete = true
                            GROUP BY "Matches".match_id
                            order by match_id"""
        cursor.execute(Query, (user_id,))
        data = cursor.fetchall()
        data = [list(item) for item in data]  # Convert tuples to lists
        for x in range(1, len(data)):
            data[x][1] = data[x][1] + data[x - 1][1]

        player_name = users.getname(user_id)  # Use your function to get the user's name
        all_players_data[player_name] = data  # Store each player's data using their name as the key

    return all_players_data

def preivous_game():
    cursor = connect_database()
    query_game = """ SELECT DISTINCT pg.match_id, r.round_id, r.home_score, r.away_score, r.home_closer, r.away_closer FROM "Matches" AS ms
                        INNER JOIN "Games" as ga ON ga.match_id = ms.match_id
                        INNER JOIN "Rounds" as r ON r.game_id = ga.game_id
                        INNER JOIN "PlayerInGame" as pg ON pg.match_id = ms.match_id
                        INNER JOIN "Users" as u ON u.id = pg.player_id
                        WHERE ms.complete = true
                        AND pg.match_id = (
                            SELECT MAX(pg.match_id)
                            FROM "PlayerInGame" AS pg
                            JOIN "Matches" AS ms ON pg.match_id = ms.match_id
                            WHERE ms.complete = true)
                        ORDER BY r.round_id ASC;"""
    query_name = """SELECT pg.match_id, u.f_name, ms.complete FROM "PlayerInGame" as pg
                        INNER JOIN "Matches" AS ms ON pg.match_id = ms.match_id
                        INNER JOIN "Users" as u ON u.id = pg.player_id
                        WHERE ms.complete = true
                        AND pg.match_id = (
                            SELECT MAX(pg.match_id)
                            FROM "PlayerInGame" AS pg
                            JOIN "Matches" AS ms ON pg.match_id = ms.match_id
                            WHERE ms.complete = true)
                        ORDER BY pg.match_id DESC;"""

    cursor.execute(query_game)
    game_data = cursor.fetchall()
    game_data = [list(item) for item in game_data]

    cursor.execute(query_name)
    name_data = cursor.fetchall()
    name_data = [list(item) for item in name_data]
    return game_data, name_data

# Computer Vision Stuff
def create_class():
    global scores
    scores = st.Scores()

def update_scores(b,g):
    print(b,g)
    scores.update_scores(b, g)

def get_team(colour):
    if colour == 'blue':
        return scores.get_blue()
    elif colour == 'green':
        return scores.get_green()
    else:
        print('incorrect team')

def get_round(colour):
    if colour == 'blue':
        return scores.get_rounds_blue()
    elif colour == 'green':
        return scores.get_rounds_green()
    else:
        print('incorrect team')

def check_score():
    if scores.get_blue() >= 11 and scores.get_blue() > scores.get_green(): # game won b
        scores.update_rounds('blue')
        scores.reset_scores()
    elif scores.get_green() >= 11 and scores.get_green() > scores.get_blue(): # game won g
        scores.update_rounds('green')
        scores.reset_scores()

    if scores.get_rounds_blue() == 3:
        #scores.reset_rounds()
        return 'match won blue'
    elif scores.get_rounds_green() == 3:
        #scores.reset_rounds()
        return 'match won green'
    return None

def camera_on():
    camera_found = False
    global camera
    for camera_index in range(10):  # Try camera indexes 0 to 9
        camera = cv2.VideoCapture(camera_index)
        if camera.isOpened():
            print("on")
            camera_found = True
            break

    if not camera_found:
        print("set 0 - No camera found.")

def camera_off():
    camera.release()

def generate_frames(capture):
    while True:
        success, frame = camera.read()
        if not success:
            break
        if capture:
            print("PICTURE TAKEN")
            capture=0
            p = os.path.sep.join(['compVision/rounds', f"rounds_{get_next_round_number()}.jpg"])
            cv2.imwrite(p, frame)
        try:
            ret, buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') # generates the next frame
        except Exception as e:
            pass

def logic(r_image):
    # wImg.unwarp_img('compVision/round_image') # Toggle
    labels, boxes, scores = hp.load_model(r_image) # Will need to find a way to get latest image
    center_darts, labels, boxes, scores = hp.clean_data(labels, boxes, scores)
    # print(boxes)
    # print(center_darts)
    closest, team = rs.dart_system(labels, center_darts)
    return team, closest

def last_image():
    files = os.listdir('compVision/rounds')
    image_files = [file for file in files if file.startswith('rounds_') and file.endswith('.jpg')]
    sorted_files = sorted(image_files)
    if sorted_files:
        last_image = sorted_files[-1]
        return last_image
    else:
        print("No image")

def get_next_round_number():
    saved_files, temp_files = os.listdir('compVision/all_rounds'), os.listdir('compVision/rounds')
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
    cursor = connect_database()
    Query = """SELECT p.match_id,
       AVG(p.score)
       OVER(ORDER BY p.match_id ROWS BETWEEN 4 PRECEDING AND CURRENT ROW)
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
    Query = """SELECT "PlayerInGame".player_id, "PlayerInGame".score, "PlayerInGame".match_id
    FROM "PlayerInGame"
    WHERE match_id in (SELECT "PlayerInGame".match_id from "PlayerInGame" where player_id = %s order by match_id desc limit 5)
    order by match_id, player_id"""
    cursor.execute(Query, (userID,))
    data = cursor.fetchall()
    print (data)
    games = []
    for x in range (0,5):
        games.append([data[x*2][2],users.getname(data[x*2][0]),data[x*2][1],users.getname(data[x*2+1][0]),data[x*2+1][1]])
    print(games)
    return games