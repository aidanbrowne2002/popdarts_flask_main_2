from detecto import visualize
import torch
import math

def clean_data(labels, boxes, scores):
    new_labels, new_boxes, new_scores = [], [], []

    for index in range(len(scores)): # Remove labels that its not confident
        if scores[index] >= 0.9:
            new_labels.append(labels[index])
            new_boxes.append(boxes[index])
            new_scores.append(scores[index])

    new_boxes, new_scores = torch.stack(new_boxes), torch.stack(new_scores) # Merge Items to one tensor
    # print(new_labels, '\n',new_boxes, '\n',new_scores)
    # visualize.show_labeled_image(image, new_boxes, new_labels)

    float_boxes = new_boxes.float()
    center_darts = [torch.stack([(cord[0]+cord[2])/2,(cord[1]+cord[3])/2]) for cord in float_boxes]

    return torch.stack(center_darts), new_labels, new_boxes, new_scores

def find_closest(labels, darts):
    # Find target
    # Remove labels with down
    darts = darts.tolist()

    for i in range(len(labels)):
        if labels[i] == 'target':
            target = darts[i]
        # elif labels[i] == 'down': # Might not need
        #     darts = darts.pop(i)
    # try:
    #     labels = labels.remove('down')
    # except:
    #     print('No Down in this image')

    # print(darts)

    # Find closest dart to target
    distance = [math.sqrt((target[1]-dart[1])**2+(target[0]-dart[0])**2) for dart in darts]
    # print(distance)

    return distance

def point_count(labels, center_darts): # Change team when Having UI system ready!!!!! (Proof of concept)
    team = {'blue'  : 0,
            'green' : 0}
    index = 0

    darts = [[labels[i],center_darts[i]] for i in range(len(labels))]
    darts = sorted(darts, key=lambda x: x[1])
    darts.pop(0) # Removes target
    # print(darts)

    # +2 to the closest dart v
    if darts[0][0] == 'blueUp':
        team['blue'] += 2
        closest = 'blue'
    elif darts[0][0] == 'greenUp':
        team['green'] += 2
        closest = 'green'
    # +2 if the same colour is the next closest v
    for dart in darts[1:]:
        if closest in dart[0]:
            team[closest] += 2
            index +=1
        else:
            index +=1
            break
    # +1 for all other colours when the other team is the next closest v
    for dart in darts[index:]:
        if 'blue' in dart[0]:
            team['blue'] += 1
        elif 'green' in dart[0]:
            team['green'] += 1
        else: # This is when it finds a down dart
            continue
    return closest, team

def recalabrate(closest, team):
    print(f"Closest: {closest} \nPoints: {team}")

    # Recal
    closest_input = input("Is closest colour correct?(re-enter value if corrcet): ")
    closest = closest_input
    blue_input = input("Is blue correct?(re-enter value if corrcet): ")
    team['blue'] = blue_input
    green_input = input("Is green correct?(re-enter value if corrcet): ")
    team['green'] = green_input

    print(f"Closest: {closest} \nPoints: {team}")

    # send this to server thingy

# Notes
"""

"""