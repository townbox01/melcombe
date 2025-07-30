from fastapi import FastAPI, Depends, HTTPException,  FastAPI, File, UploadFile, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.responses import HTMLResponse
from jose import JWTError, jwt
import shutil
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from config import settings
import os
from config import UPLOAD_DIR  # ← import your config
from crud import generate_random_password
from passlib.hash import bcrypt
from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from database import get_db, engine
from datetime import datetime
import models
from utils import haversine
import schemas
import crud
from datetime import date
from mail_utils import register_email
import utils
from admin import setup_admin
import asyncio
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
from security import verify_password
from auth import create_access_token, get_current_user,create_refresh_token, REFRESH_SECRET_KEY, ALGORITHM
from sqlalchemy import select
from fastapi import Request
#models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Security Company Shift & Clock-in API")


app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


setup_admin(app)

REQUEST_COUNT = Counter('request_count', 'Total HTTP requests')

@app.middleware("http")
async def prometheus_middleware(request, call_next):
    REQUEST_COUNT.inc()
    response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)




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





@app.post("/shifts/clock-out")
async def clock_out(
    data: schemas.ClockInData,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    attendance = db.query(models.Attendance).filter(
        models.Attendance.assign_id == data.assign_id,
        models.Attendance.user_id == current_user.id,
        models.Attendance.clock_in_time.isnot(None),
        models.Attendance.clock_out_time.is_(None),
        models.Attendance.status == "ongoing"
    ).first()

    if not attendance:
        raise HTTPException(
            status_code=400,
            detail="No active attendance record found for clock-out."
        )

    shift_assignment = db.query(models.ShiftAssignment).filter(
        models.ShiftAssignment.id == data.assign_id,
        models.ShiftAssignment.user_id == current_user.id
    ).first()

    if not shift_assignment:
        raise HTTPException(status_code=404, detail="Shift assignment not found.")

    try:
        shift_lat = shift_assignment.shift.latitude
        shift_lon = shift_assignment.shift.longitude
        max_distance = settings.CLOCKIN_RADIUS_METERS

        dist = haversine(
            float(data.guard_lat),
            float(data.guard_lon),
            float(shift_lat),
            float(shift_lon)
        )

        if dist > max_distance:
            raise ValueError(f"Too far from assigned location: {dist:.1f} meters")

        attendance.clock_out_time = datetime.utcnow()
        attendance.clock_out_lat = data.guard_lat
        attendance.clock_out_lon = data.guard_lon
        attendance.status = "completed"

        db.commit()
        db.refresh(attendance)

        return {"message": "Clock-out successful"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Clock-out failed.")






#clock in her

@app.post("/shifts/clock-in")
async def clock_in(data: schemas.ClockInData, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    shift_assigned = db.query(models.ShiftAssignment).filter(models.ShiftAssignment.id == data.assign_id, models.ShiftAssignment.user_id == current_user.id).first()
    

    existing_attendance = db.query(models.Attendance).filter(
        models.Attendance.assign_id == data.assign_id,
        models.Attendance.user_id == current_user.id
    ).first()

    
    if not shift_assigned:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    if existing_attendance:
        raise HTTPException(
            status_code=400,
            detail="You have already clocked in for this shift and not clocked out.")
    try:
        shift_lat, shift_lon = shift_assigned.shift.latitude, shift_assigned.shift.longitude
        max_distance=settings.CLOCKIN_RADIUS_METERS
        dist = haversine(float(data.guard_lat), float(data.guard_lon), float(shift_lat), float(shift_lon))

        if dist > max_distance:
            raise ValueError(f"Too far from assigned location: {dist:.1f} meters")
        
        clock_in = models.Attendance(
            clock_in_time = datetime.utcnow(),
            user_id = current_user.id,
            assign_id = data.assign_id,
            clock_in_lon  = data.guard_lon,
            clock_in_lat = data.guard_lat,
            status = 'ongoing'

        )

        db.add(clock_in)
        db.commit()
        db.refresh(clock_in)

        return {"Message": "Guard Clock in Successful"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))







@app.put("/update/{user_id}")
async def upload_files(
    user_id: int,
    badge_pic: UploadFile = File(...),
    profile_pic: UploadFile = File(...),
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

    if profile_pic:
        
        image_path = os.path.join(UPLOAD_DIR, f"{uuid4()}{profile_pic.filename}")
    

        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(profile_pic.file, buffer)

        user.profile_pic = image_path

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
async def admin_create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    password = generate_random_password()
    hashed_password = bcrypt.hash(password)
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
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user_id":user.id}




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
    







@app.get('/users_not_assigned', response_model=list[schemas.UserTOAssignResponse])
def get_users_not_assigned_to_shift(request:Request, data: schemas.UserTOAssign, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Subquery: all user_ids already assigned to the shift
    subquery = (
        select(models.ShiftAssignment.user_id)
        .where(models.ShiftAssignment.shift_id == data.shift_id)
        .subquery()
    )


    # Main query: users whose IDs are NOT in the above subquery
    users = db.query(models.User).filter(models.User.id.notin_(subquery)).all()

        # Convert to list of UserSummary
    return [
        schemas.UserTOAssignResponse(
            id=u.id,
            profile_pic=u.profile_pic,
            name=f"{u.first_name or ''} {u.last_name or ''}".strip()
        )
        for u in users
    ]
    





@app.post("/assign_shift")
def assign_shift(data: schemas.ShiftAssignRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # 1. Check if shift exists
    shift = db.query(models.Shift).filter(models.Shift.id == data.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    # 2. Ensure the shift date is in the future
    today = date.today()
    if shift.date < today:
        raise HTTPException(status_code=400, detail="Cannot assign staff to a past shift")

    # 3. Validate staff IDs
    users = db.query(models.User).filter(models.User.id.in_(data.staff_ids)).all()
    found_ids = {user.id for user in users}
    missing_ids = set(data.staff_ids) - found_ids
    if missing_ids:
        raise HTTPException(status_code=400, detail=f"Invalid user IDs: {list(missing_ids)}")

    # 4. Check already assigned staff to prevent duplication
    existing = db.query(models.ShiftAssignment).filter(
        models.ShiftAssignment.shift_id == data.shift_id,
        models.ShiftAssignment.user_id.in_(data.staff_ids)
    ).all()

    already_assigned_ids = {a.user_id for a in existing}
    new_user_ids = set(data.staff_ids) - already_assigned_ids

    if not new_user_ids:
        return {"msg": "All users are already assigned to this shift"}

    # 5. Create new assignments
    new_assignments = [
        models.ShiftAssignment(
            shift_id=data.shift_id,
            user_id=user_id,
            assigned_by=current_user.id,
            assigned_at=datetime.utcnow()
        )
        for user_id in new_user_ids
    ]

    db.add_all(new_assignments)
    db.commit()

    return {
        "msg": f"{len(new_assignments)} user(s) assigned successfully",
        "assigned_user_ids": list(new_user_ids)
    }






@app.post("/shift_assignment/respond")
def respond_shift_assignment(
    data: schemas.ShiftResponseUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(models.ShiftAssignment).filter(models.ShiftAssignment.id == data.assignment_id, models.ShiftAssignment.user_id == current_user.id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    assignment.response = data.response
    db.commit()
    db.refresh(assignment)
    return {
        "msg": f"Shift assignment {assignment.id} marked as {assignment.response}"
    }




@app.post("/create_shifts", status_code=201)
def create_shift(shift_in: schemas.ShiftCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Validate shift date is not in the past
    if shift_in.date < date.today():
        raise HTTPException(status_code=400, detail="Shift date must be today or in the future")

    # Optional: Validate that start_time is before end_time
    if shift_in.start_time >= shift_in.end_time:
        raise HTTPException(status_code=400, detail="Shift start time must be before end time")

    # Create Shift instance
    shift = models.Shift(
        place_name=shift_in.place_name,
        postcode=shift_in.postcode,
        latitude=shift_in.latitude,
        longitude=shift_in.longitude,
        date=shift_in.date,
        start_time=shift_in.start_time,
        end_time=shift_in.end_time,
        created_by=current_user.id  # assuming you have auth
    )

    db.add(shift)
    db.commit()
    db.refresh(shift)

    return {"msg": "Shift created successfully", "shift_id": shift.id}





#all shifts assigned to a user
@app.get("/fetch_my_shifts", response_model=list[schemas.ShiftCreate])
def fetch_user_shifts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    assignments = (
        db.query(models.ShiftAssignment)
        .filter(models.ShiftAssignment.user_id == current_user.id)
        .all()
    )
    
    if not assignments:
        raise HTTPException(status_code=404, detail="No shifts found for user")

    # Extract all shift details from assignments
    shifts = [assignment.shift for assignment in assignments]

    return shifts


#all shifts 
@app.get("/fetch_all_shifts", response_model=list[schemas.AllShifts])
def fetch_user_shifts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    shifts = db.query(models.Shift).all()
    
    if not shifts:
        raise HTTPException(status_code=404, detail="No shift")

    # Extract all shift details from assignments
    #shifts = [assignment.shift for assignment in assignments]

    return shifts



@app.put("/update_shift")
def shift_update(
    data: schemas.UpdateShift,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    shift = db.query(models.Shift).filter(models.Shift.id == data.shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    

    shift.date = data.date
    shift.start_time = data.start_time
    shift.end_time = data.end_time
    db.commit()
    db.refresh(shift)

    return {
        "msg": f"Shift {shift.id} updated successfully"
    }
