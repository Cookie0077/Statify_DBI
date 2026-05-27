from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import Base
from python_client import sp as importedSpotify

class BaseAPI:
    sp = importedSpotify

    def get_or_404(self, db: Session, model: Base, item_id: int):
        item = db.query(model).filter(model.Id == item_id).first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Eintrag in {model.__tablename__} mit ID {item_id} nicht gefunden")

        return item


