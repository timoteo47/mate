from flask import Flask, session, redirect, url_for, request
from markupsafe import escape
from pprint import pprint
import json
from flask import Flask, request, jsonify
import time
import logging
count = 0
start_time = 0
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route("/motor", methods=['POST'])
def hello():
    # logging.info('hello')
    global count
    global start_time
    if request.method == "POST":
        # print("got request method POST")
        pass
    if request.is_json:
        # print("is json")
        count += 1
        if count == 1:
            start_time = time.time()
        data = request.get_json()
        # print("type of data {}".format(type(data))) # type dict
        # print("data {}".format(data)) # type dict
        # print("data as string {}".format(json.dumps(data)))
        if (count % 1000) == 0:
            rate = count/(time.time() - start_time)
            print("Rate == {} qps".format(rate))

        motorid = data['motorid']
        pwm = data['pwm']
        # print("MotorID: {} PWM: {}".format(motorid, pwm))

        # print("MotorID: {} PWM: {}".format[data['motorid'], data['pwm']])
        # print ("keys {}".format(json.dumps(data.keys())))
    return jsonify(message='success')
#
# @app.route('/motor', methods=['POST', 'GET'])
# def motor():
#     error = None
#     if request.method == 'POST':
#         print("REQUEST **********")
#         pprint(request)
#         print("REQUEST **********")
#         content = request.json
#         motor_id = content['motorid']
#         pwm = content['pwm']
#         print("Received command to set motor: {} to {}".format(motor_id, pwm))
#         return {'motor': id, 'pwm': pwm}
#     else:
#         id = 0
#         pwm = 1500
#         return {'motor': id, 'pwm': pwm}
#
