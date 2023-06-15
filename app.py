from flask import Flask, render_template, request, session, redirect, url_for, Response
import psycopg2, rating, users, helperF as hf
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#make shots directory to save pics
try:
    os.mkdir('./rounds')
    os.mkdir('./all_rounds')
except OSError as error:
    pass

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
    return render_template("game_start.html", autocompleteData=users.getUsernames())

@app.route('/rounds', methods=['POST'])
def rounds():
    if request.method == 'POST': # Maybe another if statment
        form = request.form
        result = (form['name1'],form['team1']),(form['name2'],form['team2'])
        print(result)

        # if request.form.get('click') == 'End Round':
        #     global capture
        #     capture=1

    return render_template('rounds.html')

@app.route('/video')
def video():
    return Response(hf.generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()
