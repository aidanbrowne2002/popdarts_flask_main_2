import warp_img as wImg, helper as hp, round_score as rs
from detecto import visualize

def main():
    # table = wImg.unwarp_img('Game_Img/test') # Toggle
    labels, boxes, scores, image = hp.load_model('image') # Will need to find a way to get latest image
    center_darts, labels, boxes, scores = rs.clean_data(labels, boxes, scores)
    # print(boxes)
    # print(center_darts)

    distance = rs.find_closest(labels, center_darts)
    # visualize.show_labeled_image(image, boxes, distance)
    closest, dart_score = rs.point_count(labels, distance)
    # hp.plot_center(center_darts, image)
    rs.recalabrate(closest, dart_score)

# Notes:
# python labelImg.py -- Labeling Software
# Noted that how I labelled the target as a whole not the top part. Causes issue which popdart is the closes. v2 of the labelled images has target labelled differently
# Note that (atm with the camera that is fish eyed) the image fish eyed lens hasn't been removed. This affects on games that are really close in the corder of the table
# Place this main file in app.py!!!!!!!!!!!