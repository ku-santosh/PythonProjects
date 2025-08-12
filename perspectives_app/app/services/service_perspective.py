# Contains the business logic for interacting with the database.
#
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Optional
from ..models.perspective import Perspective as PerspectiveModel
from ..schemas.perspective import PerspectiveCreate, PerspectiveUpdate


class PerspectiveService:
    """Service class for performing CRUD operations on Perspective data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_perspectives(self) -> List[PerspectiveModel]:
        """
        Retrieves all perspective records from the database.

        Equivalent SQL query:
        SELECT id, username, layout_name, column_state, sort_model, filter_model, updated_by, updated_time
        FROM skg023.recsui.perspectives;
        """
        result = await self.db.execute(select(PerspectiveModel))
        perspectives = result.scalars().all()
        return perspectives

    async def get_perspective_by_id(self, perspective_id: int) -> Optional[PerspectiveModel]:
        """Retrieves a single perspective record by its ID."""
        result = await self.db.execute(select(PerspectiveModel).filter(PerspectiveModel.id == perspective_id))
        return result.scalars().first()

    async def create_perspective(self, perspective_in: PerspectiveCreate) -> PerspectiveModel:
        """Creates a new perspective record in the database."""
        # Create a new model instance from the input schema data
        new_perspective = PerspectiveModel(**perspective_in.model_dump())
        self.db.add(new_perspective)
        await self.db.commit()
        await self.db.refresh(new_perspective)
        return new_perspective

    async def update_perspective(self, perspective_id: int, perspective_in: PerspectiveUpdate) -> Optional[
        PerspectiveModel]:
        """Updates an existing perspective record."""
        # Find the existing perspective by ID
        existing_perspective = await self.db.get(PerspectiveModel, perspective_id)

        if not existing_perspective:
            return None

        # Update the model attributes with the new data from the schema
        update_data = perspective_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing_perspective, key, value)

        await self.db.commit()
        await self.db.refresh(existing_perspective)
        return existing_perspective

    async def delete_perspective(self, perspective_id: int) -> bool:
        """Deletes a perspective record by its ID."""
        perspective_to_delete = await self.db.get(PerspectiveModel, perspective_id)
        if not perspective_to_delete:
            return False

        await self.db.delete(perspective_to_delete)
        await self.db.commit()
        return True