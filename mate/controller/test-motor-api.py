from __future__ import print_function
import time
import controller
from controller.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = controller.DefaultApi(controller.ApiClient())
#
# try:
#     # Get motor status.
#     api_response = api_instance.get_motor()
#     pprint(api_response)
# except ApiException as e:
#     print("Exception when calling DefaultApi->get_motor: %s\n" % e)

# create an instance of the API class
# api_instance = controller.DefaultApi(controller.ApiClient())
body = controller.MotorRequest() # MotorRequest | null

try:
    # Set PWM value for motor.
    for i in range(0, 10000):
        api_instance.set_motor({'motorid': 1, 'pwm': i})
except ApiException as e:
    print("Exception when calling DefaultApi->set_motor: %s\n" % e)


