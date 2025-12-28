from ..models.court import Court
from ..models.user import User
from decimal import Decimal
from ..models.loyalty import LoyaltyAccount, LoyaltyLevel

DISCOUNTS: dict = {"beginner": 0.0, "silver": 0.05, "gold": 0.1, "platinum": 0.15}
POINTS_PER_HOUR = 10


def calculate_price(court: Court, duration_minutes: int, user: User) -> Decimal:
    hours = Decimal((duration_minutes) / (60))
    base_price = court.price_per_hour * hours

    level = "beginner"
    if user.loyalty:
        level = user.loyalty.level.value

    discount_percent = DISCOUNTS.get(level, 0.0)
    discount_amount = base_price * Decimal(discount_percent)
    final_price = base_price - discount_amount

    return final_price


def calculate_earned_points(duration_minutes: int) -> int:
    points_earned: int = int((duration_minutes / 60) * 10)

    return points_earned


def update_loyalty_level(
    user: User, loyalty: LoyaltyAccount, points_earned: int
) -> None:
    if not user.loyalty:
        return

    user.loyalty.points += points_earned

    if user.loyalty.points >= 1000:
        user.loyalty.level = LoyaltyLevel.PLATINUM
    elif user.loyalty.points >= 500:
        user.loyalty.level = LoyaltyLevel.GOLD
    elif user.loyalty.points >= 200:
        user.loyalty.level = LoyaltyLevel.SILVER
    else:
        user.loyalty.level = LoyaltyLevel.BEGINNER
