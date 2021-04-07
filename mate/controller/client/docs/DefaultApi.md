# controller.DefaultApi

All URIs are relative to *http://127.0.0.1:5000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_motor**](DefaultApi.md#get_motor) | **GET** /motor | Get motor status.
[**set_motor**](DefaultApi.md#set_motor) | **POST** /motor | Set PWM value for motor.

# **get_motor**
> object get_motor()

Get motor status.

Get motor status.

### Example
```python
from __future__ import print_function
import time
import controller
from controller.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = controller.DefaultApi()

try:
    # Get motor status.
    api_response = api_instance.get_motor()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling DefaultApi->get_motor: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_motor**
> set_motor(body)

Set PWM value for motor.

Send PWM value for motor. 

### Example
```python
from __future__ import print_function
import time
import controller
from controller.rest import ApiException
from pprint import pprint

# create an instance of the API class
api_instance = controller.DefaultApi()
body = controller.MotorRequest() # MotorRequest | null

try:
    # Set PWM value for motor.
    api_instance.set_motor(body)
except ApiException as e:
    print("Exception when calling DefaultApi->set_motor: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**MotorRequest**](MotorRequest.md)| null | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

