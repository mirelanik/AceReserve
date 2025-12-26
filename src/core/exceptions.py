from fastapi import HTTPException, status


class AceReserveException(HTTPException):
    pass


class CredentialsError(AceReserveException):
    def __init__(self, detail: str = "Invalid credentials.") -> None:
        super().__init__(status_code=401, detail=detail)


class ExistingUserError(AceReserveException):
    def __init__(self, detail: str = "User with this email already exists."):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedUserError(AceReserveException):
    def __init__(self, detail: str = "Incorrect email or password."):
        super().__init__(status_code=401, detail=detail)