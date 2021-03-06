# coding: utf-8

"""
    X Academy ROV controller

    API to control ROV  # noqa: E501

    OpenAPI spec version: 0.7.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class MotorRequest(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'motorid': 'int',
        'pwm': 'int'
    }

    attribute_map = {
        'motorid': 'motorid',
        'pwm': 'pwm'
    }

    def __init__(self, motorid=None, pwm=None):  # noqa: E501
        """MotorRequest - a model defined in Swagger"""  # noqa: E501
        self._motorid = None
        self._pwm = None
        self.discriminator = None
        if motorid is not None:
            self.motorid = motorid
        if pwm is not None:
            self.pwm = pwm

    @property
    def motorid(self):
        """Gets the motorid of this MotorRequest.  # noqa: E501

        motor id  # noqa: E501

        :return: The motorid of this MotorRequest.  # noqa: E501
        :rtype: int
        """
        return self._motorid

    @motorid.setter
    def motorid(self, motorid):
        """Sets the motorid of this MotorRequest.

        motor id  # noqa: E501

        :param motorid: The motorid of this MotorRequest.  # noqa: E501
        :type: int
        """

        self._motorid = motorid

    @property
    def pwm(self):
        """Gets the pwm of this MotorRequest.  # noqa: E501

        PWM.  # noqa: E501

        :return: The pwm of this MotorRequest.  # noqa: E501
        :rtype: int
        """
        return self._pwm

    @pwm.setter
    def pwm(self, pwm):
        """Sets the pwm of this MotorRequest.

        PWM.  # noqa: E501

        :param pwm: The pwm of this MotorRequest.  # noqa: E501
        :type: int
        """

        self._pwm = pwm

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(MotorRequest, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, MotorRequest):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
