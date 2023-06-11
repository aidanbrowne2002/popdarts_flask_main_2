import round_score as rs
import warp_img as wImg
from detecto import visualize
import helper as hp

def main():
    # wImg.unwarp_img('Game_Img/test') # Toggle
    labels, boxes, scores, image = hp.load_model('image') # Will need to find a way to get latest image
    center_darts, labels, boxes, scores = rs.clean_data(labels, boxes, scores)
    # print(boxes)
    # print(center_darts)

    distance = rs.find_closest(labels, center_darts)
    # visualize.show_labeled_image(image, boxes, distance)
    closest, dart_score = rs.point_count(labels, distance)
    # hp.plot_center(center_darts, image)
    rs.recalabrate(closest, dart_score)

if __name__ == '__main__':
    main()

# Notes:
# python labelImg.py -- Labeling Software
# Noted that how I labelled the target as a whole not the top part. Causes issue which popdart is the closes. v2 of the labelled images has target labelled differently
# Note that (atm with the camera that is fish eyed) the image fish eyed lens hasn't been removed. This affects on games that are really close in the corder of the table