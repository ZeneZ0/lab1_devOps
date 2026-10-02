from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db


def _commit(db: Session):
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Нарушение ограничений БД")


def make_crud_router(model, schema_in, schema_out, prefix: str) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[prefix.strip("/")])

    def get_or_404(db: Session, item_id: int):
        obj = db.get(model, item_id)
        if obj is None:
            raise HTTPException(status_code=404, detail="Не найдено")
        return obj

    @router.post("", response_model=schema_out, status_code=status.HTTP_201_CREATED)
    def create_item(item: schema_in, db: Session = Depends(get_db)):
        obj = model(**item.model_dump())
        db.add(obj)
        _commit(db)
        db.refresh(obj)
        return obj

    @router.get("", response_model=list[schema_out])
    def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return db.query(model).offset(skip).limit(limit).all()

    @router.get("/{item_id}", response_model=schema_out)
    def get_item(item_id: int, db: Session = Depends(get_db)):
        return get_or_404(db, item_id)

    @router.put("/{item_id}", response_model=schema_out)
    def update_item(item_id: int, item: schema_in, db: Session = Depends(get_db)):
        obj = get_or_404(db, item_id)
        for field, value in item.model_dump().items():
            setattr(obj, field, value)
        _commit(db)
        db.refresh(obj)
        return obj

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int, db: Session = Depends(get_db)):
        obj = get_or_404(db, item_id)
        db.delete(obj)
        _commit(db)

    return router