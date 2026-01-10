from fastapi import HTTPException


class AceReserveException(HTTPException):
    pass


class CredentialsError(AceReserveException):
    def __init__(self, detail: str = "Invalid credentials.") -> None:
        super().__init__(status_code=401, detail=detail)


class ExistingUserError(AceReserveException):
    def __init__(self, detail: str = "User with this email already exists."):
        super().__init__(status_code=400, detail=detail)


class UserNotFoundError(AceReserveException):
    def __init__(self, detail: str = "User not found."):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedUserError(AceReserveException):
    def __init__(self, detail: str = "Incorrect email or password."):
        super().__init__(status_code=401, detail=detail)


class CourtNotFoundError(AceReserveException):
    def __init__(self, detail: str = "Court not found."):
        super().__init__(status_code=404, detail=detail)


class ExistingCourtError(AceReserveException):
    def __init__(self, detail: str = "Court with this number already exists."):
        super().__init__(status_code=400, detail=detail)


class ForbiddenActionError(AceReserveException):
    def __init__(
        self, detail: str = "You do not have permission to perform this action."
    ):
        super().__init__(status_code=403, detail=detail)


class StartTimeError(AceReserveException):
    def __init__(self, detail: str = "Invalid start time."):
        super().__init__(status_code=400, detail=detail)


class DoubleCourtBookingError(AceReserveException):

    def __init__(self, detail: str = "Court is already booked for this time slot."):
        super().__init__(status_code=409, detail=detail)


class DoubleCoachBookingError(AceReserveException):
    def __init__(self, detail: str = "Coach is already booked for this time slot."):
        super().__init__(status_code=409, detail=detail)


class ReservationNotFoundError(AceReserveException):
    def __init__(self, detail: str = "There is no reservation with this ID."):
        super().__init__(status_code=404, detail=detail)


class ServiceNotFoundError(AceReserveException):
    def __init__(self, detail: str = "There is no service with this ID."):
        super().__init__(status_code=404, detail=detail)


class ServiceNotChosenError(AceReserveException):
    def __init__(
        self, detail: str = "There is no service chosen for this reservation."
    ):
        super().__init__(status_code=404, detail=detail)


class NotLoggedInError(AceReserveException):
    def __init__(self, detail: str = "Only logged-in users can perform this action."):
        super().__init__(status_code=403, detail=detail)


class LoyaltyAccountNotFoundError(AceReserveException):
    def __init__(self, detail: str = "No loyalty account related to this user."):
        super().__init__(status_code=404, detail=detail)


class LightingAvailabilityError(AceReserveException):
    def __init__(self, detail: str = "Lighting is not available for this court."):
        super().__init__(status_code=400, detail=detail)


class LightingTimeError(AceReserveException):
    def __init__(self, detail: str = "Lighting is only available after 18:00."):
        super().__init__(status_code=400, detail=detail)


class FavoriteAlreadyExistsError(AceReserveException):
    def __init__(self, detail: str = "Already in your favorites."):
        super().__init__(status_code=400, detail=detail)


class CoachNotFoundError(AceReserveException):
    def __init__(self, detail: str = "Coach not found."):
        super().__init__(status_code=404, detail=detail)


class NoTargetTypeError(AceReserveException):
    def __init__(self, detail: str = "Review must target at least one entity."):
        super().__init__(status_code=400, detail=detail)


class MoreTargetTypesError(AceReserveException):
    def __init__(self, detail: str = "Review must target only one entity."):
        super().__init__(status_code=400, detail=detail)
