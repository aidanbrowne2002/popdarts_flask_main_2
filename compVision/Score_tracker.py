class Scores:
    def __init__(self):
        self.score_blue   = 0
        self.score_green  = 0

        self.rounds_blue  = 0
        self.rounds_green = 0

    def get_rounds_blue(self):
        return self.rounds_blue

    def get_rounds_green(self):
        return self.rounds_green

    def get_blue(self):
        return self.score_blue

    def get_green(self):
        return self.score_green

    def update_scores(self, blue_points, green_points):
        self.score_blue += blue_points
        self.score_green += green_points

    def update_rounds(self, winner):
        if 'blue' in winner:
            self.rounds_blue += 1
        elif 'green' in winner:
            self.rounds_green += 1
        else:
            print('no team colour given')

    def reset_scores(self):
        self.score_blue = 0
        self.score_green = 0

    def reset_rounds(self):
        self.rounds_blue = 0
        self.rounds_green = 0