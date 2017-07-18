from flask import Flask
from flask import jsonify
from flask import request
import requests
import json

app = Flask(__name__)


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
    print(req)
    ##
    # Check if the action is completed
    if not req['result']['actionIncomplete']:
        ##
        # Check in which context we are
        if req['result']['contexts'][0]['name'] == "info-cryptocurrency-exchange":
            ##
            # Call the reponse for the "info-bitcoin-exchange" context
            if  req['result']['contexts'][0]['parameters']['cryptocurrency'] == "bitcoin":
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
                }), 200, {'Content-Type': 'text/css; charset=utf-8'}
            else:
                return jsonify({
                    "speech": "I don't know the exchange rate for that cryptocurrency...",
                    "displayText": "I don't know the exchange rate for that cryptocurrency...",
                    "data": {},
                    "contextOut": [],
                    "source": ""
                }), 200, {'Content-Type': 'text/css; charset=utf-8'}
        else:
            return jsonify({
                "speech": "Sorry, can't understand your request...",
                "displayText": "Sorry, can't understand your request...",
                "data": {},
                "contextOut": [],
                "source": ""
            }), 404, {'Content-Type': 'text/css; charset=utf-8'}
    else:
        return jsonify({
            "speech": "Sorry, your request is not complete...",
            "displayText": "Sorry, your request is not complete...",
            "data": {},
            "contextOut": [],
            "source": ""
        }), 400, {'Content-Type': 'text/css; charset=utf-8'}


if __name__ == "__main__":
    app.run("0.0.0.0", 80, debug=True)
