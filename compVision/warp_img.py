import numpy as np
import cv2
import os

def get_board(img):
    corner_points = [[77,28],[1079,12],[82,695],[1086,687]]

    width, height = int(1130), int(700)
    pts1 = np.float32(corner_points)
    pts2 = np.float32([[0,0],[width,0],[0,height],[width,height]])

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    warp = cv2.warpPerspective(img, matrix, (width, height))

    # print(pts1)
    # for x in range(4):
    #     cv2.circle(image,(pts1[x][0],pts1[x][1]),5,(0, 0, 255),cv2.FILLED)
    return warp

def unwarp_img(dir):
    for files in os.listdir(f'{dir}'):
        image = cv2.imread(f'{dir}/{files}')
        if image is not None: # Display the image
            img_board = get_board(image)
            # cv2.imshow('Image', image)
            # cv2.imshow('Unwarp',img_board)
            # cv2.waitKey(0)  # Wait until a key is pressed
            # cv2.destroyAllWindows()
            cv2.imwrite(f'{dir}/{files}',img_board)
        else:
            print("no image")