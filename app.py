from flask import Flask, render_template, request, session, redirect, url_for, Response
import psycopg2, rating, users, helperF as hf, credentials
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash

import os

app = Flask(__name__)
app.secret_key = credentials.secretkey

login_manager = LoginManager()
login_manager.init_app(app)

# Create a user class with UserMixin
class User(UserMixin):
    def __init__(self, id, name=None, username=None, password=None):
        self.id = id
        self.name = name
        self.username = username
        self.password = password
        self.rating = rating
        if name is None and username is None:
            self.get_user_details()

    def get_user_details(self):
        conn = psycopg2.connect(database=credentials.database, user=credentials.user, password=credentials.password, host=credentials.host, port=credentials.port)
        cur = conn.cursor()
        cur.execute("""SELECT id, f_name, username, hashed_pass, rating from "Users" WHERE id = %s""", (self.id,))
        result = cur.fetchone()
        conn.close()
        if result:
            self.id, self.name, self.username, self.password, self.rating = result

    @staticmethod
    def getIdFromUsername(username):
        conn = psycopg2.connect(database=credentials.database, user=credentials.user, password=credentials.password,
                                host=credentials.host, port=credentials.port)
        cursor = conn.cursor()
        cursor.execute("""SELECT id FROM "Users" WHERE username = %s""", (username,))
        result = cursor.fetchone()
        conn.close()
        if result is not None:
            return result[0]
        else:
            return None

@login_manager.user_loader
def load_user(user_id):
    user = User(user_id)
    user.get_user_details()
    return user

@app.context_processor
def utility_processor():
    def userChange():
        return rating.getchangetodaysingle(current_user.id)
    return dict(userChange=userChange)

@app.route('/')
def table():
    # hf.camera_off()
    all_players_data = hf.newgraphdata()
    return render_template('index.html', parse=rating.getTable(), now=hf.tStamp(), today = rating.getChangeToday(), all_players_data=all_players_data)


@app.route('/match')
@login_required
def add_match():
    return render_template('addMatch.html', autocompleteData=users.getUsernames())


@app.route('/confirmation', methods=['POST'])
@login_required
def confirmation():
    if request.method == 'POST':
        result = request.form
        result = hf.convertFormMatch(result)
        if result == 'error':
            return ("Incorrect score format, go back and try again")
        session['result'] = result
        if result[0][1] > result[1][1]:
            winner = result[0][0]
        else:
            winner = result[1][0]
        return render_template("confirmation.html", result=session['result'], winner=winner)


@app.route('/submitted', methods=['POST'])
@login_required
def submit_results():
    result = session.get('result', None)
    if result is not None:
        result = hf.convertResult(result)
        rrchange = rating.changerr(result)
        result[0].append(rrchange[0])
        result[1].append(rrchange[1])
        print(result)
        rating.addMatch(result)
        return render_template("submit.html", result=result)  # confirmation of commit
    else:
        return "No data to commit", 400

@app.route('/add_user')
@login_required
def add_user():
    return render_template("addUser.html")

@app.route('/user_confirm', methods=['POST'])
@login_required
def user_confirm():
    if request.method == 'POST':
        results = hf.convertFormUser(request.form)
        users.addUser(results)
    return render_template("confirm_user.html")

@app.route('/graph')
def graph():
    data = rating.getRRChange(str(11))
    return render_template("graphs.html", xdata = data[0], ydata = data[1], min = min(data[1]), max = max(data[1]))


@app.route('/graphbig')
def graph2():
    # List of user ids you want to plot
    all_players_data = hf.newgraphdata()
    return render_template('graphs2.html', all_players_data=all_players_data)

# ComputerVision Stuff
@app.route('/game')
def game():
    global capture
    capture = 0

    all_players_data = hf.newgraphdata()
    hf.create_class()
    data, names = hf.preivous_game()
    return render_template("game_start.html", autocompleteData=users.getUsernames(),last_game=data, last_name=names, all_players_data=all_players_data)

@app.route('/rounds',methods=['GET', 'POST'])
def rounds():
    if request.method == 'POST':
        name1,name2 = request.form.get('name1'), request.form.get('name2')
        if request.form.get('click') == 'End Round': # Capture image
            global capture
            capture=1

        elif request.form.get('complete_round') == 'Submit':
            closest = request.form.get('winning_dart') # For future data capture (also need all down darts)
            team_blue,team_green = request.form.get('blue_s'), request.form.get('green_s')
            hf.update_scores(int(team_blue), int(team_green))

            end_match = hf.check_score()
            if end_match:
                print(end_match)
                return redirect('/match')

        # Either its from game_start or after image is captured from previous round
        print(hf.get_team('blue'),hf.get_team('green'))
        return render_template('rounds.html',player_blue=name1,player_green=name2,g_score=str(hf.get_team('green')),b_score=str(hf.get_team('blue')),g_rounds=str(hf.get_round('green')),b_rounds=str(hf.get_round('blue')))
    return render_template('rounds.html') # Should turn this into a some error page

@app.route('/procces',methods=['POST'])
def processing():
    if request.method == 'POST':
        name1,name2 = request.form.get('name1'), request.form.get('name2')
        session['name1'], session['name2'] = name1, name2
        if request.form.get('next') == 'Next Round':
            round_image = hf.last_image()
            team, closest = hf.logic(round_image)
            session['team'], session['closest'] = team, closest
    return redirect('/score_confirm')

@app.route('/score_confirm',methods=['GET','POST'])
def score_confirm():
    name1, name2 = session.get('name1', None), session.get('name2', None)
    team, closest = session.get('team', None), session.get('closest', None)
    return render_template('confirm_score.html',player_blue=name1,player_green=name2,teams=team,winner_dart=closest)

@app.route('/video')
def video():
    return Response(hf.generate_frames(capture),mimetype='multipart/x-mixed-replace; boundary=frame')

# User Login
# User Login
# Example usage
# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_id = users.getIdFromUsername(username)
        if user_id is None:  # username not found in DB
            return 'Bad login'
        user = User(user_id)
        if check_password_hash(user.password, password):  # valid user found in DB
            login_user(user)
            return redirect(url_for('protected'))
        else:
            return 'Bad login'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/protected')
@login_required
def protected():
    return redirect('/')


@app.route('/profile/<user>')
@login_required
def profile(user):

    gamedata = hf.getPreviousGames(current_user.id)

    scoreMA = hf.getScoreMA(current_user.id)

    return render_template("profile.html", ydata = scoreMA[0], xdata = scoreMA[1], min = min(scoreMA[0]), max = max(scoreMA[0])+1, game_data = gamedata)


if __name__ == '__main__':
    app.run()
