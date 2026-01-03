from sqlmodel import Session, select
from ..models.user import User
from ..models.loyalty import LoyaltyAccount, LoyaltyLevel
from ..core.exceptions import LoyaltyAccountNotFoundError


def update_loyalty_level(account: LoyaltyAccount, points_change: int) -> None:
    account.points += points_change

    if account.points < 0:
        account.points = 0

    if account.points >= 300:
        account.level = LoyaltyLevel.PLATINUM
    elif account.points >= 150:
        account.level = LoyaltyLevel.GOLD
    elif account.points >= 50:
        account.level = LoyaltyLevel.SILVER
    else:
        account.level = LoyaltyLevel.BEGINNER


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
    
    update_loyalty_level(loyalty_account, adjustment)

    session.add(loyalty_account)
    session.commit()
    session.refresh(loyalty_account)

    return loyalty_account
