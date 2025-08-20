from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(prefix="/banners", tags=["Banners"])

# Get all banners
@router.get("/", response_model=List[schemas.Banner])
def list_banners(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db)):
    return crud.get_banners(db, skip=skip, limit=limit)

# Get one banner
@router.get("/{banner_id}", response_model=schemas.Banner)
def get_banner(banner_id: int, db: Session = Depends(database.get_db)):
    db_banner = crud.get_banner(db, banner_id)
    if not db_banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return db_banner

# Create banner
@router.post("/", response_model=schemas.Banner)
def create_banner(banner: schemas.BannerCreate, db: Session = Depends(database.get_db)):
    return crud.create_banner(db, banner)

# Update banner
@router.put("/{banner_id}", response_model=schemas.Banner)
def update_banner(banner_id: int, banner: schemas.BannerUpdate, db: Session = Depends(database.get_db)):
    db_banner = crud.update_banner(db, banner_id, banner)
    if not db_banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return db_banner

# Delete banner
@router.delete("/{banner_id}")
def delete_banner(banner_id: int, db: Session = Depends(database.get_db)):
    db_banner = crud.delete_banner(db, banner_id)
    if not db_banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return {"message": "Banner deleted successfully"}
