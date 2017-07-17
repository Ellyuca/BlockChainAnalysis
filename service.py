from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route("/chainBot", methods=['POST'])
def chainBot():
    print(request.data)
    return jsonify({
        "speech": "My Test Speech",
        "displayText": "My Test Text",
        "data": {},
        "contextOut": [],
        "source": ""
    }), 200, {'Content-Type': 'text/css; charset=utf-8'}


if __name__ == "__main__":
    app.run("0.0.0.0", 80)
