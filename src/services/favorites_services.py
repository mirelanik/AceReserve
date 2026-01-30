from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from ..models.user import User, Role
from ..models.court import Court
from ..core.exceptions import (
    CourtNotFoundError,
    FavoriteAlreadyExistsError,
    CoachNotFoundError,
)


class FavoritesService:
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_court_to_favorites(self, user: User, court_number: int) -> dict:
        result = await self.session.execute(
            select(Court).where(Court.number == court_number)
        )
        court = result.scalars().first()
        if not court:
            raise CourtNotFoundError()

        if court in user.favorite_courts:
            raise FavoriteAlreadyExistsError()

        user.favorite_courts.append(court)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return {"message": f"Court {court_number} added to favorites."}

    async def remove_court_from_favorites(self, user: User, court_number: int) -> dict:
        result = await self.session.execute(
            select(Court).where(Court.number == court_number)
        )
        court = result.scalars().first()
        if court and court in user.favorite_courts:
            user.favorite_courts.remove(court)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return {"message": f"Court {court_number} removed from favorites."}

    @staticmethod
    def list_favorite_courts(user: User) -> list[Court]:
        return user.favorite_courts

    async def add_coach_to_favorites(self, user: User, coach_id: int) -> dict:
        coach = await self.session.get(User, coach_id)
        if not coach or coach.role != Role.COACH:
            raise CoachNotFoundError()

        await self.session.refresh(user, ["favorite_coaches"])

        if coach in user.favorite_coaches:
            raise FavoriteAlreadyExistsError()

        user.favorite_coaches.append(coach)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return {"message": f"Coach {coach_id} added to favorites."}

    async def remove_coach_from_favorites(self, user: User, coach_id: int) -> dict:
        coach = await self.session.get(User, coach_id)
        await self.session.refresh(user, ["favorite_coaches"])
        if coach and coach in user.favorite_coaches:
            user.favorite_coaches.remove(coach)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return {"message": f"Coach {coach_id} removed from favorites."}

    @staticmethod
    def list_favorite_coaches(user: User) -> list[User]:
        return user.favorite_coaches
