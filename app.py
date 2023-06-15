from flask import Flask, render_template, request, session, redirect, url_for, Response
import psycopg2, rating, users, helperF as hf, credentials
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash



app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
    all_players_data = hf.newgraphdata()
    return render_template('index.html', parse=rating.getTable(), now=hf.tStamp(), today=rating.getChangeToday(), all_players_data=all_players_data)


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




@app.route('/game')
def game():
    return render_template("games.html", autocompleteData=users.getUsernames())

@app.route('/video')
def video():
    return Response(hf.generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

    """
    - Screen with camera in the middle
    - Top there is the round score board (green and blue) 0 | 0
    - Button at the bottom "start game". Also options to enter player 1 and 2 (has to be a user from the database)
    - When "start game" pressed button changes to "end round"
    - When "end round" is pressed, all the processing for the image is done and the score is calculated
    - Gives option to user (ref) to change scores and closest dart ext.
    - Score board updates until its first to 11 points
    - When first to 11 happens sends off to do all the autofill through the submit result tab
    - Then goes to confirmation table
    - Then either goes back to the game tab or home tab.
    """

    """
    Data that needs to be kept (then put into a database for each game):
    - Points per round (can do average points per round)
    - Who was the closest per round (how many times did that player get the closest)
    - Winner of each round (keep track how many times) / Winner of each game is already recored but can also be kept in this table
    - How many rounds where there in that game
    - Could keep tract of the closest dart in that game (and who did that)
    - How many downs on the table / how many were stuck on the table (do an average for each player / Do this by [dartColour]Total - [dartColour]Up)
    """





#User Login
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


if __name__ == '__main__':
    app.run()
