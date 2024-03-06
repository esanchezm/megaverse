from enum import Enum

import tenacity
from apiclient import (
    APIClient,
    JsonRequestFormatter,
    JsonResponseHandler,
    NoAuthentication,
)
from apiclient.error_handlers import ErrorHandler
from apiclient.request_strategies import RequestStrategy
from apiclient.retrying import retry_if_api_request_error
from apiclient.utils.typing import OptionalDict

retry_request = tenacity.retry(
    retry=retry_if_api_request_error(status_codes=[429, 500, 501, 503]),
    wait=tenacity.wait_fixed(2),
    stop=tenacity.stop_after_attempt(5),
    reraise=True,
)


class CrossmintAuthenticationStrategy(RequestStrategy):
    """
    Authentication strategy for Crossmint API. It adds the candidateId to the request data for POST and DELETE.
    """

    def __init__(self, candidate_id: str):
        self.candidate_id = candidate_id
        super().__init__()

    @retry_request
    def post(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
        data.update({"candidateId": self.candidate_id})
        super().post(endpoint, data, params, **kwargs)

    @retry_request
    def delete(self, endpoint: str, params: OptionalDict = None, **kwargs):
        kwargs["data"].update({"candidateId": self.candidate_id})
        super().delete(endpoint, params, **kwargs)


class BaseCrossmintClient(APIClient):
    """
    Base client for Crossmint API. It sets the authentication strategy to CrossmintAuthenticationStrategy and the
    response handler to JsonResponseHandler.
    """

    DEFAULT_BASE_URL = "https://challenge.crossmint.io"

    def __init__(self, candidate_id: str, base_url=None):
        self.candidate_id = candidate_id
        self.base_url = base_url or self.DEFAULT_BASE_URL
        super(BaseCrossmintClient, self).__init__(
            request_strategy=CrossmintAuthenticationStrategy(self.candidate_id),
            response_handler=JsonResponseHandler,
            request_formatter=JsonRequestFormatter,
            error_handler=ErrorHandler,
        )


class MapClient(BaseCrossmintClient):
    """
    Client for the map endpoint of the Crossmint API. It has no authentication
    """

    def __init__(self, candidate_id: str, base_url=None):
        super().__init__(candidate_id, base_url)
        self.set_authentication_method(NoAuthentication())
        self.rest_url = f"{self.base_url}/api/map/{self.candidate_id}"

    @retry_request
    def get_status(self):
        return self.get(self.rest_url)

    @retry_request
    def get_goal(self):
        return self.get(f"{self.rest_url}/goal")


class PolyanetClient(BaseCrossmintClient):
    """
    Client for the polyanet endpoint of the Crossmint API.

    It has the following methods:
    - set(row: int, col: int): Set a polyanet at the given row and column
    - clean(row: int, col: int): Clean the polyanet at the given row and column
    """

    def __init__(self, candidate_id: str, base_url=None):
        super().__init__(candidate_id, base_url)
        self.rest_url = f"{self.base_url}/api/polyanets"

    @retry_request
    def set(self, row: int, col: int):
        return self.post(
            self.rest_url,
            data={
                "row": row,
                "column": col,
            },
        )

    @retry_request
    def clean(self, row: int, col: int):
        return self.delete(
            self.rest_url,
            data={
                "row": row,
                "column": col,
            },
        )


class Color(Enum):
    """
    Enum for the color of the soloon.
    """

    RED = "red"
    BLUE = "blue"
    PURPLE = "purple"
    WHITE = "white"

    @classmethod
    def parse(cls, value: str):
        try:
            return cls[value.upper()]
        except KeyError as e:
            raise ValueError(f"Unknown color: {value}", e)


class SoloonClient(BaseCrossmintClient):
    """
    Client for the soloon endpoint of the Crossmint API.

    It has the following methods:
    - set(row: int, col: int, color: Color): Set a soloon at the given row and column with the given color
    - clean(row: int, col: int): Clean the soloon at the given row and column
    """

    def __init__(self, candidate_id: str, base_url=None):
        super().__init__(candidate_id, base_url)
        self.rest_url = f"{self.base_url}/api/soloons"

    @retry_request
    def set(self, row: int, col: int, color: Color):
        return self.post(
            self.rest_url,
            data={
                "row": row,
                "column": col,
                "color": color.value,
            },
        )

    @retry_request
    def clean(self, row: int, col: int):
        return self.delete(
            self.rest_url,
            data={
                "row": row,
                "column": col,
            },
        )


class Direction(Enum):
    """
    Enum for the direction of the cometh.
    """

    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

    @classmethod
    def parse(cls, value: str):
        try:
            return cls[value.upper()]
        except KeyError as e:
            raise ValueError(f"Unknown direction: {value}", e)


class ComethClient(BaseCrossmintClient):
    """
    Client for the cometh endpoint of the Crossmint API.

    It has the following methods:
    - set(row: int, col: int, direction: Direction): Set a cometh at the given row and column with the given direction
    - clean(row: int, col: int): Clean the cometh at the given row and column
    """

    def __init__(self, candidate_id: str, base_url=None):
        super().__init__(candidate_id, base_url)
        self.rest_url = f"{self.base_url}/api/comeths"

    @retry_request
    def set(self, row: int, col: int, direction: Direction):
        return self.post(
            self.rest_url,
            data={
                "row": row,
                "column": col,
                "direction": direction.value,
            },
        )

    @retry_request
    def clean(self, row: int, col: int):
        return self.delete(
            self.rest_url,
            data={
                "row": row,
                "column": col,
            },
        )
