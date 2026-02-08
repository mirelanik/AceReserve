"""Custom exception classes for AceReserve API.
Defines domain-specific exceptions that map to appropriate HTTP status codes
for clear and consistent error handling throughout the API.
"""

from fastapi import HTTPException


class AceReserveException(HTTPException):
    """Base exception class for all AceReserve application errors."""

    pass


class CredentialsError(AceReserveException):
    """Raised when authentication fails due to invalid email or password."""

    def __init__(self, detail: str = "Invalid credentials.") -> None:
        super().__init__(status_code=401, detail=detail)


class ExistingUserError(AceReserveException):
    """Raised when attempting to register a user that already exists."""

    def __init__(self, detail: str = "User with this email already exists."):
        super().__init__(status_code=400, detail=detail)


class UserNotFoundError(AceReserveException):
    """Raised when a requested user cannot be found in the database."""

    def __init__(self, detail: str = "User not found."):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedUserError(AceReserveException):
    """Raised when a user is not authorized to access a resource."""

    def __init__(self, detail: str = "Incorrect email or password."):
        super().__init__(status_code=401, detail=detail)


class CourtNotFoundError(AceReserveException):
    """Raised when a requested court cannot be found."""

    def __init__(self, detail: str = "Court not found."):
        super().__init__(status_code=404, detail=detail)


class ExistingCourtError(AceReserveException):
    """Raised when attempting to create a court that already exists."""

    def __init__(self, detail: str = "Court with this number already exists."):
        super().__init__(status_code=400, detail=detail)


class ForbiddenActionError(AceReserveException):
    """Raised when a user has insufficient permissions for an action."""

    def __init__(
        self, detail: str = "You do not have permission to perform this action."
    ):
        super().__init__(status_code=403, detail=detail)


class StartTimeError(AceReserveException):
    """Raised when the reservation start time is invalid."""

    def __init__(self, detail: str = "Invalid start time."):
        super().__init__(status_code=400, detail=detail)


class DoubleCourtBookingError(AceReserveException):
    """Raised when attempting to book an already occupied court slot."""

    def __init__(self, detail: str = "Court is already booked for this time slot."):
        super().__init__(status_code=409, detail=detail)


class DoubleCoachBookingError(AceReserveException):
    """Raised when attempting to book an already occupied coach slot."""

    def __init__(self, detail: str = "Coach is already booked for this time slot."):
        super().__init__(status_code=409, detail=detail)


class ReservationNotFoundError(AceReserveException):
    """Raised when a requested reservation cannot be found."""

    def __init__(self, detail: str = "There is no reservation with this ID."):
        super().__init__(status_code=404, detail=detail)


class ServiceNotFoundError(AceReserveException):
    """Raised when a requested generic service cannot be found."""

    def __init__(self, detail: str = "There is no service with this ID."):
        super().__init__(status_code=404, detail=detail)


class ServiceNotChosenError(AceReserveException):
    """Raised when creating a reservation without selecting a service type."""

    def __init__(
        self, detail: str = "There is no service chosen for this reservation."
    ):
        super().__init__(status_code=400, detail=detail)


class NotLoggedInError(AceReserveException):
    """Raised when an unauthenticated user attempts a protected action."""

    def __init__(self, detail: str = "Only logged-in users can perform this action."):
        super().__init__(status_code=401, detail=detail)


class LoyaltyAccountNotFoundError(AceReserveException):
    """Raised when a user does not have an associated loyalty account."""

    def __init__(self, detail: str = "No loyalty account related to this user."):
        super().__init__(status_code=404, detail=detail)


class LightingAvailabilityError(AceReserveException):
    """Raised when lighting is requested for a court that doesn't support it."""

    def __init__(self, detail: str = "Lighting is not available for this court."):
        super().__init__(status_code=400, detail=detail)


class LightingTimeError(AceReserveException):
    """Raised when lighting is requested outside of allowed hours."""

    def __init__(self, detail: str = "Lighting is only available after 18:00."):
        super().__init__(status_code=400, detail=detail)


class FavoriteAlreadyExistsError(AceReserveException):
    """Raised when adding an item to favorites that is already there."""

    def __init__(self, detail: str = "Already in your favorites."):
        super().__init__(status_code=409, detail=detail)


class CoachNotFoundError(AceReserveException):
    """Raised when a requested coach cannot be found."""

    def __init__(self, detail: str = "Coach not found."):
        super().__init__(status_code=404, detail=detail)


class FavoriteNotFoundError(AceReserveException):
    """Raised when attempting to remove a non-existent favorite item."""

    def __init__(self, detail: str = "Item not found in favorites."):
        super().__init__(status_code=404, detail=detail)


class NoTargetTypeError(AceReserveException):
    """Raised when a review is created without a valid target entity."""

    def __init__(self, detail: str = "Review must target at least one entity."):
        super().__init__(status_code=400, detail=detail)


class MoreTargetTypesError(AceReserveException):
    """Raised when a review targets multiple entities simultaneously."""

    def __init__(self, detail: str = "Review must target only one entity."):
        super().__init__(status_code=400, detail=detail)


class ClubNotOpenError(AceReserveException):
    """Raised when a reservation creation is attempted before the club opens."""

    def __init__(self, detail: str = "Club is not open at the specified time."):
        super().__init__(status_code=400, detail=detail)


class ClubClosedError(AceReserveException):
    """Raised when a reservation creation is attempted after the club has closed."""

    def __init__(self, detail: str = "Club is closed at the specified time."):
        super().__init__(status_code=400, detail=detail)
