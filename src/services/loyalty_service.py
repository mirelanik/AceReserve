from decimal import Decimal
from sqlmodel import Session, select
from ..models.court import Court
from ..models.user import User
from ..models.loyalty import LoyaltyAccount, LoyaltyLevel
from ..core.exceptions import LoyaltyAccountNotFoundError

DISCOUNTS: dict = {
    LoyaltyLevel.BEGINNER: 0.0,
    LoyaltyLevel.SILVER: 0.05,
    LoyaltyLevel.GOLD: 0.1,
    LoyaltyLevel.PLATINUM: 0.15,
}
POINTS_PER_HOUR = 10


def calculate_price(court: Court, duration_minutes: int, user: User) -> Decimal:
    hours = Decimal((duration_minutes) / (60))
    base_price = court.price_per_hour * hours

    level = LoyaltyLevel.BEGINNER
    if user.loyalty:
        level = user.loyalty.level

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

    if user.loyalty.points >= 300:
        user.loyalty.level = LoyaltyLevel.PLATINUM
    elif user.loyalty.points >= 150:
        user.loyalty.level = LoyaltyLevel.GOLD
    elif user.loyalty.points >= 50:
        user.loyalty.level = LoyaltyLevel.SILVER
    else:
        user.loyalty.level = LoyaltyLevel.BEGINNER


def get_loyalty_info(user: User) -> dict:
    if not user.loyalty:
        return {"points": 0, "level": LoyaltyLevel.BEGINNER}

    return {"points": user.loyalty.points, "level": user.loyalty.level}


def change_loyalty_points(
    session: Session, user: User, adjustment: int
) -> LoyaltyAccount:
    loyalty_account = session.exec(
        select(LoyaltyAccount).where(LoyaltyAccount.user_id == user.id)
    ).first()

    if not loyalty_account:
        raise LoyaltyAccountNotFoundError()

    update_loyalty_level(user, loyalty_account, adjustment)

    session.add(loyalty_account)
    session.commit()
    session.refresh(loyalty_account)

    return loyalty_account
