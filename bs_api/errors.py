class ClientError(Exception):
    def __init__(self, message) -> None:
        self.message = message

    def __str__(self):
        return self.message


class IncorrectError(ClientError):
    def __init__(
        self, message: str = "Provided incorrect parameters for the request."
    ) -> None:
        super().__init__(message)


class AccessError(ClientError):
    def __init__(
        self,
        message: str = "Access denied, either because of missing/incorrect credentials or used API token does not grant access to the requested resource.",
    ) -> None:
        super().__init__(message)


class ResourceError(ClientError):
    def __init__(self, message: str = "Resource was not found.") -> None:
        super().__init__(message)


class RequestsLimitError(ClientError):
    def __init__(
        self,
        message: str = "Request was throttled, because amount of requests was above the threshold defined for the used API token.",
    ) -> None:
        super().__init__(message)


class UnknownError(ClientError):
    def __init__(
        self, message: str = "Unknown error happened when handling the request."
    ) -> None:
        super().__init__(message)


class ServiceError(ClientError):
    def __init__(
        self,
        message: str = "Service is temporarily unavailable because of maintenance.",
    ) -> None:
        super().__init__(message)
