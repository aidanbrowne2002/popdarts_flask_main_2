class Scores:
    def __init__(self):
        self.score_blue = 0
        self.score_green = 0

    def get_blue(self):
        return self.score_blue

    def get_green(self):
        return self.score_green

    def update_scores(self, blue_points, green_points):
        self.score_blue += blue_points
        self.score_green += green_points

    def reset_scores(self):
        self.score_blue = 0
        self.score_green = 0