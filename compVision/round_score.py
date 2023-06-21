from detecto import visualize
import math

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

    all_darts = [[labels[i],center_darts[i]] for i in range(len(labels))]
    all_darts = sorted(all_darts, key=lambda x: x[1])
    all_darts.pop(0) # Removes target
    no_down_darts = [item for item in all_darts if 'down' not in item]
    # print(darts)

    # +2 to the closest dart v
    if no_down_darts[0][0] == 'blueUp':
        team['blue'] += 2
        closest = 'blue'
    elif no_down_darts[0][0] == 'greenUp':
        team['green'] += 2
        closest = 'green'
    # +2 if the same colour is the next closest v
    for dart in no_down_darts[1:]:
        if closest in dart[0]:
            team[closest] += 2
            index +=1
        else:
            index +=1
            break
    # +1 for all other colours when the other team is the next closest v
    for dart in no_down_darts[index:]:
        if 'blue' in dart[0]:
            team['blue'] += 1
        elif 'green' in dart[0]:
            team['green'] += 1
        else: # This is when it finds a down dart
            continue
    return closest, team, all_darts

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
    return closest, team

    # send this to server thingy

def dart_system(labels, center_darts):
    distance = find_closest(labels, center_darts)

    closest, dart_score, all_darts = point_count(labels, distance) # all_darts are for future stats

    # closest, team = recalabrate(closest, dart_score)
    # visualize.show_labeled_image(image, boxes, distance)
    # hp.plot_center(center_darts, image)

    return closest, dart_score
# Notes
"""

"""