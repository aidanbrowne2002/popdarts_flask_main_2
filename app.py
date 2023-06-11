from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2, rating, users, helperF as hf

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def table():
    return render_template('index.html', parse=rating.getTable(), now=hf.tStamp(), today=rating.getChangeToday())


@app.route('/match')
def add_match():
    return render_template('addMatch.html', autocompleteData=users.getUsernames())


@app.route('/confirmation', methods=['POST'])
def confirmation():
    if request.method == 'POST':
        result = request.form
        result = hf.convertForm(result)
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

@app.route('/game')
def game():
    print("Filler")
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

if __name__ == '__main__':
    app.run()
