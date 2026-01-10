from decimal import Decimal, ROUND_HALF_UP
from ..models.court import Court
from ..models.user import User
from ..models.loyalty import LoyaltyLevel
from ..models.reservation import (
    ReservationCreate,
)

DISCOUNTS: dict = {
    LoyaltyLevel.BEGINNER: Decimal("0.00"),
    LoyaltyLevel.SILVER: Decimal("0.05"),
    LoyaltyLevel.GOLD: Decimal("0.10"),
    LoyaltyLevel.PLATINUM: Decimal("0.15"),
}

EXTRAS_PRICES = {
    "racket": Decimal("5.00"),
    "balls": Decimal("3.00"),
    "lighting": Decimal("10.00"),
}

LIGHTING_START_HOUR = 19
POINTS_PER_HOUR = 10


def calculate_price(court: Court, data: ReservationCreate, user: User) -> Decimal:
    hours = Decimal(data.duration_minutes) / Decimal(60)
    base_price = Decimal(str(court.price_per_hour)) * hours

    extras_cost = Decimal("0.00")
    if data.rent_racket:
        extras_cost += EXTRAS_PRICES["racket"]
    if data.rent_balls:
        extras_cost += EXTRAS_PRICES["balls"]
    if data.wants_lighting:
        extras_cost += EXTRAS_PRICES["lighting"]

    total_before_discount = base_price + extras_cost

    level = LoyaltyLevel.BEGINNER
    if user.loyalty:
        level = user.loyalty.level

    discount_percent = DISCOUNTS.get(level, Decimal("0.00"))
    discount_amount = total_before_discount * discount_percent

    final_price = total_before_discount - discount_amount

    return final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_earned_points(duration_minutes: int) -> int:
    return int((duration_minutes / 60) * POINTS_PER_HOUR)
