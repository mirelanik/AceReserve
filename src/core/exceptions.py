from fastapi import HTTPException, status


class AceReserveException(HTTPException):
    pass


class CredentialsError(AceReserveException):
    def __init__(self, detail: str = "Invalid credentials.") -> None:
        super().__init__(status_code=401, detail=detail)

