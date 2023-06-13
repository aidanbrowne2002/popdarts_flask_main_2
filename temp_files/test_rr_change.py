id_1 = 7
id_2 = 3

score_1 = 0
score_2 = 3

rating_1 = 720
rating_2 = 400

data = [[id_1, score_1, rating_1],[id_2, score_2, rating_2]]


#Helper functions

def change_rr(data):
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


print (change_rr(data))