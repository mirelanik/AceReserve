from sqlmodel import Session, select
from ..models.user import UserCreate, User, Role
from ..core.exceptions import ExistingUserError, UserNotFoundError
from ..auth.hashing import get_password_hash, verify_password
from ..models.loyalty import LoyaltyAccount
from ..models.reservation import Reservation, ReservationStatus


def _create_loyalty_account(session: Session, new_user: User):
    loyalty = LoyaltyAccount(user_id=new_user.id, points=0)

    session.add(loyalty)
    session.commit()
    session.refresh(new_user)


def create_user(session: Session, user_input: UserCreate) -> User:
    existing_user = session.exec(
        select(User).where(User.email == user_input.email)
    ).first()

    if existing_user:
        raise ExistingUserError()

    hashed_password = get_password_hash(user_input.password)

    new_user = User(
        email=user_input.email,
        hashed_password=hashed_password,
        full_name=user_input.full_name,
        role=Role.USER,
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    _create_loyalty_account(session, new_user)

    return new_user


def create_user_by_admin(
    user_input: UserCreate, role: Role, current_user: User, session: Session
) -> User:
    new_user = create_user(session, user_input)
    new_user.role = role

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


def remove_user_by_admin(user_id: int, current_user: User, session: Session):
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundError()

    user_reservations = session.exec(
        select(Reservation).where(Reservation.user_id == user_id)
    ).all()
    for reservation in user_reservations:
        reservation.status = ReservationStatus.CANCELLED
        session.add(reservation)

    session.delete(user)
    session.commit()
    return {"msg": "User deleted successfully"}


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
