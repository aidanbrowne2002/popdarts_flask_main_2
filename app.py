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



if __name__ == '__main__':
    app.run()
