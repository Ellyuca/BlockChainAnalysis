from flask import Flask
from flask import jsonify
from flask import request
from flask import url_for
from flask import send_file
from os import path
# matplotlib
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import requests
from PIL import Image
import datetime
import numpy as np

app = Flask(__name__)
TMP_FILE = "/tmp/myChart.jpeg"

@app.route("/updateChart", methods=['GET'])
def update_chart():
    """Download chart and save the image.

    ref: https://core.telegram.org/blackberry/chat-media-send
    """
    r = requests.get(
        'https://api.blockchain.info/charts/market-price?format=json&timespan=30days')
    result = r.json()

    x_list = []
    y_list = []
    for obj in result['values']:
        x_list.append(obj['x'])
        y_list.append(obj['y'])

    last_result = [datetime.datetime.fromtimestamp(
        day).strftime("%d/%m") for day in x_list]

    plt.plot(x_list, y_list, rasterized=True)
    plt.xticks(x_list[0::2], last_result[0::2])
    low = (min(y_list) / 100) * 100 - 100
    high = (max(y_list) / 100) * 100 + 200
    plt.yticks(np.arange(low, high, 100))

    # print("my Y valeus", y_list)
    plt.xlabel('Day')
    figure = plt.gcf()  # get current figure
    figure.set_size_inches(12, 7)
    figure.tight_layout()
    plt.grid(True)
    plt.savefig(TMP_FILE, dpi=200, orientation='landscape',
                pad_inches=0, bbox_inches='tight')
    ##
    # Resize for telegram
    foo = Image.open(TMP_FILE)
    size_x, size_y = foo.size
    foo = foo.resize((int(size_x / 4), int(size_y / 4)),Image.ANTIALIAS)
    foo.save(TMP_FILE, quality=87)
    return jsonify({
        'url': "https://getcharts.herokuapp.com/getChart"
    })

@app.route("/getChart", methods=['GET'])
def get_chart():
    return send_file(TMP_FILE, mimetype="image/jpeg")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)