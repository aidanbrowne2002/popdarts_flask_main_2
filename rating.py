import psycopg2
import credentials #database credentials
def getTable():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT f_name, rating FROM "Users" ORDER BY rating desc"""
    cursor.execute(Query)
    return cursor.fetchall()
    conn.commit()
    conn.close()

def getChangeToday():
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT 
    "Users".f_name, 
    "Users".rating, 
    SUM("PlayerInGame".rr_change) as total_change 
FROM 
    "PlayerInGame"
INNER JOIN 
    "Users" ON "PlayerInGame".player_id = "Users".id
INNER JOIN 
    "Matches" ON "Matches".game_id = "PlayerInGame".game_id
WHERE 
    "Matches".occured >= CURRENT_DATE-1
GROUP BY 
    "Users".f_name, "Users".rating
ORDER BY 
    total_change DESC;"""
    cursor.execute(Query)
    return cursor.fetchall()
    conn.commit()
    conn.close()
def get_k_factor(rating_difference, is_winner):
    if is_winner:
        if rating_difference > 200:
            return 10
        elif rating_difference > 100:
            return 20
        elif rating_difference > 50:
            return 30
        else:
            return 40
    else:
        if rating_difference < 50:
            return 40
        elif rating_difference < 100:
            return 30
        elif rating_difference < 200:
            return 20
        else:
            return 15

def get_min_loss(rating_difference):
    if rating_difference < 50:
        return -10
    elif rating_difference < 100:
        return -8
    elif rating_difference < 200:
        return -6
    else:
        return -4

def changerr(data):
    player1_rank = data[0][2]
    player2_rank = data[1][2]

    rank_difference = abs(player1_rank - player2_rank)

    is_winner_player1 = data[0][1] > data[1][1]
    is_winner_player2 = not is_winner_player1

    k_factor_player1 = get_k_factor(rank_difference, is_winner_player1)
    k_factor_player2 = get_k_factor(rank_difference, is_winner_player2)

    total_score = data[0][1] + data[1][1]
    actualscore1 = data[0][1] / total_score
    actualscore2 = data[1][1] / total_score

    expectedscore1 = 1 / (1 + 10 ** ((player2_rank - player1_rank) / 400))
    changeinrank1 = k_factor_player1 * (actualscore1 - expectedscore1)
    min_loss1 = get_min_loss(rank_difference)
    changeinrank1 = max(2, changeinrank1) if is_winner_player1 else min(min_loss1, changeinrank1)

    expectedscore2 = 1 / (1 + 10 ** ((player1_rank - player2_rank) / 400))
    changeinrank2 = k_factor_player2 * (actualscore2 - expectedscore2)
    min_loss2 = get_min_loss(rank_difference)
    changeinrank2 = max(2, changeinrank2) if is_winner_player2 else min(min_loss2, changeinrank2)

    print(changeinrank1, changeinrank2)
    return (changeinrank1, changeinrank2)

def getRank(id):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT rating FROM "Users" WHERE id = %s;"""
    cursor.execute(Query,(id,))
    return cursor.fetchone()[0]

def addMatch(results):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    place = ("10 Shirley Road")
    if results[0][1]>results[1][1]:
        result = 0
    else:
        result = 1
    Query = """ INSERT INTO "Matches" (place, result) VALUES (%s,%s) RETURNING game_id"""
    data = (place, result)
    cursor.execute(Query, data)
    gameid = cursor.fetchone()[0]
    for player in range(0,2):
        Query = """ INSERT INTO "PlayerInGame" (game_id, player_id, home_away, score, rr_change) VALUES (%s,%s,%s,%s,%s)"""
        data = (gameid,results[player][0],player,results[player][1],results[player][3])
        cursor.execute(Query, data)
        Query = """update "Users" set rating = rating + %s where id = %s"""
        data = (results[player][3], results[player][0])
        cursor.execute(Query, data)
    conn.commit()
    return gameid
def getRRChange(user):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT "PlayerInGame".rr_change, "Matches".game_id FROM "PlayerInGame"
            inner join "Users" on "Users".id = "PlayerInGame".player_id
            inner join "Matches" on "Matches".game_id = "PlayerInGame".game_id
            where "Users".id = %s;"""
    cursor.execute(Query, (user,))
    data = cursor.fetchall()
    x=[0]
    y=[0]
    for i in range (0, len(data)):
        x.append(data[i][1])
        y.append(y[i]+data[i][0])
    data = (x,y)
    return data