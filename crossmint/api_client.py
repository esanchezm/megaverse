from apiclient import APIClient, QueryParameterAuthentication, NoAuthentication, JsonResponseHandler, JsonRequestFormatter
from apiclient.error_handlers import ErrorHandler
from apiclient.request_strategies import RequestStrategy
from apiclient.utils.typing import OptionalDict


class CrossmintAuthenticationStrategy(RequestStrategy):

    def __init__(self, candidate_id: str):
        self.candidate_id = candidate_id
        super().__init__()

    def post(self, endpoint: str, data: dict, params: OptionalDict = None, **kwargs):
        data.update({"candidateId": self.candidate_id})
        super().post(endpoint, data, params, **kwargs)

    def delete(self, endpoint: str, params: OptionalDict = None, **kwargs):
        kwargs["data"].update({"candidateId": self.candidate_id})
        super().delete(endpoint, params, **kwargs)



class BaseCrossmintClient(APIClient):
    DEFAULT_BASE_URL = "https://challenge.crossmint.io"

    def __init__(self, candidate_id: str, base_url=None):
        self.candidate_id = candidate_id
        self.base_url = base_url or self.DEFAULT_BASE_URL
        super(BaseCrossmintClient, self).__init__(
            request_strategy=CrossmintAuthenticationStrategy(
                self.candidate_id
            ),
            response_handler=JsonResponseHandler,
            request_formatter=JsonRequestFormatter,
            error_handler=ErrorHandler,
        )


class MapClient(BaseCrossmintClient):

    def __init__(self, candidate_id: str, base_url=None):
        super().__init__(candidate_id, base_url)
        self.set_authentication_method(NoAuthentication())
        self.rest_url = f"{self.base_url}/api/map/{self.candidate_id}"

    def get_status(self):
        return self.get(self.rest_url)

    def get_goal(self):
        return self.get(f"{self.rest_url}/goal")


class PolyanetClient(BaseCrossmintClient):

    def __init__(self, candidate_id: str, base_url=None):
        super().__init__(candidate_id, base_url)
        self.rest_url = f"{self.base_url}/api/polyanets"

    def set(self, row: int, col: int):
        return self.post(
            self.rest_url,
            data={
                "row": row,
                "column": col,
            },
        )

    def clean(self, row: int, col: int):
        return self.delete(
            self.rest_url,
            data={
                "row": row,
                "column": col,
            },
        )
