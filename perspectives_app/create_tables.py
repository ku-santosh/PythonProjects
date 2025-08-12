from perspectives_app.app.database.database import engine
from perspectives_app.app.models.model_perspective import Base

Base.metadata.create_all(bind=engine)
