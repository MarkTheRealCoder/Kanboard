from typing import Callable

from django.http import HttpResponse, HttpRequest, JsonResponse
from django.urls import path, resolve

from .database import DBRequestBuilder, _DBServices, _DatabaseError


class RequestHandler:
    """
    RequestHandler class
    This class is a singleton class that handles requests before they are sent to the views.
    This class is responsible for:
    - Validating requests
    - Obtaining all the necessary data for the views
    - Handling errors
    - Sending the responses to the client

    How to use:
    - use the bind decorator to bind a view to a specific path
    - use the forward method inside the urls.py file to dynamically forward requests to the appropriate view

    Attributes:
        ___singleton: RequestHandler - The singleton instance of the class.
        ___views: dict[str, tuple[Callable, tuple[DBRequestBuilder]]] - A dictionary mapping paths to views and their associated DBRequestBuilders.

    Methods:
        bind: Binds a view to a specific path.
        forward: Forwards a request to the appropriate view.
        get_from_db: Executes a query using the DBServices instance.
        ___instance: Returns the singleton instance of the class.
        match_path: Matches the request path to the bound view.
    """

    def __init__(self, db_name: str):
        """
        Initializes the RequestHandler instance.
        """
        self.___views: dict[str: tuple[Callable, tuple[DBRequestBuilder]]] = {}
        self.___dbservice: _DBServices = _DBServices(db_name)
        self.___urls = []

    def ___get_from_db(self, query: str):
        """
        Executes a query using the DBServices instance.

        :param query: str - The query to execute.
        :return: Any - The result of the query execution.
        """
        return self.___dbservice.execute(query)

    def bind(self, _name: str, _path: str, *data: tuple[DBRequestBuilder]):
        """
        Binds a view to a specific path.

        :param _name: str - The name of the view.
        :param _path: str - The path to bind the view to.
        :param data: tuple[DBRequestBuilder] - The DBRequestBuilders specifying necessary request parameters and their error messages.
        :return: Callable - The decorator function.
        """
        def decorator(view: Callable):
            self.___views[_path] = (view, data)
            self.___urls.append(path(_path, self.forward, name=f"{_name}"))
            def wrapper(*args, **kwargs):
                return view(*args, **kwargs)
            return wrapper
        return decorator

    def forward(self, request: HttpRequest, **kwargs):
        """
        Forwards a request to the appropriate view.

        :param request: HttpRequest - The request object.
        :param kwargs: tuple - Additional arguments to pass to the view.
        :return: HttpResponse - The response from the view or an error message.
        """

        view, dbrequests = None, None
        try:
            view, dbrequests = self.___match_path(request.path)
        except Exception as e:
            return HttpResponse("404 Not Found")
        arguments = kwargs
        arguments['uuid'] = request.session.get('user_id', None)

        for dbreq in dbrequests:
            try:
                arguments[dbreq.name()] = self.___get_from_db(dbreq.query(**kwargs))
            except _DatabaseError as e:
                return HttpResponse(dbreq.message())

        arguments.pop('uuid')

        return view(request, **arguments)

    def ___match_path(self, path: str) -> tuple[Callable, tuple[DBRequestBuilder]]:
        """
        Matches the path specified in the bind decorator with the current path provided by the request object.
        Matching is more complicated than just checking if the path is in the dictionary, because the path can contain
        relative elements (for example: <int:board_id>/path/...).

        :param path: str - The path to match.
        :return: tuple[Callable, tuple[DBRequestBuilder]] - The matched view and its associated DBRequestBuilders.
        """
        resolution = resolve(path)
        real = resolution.route
        return self.___views.get(real, None)

    def urls(self):
        return self.___urls



class JsonResponses:
    """
    JsonResponses class
    This class is a utility class that contains static methods for generating JSON responses.

    Methods:
        response: Generates a Status JSON response.
    """

    WARNING = 100
    SUCCESS = 200
    ERROR = 500

    @staticmethod
    def response(status: int, message: str):
        """
        Generates a JSON response.

        :param status: int - The status code of the response.
        :param message: str - The message to include in the response.
        :return: JsonResponse - The JSON response.
        """
        return JsonResponse({'status': status, 'message': message})

