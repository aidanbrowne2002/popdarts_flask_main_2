import matplotlib.pyplot as plt
from detecto import core, utils

def load_model(table):
    # Load
    model = core.Model.load('Models_Version/Test_ModelV2.pth', ['greenUp','blueUp','down','target'])
    # Test Image
    image = utils.read_image(f'round_image/{table}.jpg')
    # Prediction
    predictions = model.predict(image)
    # predictions format
    labels, boxes, scores = predictions

    return labels, boxes, scores, image

def plot_center(centers, image):
    plt.imshow(image)
    for center in centers:
        plt.plot(center[0],center[1], 'ro', markersize=5)
    plt.show()