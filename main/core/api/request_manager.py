'''
Use requests library to send requests
Class:
    RequestManager
Functions:
    get_instance() --> RequestManager
    send_request(str, str, dict=None, arr):
'''

from http import HTTPStatus
from json import JSONDecodeError
import requests
from assertpy import assert_that
from main.core.utils.json_reader import JsonReader
from main.core.api.http_methods_enum import HttpMethods


class RequestManager:
    '''
    A class to represent a HHTP Request
    Atributes
    ---------
    __config : dict
    __env_users : dict
    url : str
    key : str
    token : str
    headers : dict
    params : dict

    Functions
    ---------
    get_instance()
    send_request(http_method, end_point, body=None, **kwargs):
    '''
    __instance = None

    def __init__(self):
        '''
        Constructs Request Manager object
        '''
        self.__config = JsonReader().get_json('./configuration.json')
        __environment = JsonReader().get_json('./environment.json')
        env_selected = self.__config.get("environment", "develop")
        self.__env_users = __environment.get(env_selected).get("users")
        self.url = __environment.get(env_selected).get("api_url")
        self.access = {
            self.__env_users.get("admin").get("key"):
            self.__env_users.get("admin").get("token")
            }
        self.headers = {"Accept": __environment["headers"]}
        self.params = {}
        if __environment.get(env_selected).get("auth") == "headers":
            self.headers.update(self.access)
        elif __environment.get(env_selected).get("auth") == "params":
            self.params = {"key": self.access['key'],
                           "token": self.access['token']}
        self.response = None

    @staticmethod
    def get_instance():
        '''
        Create a request manager instance
        Return
        ------
        RequestManager : object
        '''
        if RequestManager.__instance is None:
            RequestManager.__instance = RequestManager()
        return RequestManager.__instance

    def send_request(self, http_method, end_point, body=None, **kwargs):
        '''
        Send a http request to a API
        Parameters
        ----------
            http_method : str
                http_method Ex: POST GET PUT DELETE
            end_point : str
                API endpoint
            body : dict
                Dictionary for POST method
            kwargs : arr
                More options for params
        Returns
        -------
        dict
        '''
        self.params.update(kwargs)
        self.response = requests.request(
            method=HttpMethods[http_method].value,
            url=f"{self.url}{end_point}",
            headers=self.headers,
            data=None if body is None else body,
            params=self.params,
            timeout=10
        )
        try:
            assert_that(self.response.status_code).\
                is_equal_to(HTTPStatus.OK.value)
        except AssertionError:
            pass
        try:
            return self.response.json(), self.response.status_code
        except JSONDecodeError:
            response_text = {"text": self.response.text}
            return response_text, self.response.status_code
