import matplotlib.pyplot as plt
from detecto import core, utils
from torch import stack

def load_model(image):
    # Load
    model = core.Model.load('compVision/Models_Versions/Test_ModelV2.pth', ['greenUp','blueUp','down','target'])
    # Test Image
    image = utils.read_image(f'compVision/rounds/{image}')
    # Prediction
    predictions = model.predict(image)
    # predictions format
    labels, boxes, scores = predictions

    return labels, boxes, scores

def plot_center(centers, image):
    plt.imshow(image)
    for center in centers:
        plt.plot(center[0],center[1], 'ro', markersize=5)
    plt.show()

def clean_data(labels, boxes, scores):
    new_labels, new_boxes, new_scores = [], [], []

    for index in range(len(scores)): # Remove labels that its not confident
        if scores[index] >= 0.9:
            new_labels.append(labels[index])
            new_boxes.append(boxes[index])
            new_scores.append(scores[index])

    new_boxes, new_scores = stack(new_boxes), stack(new_scores) # Merge Items to one tensor
    # print(new_labels, '\n',new_boxes, '\n',new_scores)
    # visualize.show_labeled_image(image, new_boxes, new_labels)

    float_boxes = new_boxes.float()
    center_darts = [stack([(cord[0]+cord[2])/2,(cord[1]+cord[3])/2]) for cord in float_boxes]

    return stack(center_darts), new_labels, new_boxes, new_scores