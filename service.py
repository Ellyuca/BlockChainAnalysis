from flask import Flask
from flask import jsonify
from flask import request
from flask import url_for

# matplotlib
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import requests
import json
import datetime
import numpy as np
from os import path
from PIL import Image

app = Flask(__name__)


def get_chart(filename="myChart.jpeg"):
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
    out_path = path.join('static', filename)
    plt.savefig(out_path, dpi=300, orientation='landscape',
                pad_inches=0, bbox_inches='tight')
    ##
    # Resize for telegram
    foo = Image.open(out_path)
    size_x, size_y = foo.size
    foo = foo.resize((size_x / 4, size_y / 4),Image.ANTIALIAS)
    foo.save(out_path, quality=87)
    return "http://139.59.105.205{}".format(url_for('static', filename=filename))


def get_ticker(currency):
    """Get the currency echange ratio of bitcoin.

    Params:
        currencyt (str): the currency selected by the user

    Returns:
        (str) The response string
    """
    CURRENCY_TYPE = {
        'dollar': "USD",
        'euro': "EUR",
        'hkd': "HKD"
    }
    result = requests.get('https://blockchain.info/ticker')
    result = result.json()
    return "The bitchoin exchange rate in {} is : {}".format(
        CURRENCY_TYPE[currency],
        result[CURRENCY_TYPE[currency]]['last']
    )


@app.route("/chainBot", methods=['POST'])
def chainBot():
    """The Chain Bot service.

    Doc: https://api.ai/docs/fulfillment
    Doc on error responses: https://api.ai/docs/fulfillment#errors
    """
    ##
    # Convert the request data string into JSON obj
    req = json.loads(request.data)
    print(json.dumps(req, indent=2))
    ##
    # Check if the action is completed
    if not req['result']['actionIncomplete']:
        ##
        # INFO CRYPTOCURRENCY EXCHANGE
        if req['result']['contexts'][0]['name'] == "info-cryptocurrency-exchange":
            ##
            # Call the reponse for the "info-bitcoin-exchange" context
            if req['result']['contexts'][0]['parameters']['cryptocurrency'] == "bitcoin":
                response = get_ticker(req['result']['contexts'][
                                      0]['parameters']['currency'])
                ##
                # Return the response
                return jsonify({
                    "speech": response,
                    "displayText": response,
                    "data": {},
                    "contextOut": [],
                    "source": ""
                }), 200, {'Content-Type': 'application/json; charset=utf-8'}
            else:
                return jsonify({
                    "speech": "I don't know the exchange rate for that cryptocurrency...",
                    "displayText": "I don't know the exchange rate for that cryptocurrency...",
                    "data": {},
                    "contextOut": [],
                    "source": ""
                }), 200, {'Content-Type': 'application/json; charset=utf-8'}
        ##
        # INFO MARKET
        elif req['result']['contexts'][0]['name'] == "info-market":
            chart_url = get_chart()
            print(chart_url)
            return jsonify({
                "speech": chart_url,
                "messages": [
                    {
                        "type": 3,
                        "platform": "telegram",
                        "imageUrl": chart_url
                    },
                    {
                        "type": 0,
                        "speech": chart_url
                    }
                ]
            }), 200, {'Content-Type': 'application/json; charset=utf-8'}
        else:
            return jsonify({
                "speech": "Sorry, can't understand your request...",
                "displayText": "Sorry, can't understand your request...",
                "data": {},
                "contextOut": [],
                "source": ""
            }), 404, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify({
            "speech": "Sorry, your request is not complete...",
            "displayText": "Sorry, your request is not complete...",
            "data": {},
            "contextOut": [],
            "source": ""
        }), 400, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == "__main__":
    app.run("0.0.0.0", 80, debug=True)
