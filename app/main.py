from fastapi import FastAPI, Depends, HTTPException,  FastAPI, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
import shutil
import os
from config import UPLOAD_DIR  # ← import your config
from crud import generate_random_password
from passlib.hash import bcrypt
from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from database import get_db, engine
from datetime import datetime
import models
import schemas
import crud
from datetime import date
from mail_utils import register_email
import utils
from admin import setup_admin
import asyncio
from uuid import uuid4
from security import verify_password
from auth import create_access_token, get_current_user,create_refresh_token, REFRESH_SECRET_KEY, ALGORITHM


#models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Security Company Shift & Clock-in API")

setup_admin(app)




# Allowed extensions and MIME types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "application/pdf"
}

@app.post("/shifts/", response_model=schemas.ShiftOut)
async def assign_shift(data: schemas.ShiftAssign, db: Session = Depends(get_db)):
    lat, lon = await utils.get_lat_lon(data.postcode)
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Could not resolve postcode location")
    shift = crud.assign_shift(db, data.guard_id, data.post_name, data.postcode, lat, lon)
    return shift

@app.post("/shifts/clock-in/", response_model=schemas.ShiftOut)
async def clock_in(data: schemas.ClockInData, db: Session = Depends(get_db)):
    shift = crud.get_shift(db, data.shift_id)
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    try:
        updated_shift = crud.clock_in(db, shift, float(data.latitude), float(data.longitude))
        return updated_shift
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




@app.put("/update/{user_id}")
async def upload_files(
    user_id: int,
    badge_pic: UploadFile = File(...),
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    acct_num: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    badge: Optional[str] = Form(None),
    dob: Optional[date] = Form(None),
    share_code: Optional[str] = Form(None),
    ni: Optional[str] = Form(None),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    print(user)
    if badge_pic:
        
        image_path = os.path.join(UPLOAD_DIR, f"{uuid4()}{badge_pic.filename}")
    

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(badge_pic.file, buffer)

        user.badge_pic = image_path

        print(image_path)

        # Update fields
    if first_name is not None:
        user.first_name = first_name

    if last_name is not None:
        user.last_name = last_name

    if last_name is not None:
        user.ni = ni

    db.commit()
    db.refresh(user)

    return user



@app.post("/create-user")
async def admin_create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    password = generate_random_password()
    print(password)
    hashed_password = bcrypt.hash(password)
    print(hashed_password)
    count = db.query(models.User).count()
    staff_id = f"GUARD-{count+1:04d}"
    new_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        staff_id = staff_id
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(new_user.id, new_user.email, password)

    await register_email(new_user.email, new_user.staff_id, password)

    # return raw password to be sent via email or SMS
    return {"msg": "User created", "temporary_password": password}





from fastapi import UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import shutil
from uuid import uuid4
from typing import Optional

# Constants (define these somewhere in your config)
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
UPLOAD_DIR = "uploads"  # Make sure this directory exists


def validate_upload_file(upload_file: UploadFile):
    filename = upload_file.filename
    content_type = upload_file.content_type
    ext = os.path.splitext(filename)[1].lower()

    if content_type not in ALLOWED_MIME_TYPES:
        # Force-read a few bytes to "consume" the file and avoid decode error
        _ = upload_file.file.read(10)
        raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")
    
    if ext not in ALLOWED_EXTENSIONS:
        _ = upload_file.file.read(10)
        raise HTTPException(status_code=400, detail=f"Invalid file extension: {ext}")
    
    # Reset pointer for further reading if needed
    upload_file.file.seek(0)

def save_uploaded_file(upload_file: UploadFile, folder: str = UPLOAD_DIR) -> str:
    # Create upload directory if it doesn't exist
    os.makedirs(folder, exist_ok=True)
    
    ext = os.path.splitext(upload_file.filename)[1].lower()
    file_name = f"{uuid4()}{ext}"
    file_path = os.path.join(folder, file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path




# @app.post("/signin")
# async def signin(user_credentials: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(models.User).where(models.User.username == user_credentials.username))
#     user = result.scalars().first()

#     if not user or not await verify_password(user_credentials.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
    
#     account = await db.execute(select(models.Account).where(models.Account.user_id == user.id))
#     details = account.scalars().first()

#     if not details:
#         raise HTTPException(status_code=404, detail="Account not found")
    
#     token = await create_access_token({"sub": user.username, "user_id": user.id})
#     return {
#         "access_token": token,
#         "token_type": "bearer",
#         "account_number": details.account_number,
#         "user_id": details.user_id,
#         "balance": details.balance
#     }




@app.post("/login")
def login_user(data: schemas.LoginInput, db: Session = Depends(get_db)):
    user = db.query(models.User).filter((models.User.email == data.identifier) | (models.User.staff_id == data.identifier)).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}




@app.post("/refresh", response_model=dict)
def refresh_token(payload: schemas.RefreshInput):
    try:
        decoded = jwt.decode(payload.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = decoded.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        access_token = create_access_token({"sub": user_id})
        return {"access_token": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")