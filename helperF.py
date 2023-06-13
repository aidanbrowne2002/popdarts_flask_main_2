import datetime, psycopg2, rating
import credentials # database credentials
# CompVision Stuff
import cv2

def tStamp():
    timestamp = datetime.datetime.now()
    timestamp = timestamp.strftime("%m/%d/%Y, %H:%M:%S")
    return timestamp
def convertFormMatch(form):
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

def generate_frames():
    camera = cv2.VideoCapture(0) # Probs will need to change this from 0 to something else
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
        yield(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')