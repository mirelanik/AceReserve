"""Custom exception classes for AceReserve API.
Defines domain-specific exceptions that map to appropriate HTTP status codes
for clear and consistent error handling throughout the API.
"""

from fastapi import HTTPException


class AceReserveException(HTTPException):
    """Base exception class for all AceReserve API errors."""

    pass


class CredentialsError(AceReserveException):
    """Raised when authentication credentials are invalid."""

    def __init__(self, detail: str = "Invalid credentials.") -> None:
        super().__init__(status_code=401, detail=detail)


class ExistingUserError(AceReserveException):
    """Raised when attempting to create a user with an existing email."""

    def __init__(self, detail: str = "User with this email already exists."):
        super().__init__(status_code=400, detail=detail)


class UserNotFoundError(AceReserveException):
    """Raised when a requested user cannot be found."""

    def __init__(self, detail: str = "User not found."):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedUserError(AceReserveException):
    """Raised when login credentials are incorrect."""

    def __init__(self, detail: str = "Incorrect email or password."):
        super().__init__(status_code=401, detail=detail)


class CourtNotFoundError(AceReserveException):
    """Raised when a requested court cannot be found."""

    def __init__(self, detail: str = "Court not found."):
        super().__init__(status_code=404, detail=detail)


class ExistingCourtError(AceReserveException):
    """Raised when attempting to create a court with an existing number."""

    def __init__(self, detail: str = "Court with this number already exists."):
        super().__init__(status_code=400, detail=detail)


class ForbiddenActionError(AceReserveException):
    """Raised when user lacks permission for the requested action."""

    def __init__(
        self, detail: str = "You do not have permission to perform this action."
    ):
        super().__init__(status_code=403, detail=detail)


class StartTimeError(AceReserveException):
    """Raised when reservation start time is in the past."""

    def __init__(self, detail: str = "Invalid start time."):
        super().__init__(status_code=400, detail=detail)


class DoubleCourtBookingError(AceReserveException):
    """Raised when a court is already booked for the requested time slot."""

    def __init__(self, detail: str = "Court is already booked for this time slot."):
        super().__init__(status_code=409, detail=detail)


class DoubleCoachBookingError(AceReserveException):
    """Raised when a coach is already booked for the requested time slot."""

    def __init__(self, detail: str = "Coach is already booked for this time slot."):
        super().__init__(status_code=409, detail=detail)


class ReservationNotFoundError(AceReserveException):
    """Raised when a requested reservation cannot be found."""

    def __init__(self, detail: str = "There is no reservation with this ID."):
        super().__init__(status_code=404, detail=detail)


class ServiceNotFoundError(AceReserveException):
    """Raised when a requested service cannot be found."""

    def __init__(self, detail: str = "There is no service with this ID."):
        super().__init__(status_code=404, detail=detail)


class ServiceNotChosenError(AceReserveException):
    """Raised when a reservation requires a service but none was selected."""

    def __init__(
        self, detail: str = "There is no service chosen for this reservation."
    ):
        super().__init__(status_code=400, detail=detail)


class NotLoggedInError(AceReserveException):
    """Raised when an unauthenticated user tries to access protected resources."""

    def __init__(self, detail: str = "Only logged-in users can perform this action."):
        super().__init__(status_code=401, detail=detail)


class LoyaltyAccountNotFoundError(AceReserveException):
    """Raised when a user's loyalty account cannot be found."""

    def __init__(self, detail: str = "No loyalty account related to this user."):
        super().__init__(status_code=404, detail=detail)


class LightingAvailabilityError(AceReserveException):
    """Raised when a court doesn't have lighting capability."""

    def __init__(self, detail: str = "Lighting is not available for this court."):
        super().__init__(status_code=400, detail=detail)


class LightingTimeError(AceReserveException):
    """Raised when lighting is requested outside allowed hours."""

    def __init__(self, detail: str = "Lighting is only available after 18:00."):
        super().__init__(status_code=400, detail=detail)


class FavoriteAlreadyExistsError(AceReserveException):
    """Raised when attempting to add a duplicate favorite."""

    def __init__(self, detail: str = "Already in your favorites."):
        super().__init__(status_code=409, detail=detail)


class CoachNotFoundError(AceReserveException):
    """Raised when a coach cannot be found."""

    def __init__(self, detail: str = "Coach not found."):
        super().__init__(status_code=404, detail=detail)


class NoTargetTypeError(AceReserveException):
    """Raised when a review has no target type."""

    def __init__(self, detail: str = "Review must target at least one entity."):
        super().__init__(status_code=400, detail=detail)


class MoreTargetTypesError(AceReserveException):
    """Raised when a review has more than one target type."""

    def __init__(self, detail: str = "Review must target only one entity."):
        super().__init__(status_code=400, detail=detail)
