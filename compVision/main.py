import warp_img as wImg, helper as hp, round_score as rs

def main():
    # wImg.unwarp_img('compVision/round_image') # Toggle
    labels, boxes, scores, image = hp.load_model('image_2') # Will need to find a way to get latest image

    center_darts, labels, boxes, scores = hp.clean_data(labels, boxes, scores)
    # print(boxes)
    # print(center_darts)

    closest, team, all_darts = rs.dart_system(labels, center_darts)
if __name__ == '__main__':
    main()

# Notes:
# python labelImg.py -- Labeling Software
# Noted that how I labelled the target as a whole not the top part. Causes issue which popdart is the closes. v2 of the labelled images has target labelled differently
# Note that (atm with the camera that is fish eyed) the image fish eyed lens hasn't been removed. This affects on games that are really close in the corder of the table
# Place this main file in app.py!!!!!!!!!!!