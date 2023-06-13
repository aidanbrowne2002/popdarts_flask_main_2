from flask import Flask, render_template, request, session, redirect, url_for, Response
import psycopg2, rating, users, helperF as hf

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def table():
    all_players_data = hf.newgraphdata()
    print (all_players_data)
    return render_template('index.html', parse=rating.getTable(), now=hf.tStamp(), today=rating.getChangeToday(), all_players_data=all_players_data)


@app.route('/match')
def add_match():
    return render_template('addMatch.html', autocompleteData=users.getUsernames())


@app.route('/confirmation', methods=['POST'])
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
def add_user():
    return render_template("addUser.html")

@app.route('/user_confirm', methods=['POST'])
def user_confirm():
    if request.method == 'POST':
        print (request.form)
        results = hf.convertFormUser(request.form)
        print(results)
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


@app.route('/add_user')
def add_user():
    return render_template("addUser.html")

@app.route('/user_confirm', methods=['POST'])
def user_confirm():
    if request.method == 'POST':
        results = hf.convertFormUser(request.form)
        users.addUser(results)
    return render_template("confirm_user.html")


@app.route('/game')
def game():
    return render_template("games.html")

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

if __name__ == '__main__':
    app.run()
