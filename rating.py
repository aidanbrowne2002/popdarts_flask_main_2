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
    "Matches" ON "Matches".match_id = "PlayerInGame".match_id
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

def getchangetodaysingle(id):
    conn = psycopg2.connect(database=credentials.database,
                            host=credentials.host,
                            user=credentials.user,
                            password=credentials.password,
                            port=credentials.port)
    cursor = conn.cursor()
    Query = """SELECT
    "Users".id,
    SUM("PlayerInGame".rr_change) as total_change
FROM
    "PlayerInGame"
INNER JOIN
    "Users" ON "PlayerInGame".player_id = "Users".id
INNER JOIN
    "Matches" ON "Matches".match_id = "PlayerInGame".match_id
WHERE
    "Matches".occured >= CURRENT_DATE-1 and "Users".id = %s
GROUP BY
    "Users".id
ORDER BY
    total_change DESC;"""
    cursor.execute(Query,(id,))
    try:
        return cursor.fetchone()[1]
    except:
        return 0
    conn.commit()
    conn.close()


def changerr(data):
    user_id1, score1, current_rating1 = data[0]
    user_id2, score2, current_rating2 = data[1]

    # Determine who won and the score difference
    if score1 > score2:
        winner = 1
        score_diff = score1 - score2
    elif score2 > score1:
        winner = 2
        score_diff = score2 - score1
    else:
        # If it's a draw, return 0 changes
        return (0, 0)

    # Base change in rating, proportional to score difference with a minimum of 10
    base_change = max(score_diff * 10, 10)

    # Calculate bonus based on rating difference
    if winner == 1:
        bonus = max((current_rating2 - current_rating1) / 10, 0)
        changeinrank1 = base_change + bonus
        changeinrank2 = -base_change - bonus
    else:
        bonus = max((current_rating1 - current_rating2) / 10, 0)
        changeinrank1 = -base_change - bonus
        changeinrank2 = base_change + bonus

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
    Query = """ INSERT INTO "Matches" (place, result) VALUES (%s,%s) RETURNING match_id"""
    data = (place, result)
    cursor.execute(Query, data)
    gameid = cursor.fetchone()[0]
    for player in range(0,2):
        Query = """ INSERT INTO "PlayerInGame" (match_id, player_id, home_away, score, rr_change) VALUES (%s,%s,%s,%s,%s)"""
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
    Query = """SELECT "PlayerInGame".rr_change, "Matches".match_id FROM "PlayerInGame"
            inner join "Users" on "Users".id = "PlayerInGame".player_id
            inner join "Matches" on "Matches".match_id = "PlayerInGame".match_id
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