from sqlalchemy.orm import Session
from models import Shift, ShiftAssignment, Attendance
from datetime import datetime
from utils import haversine
from config import settings
import random
import string
import models, schemas
from pydantic import BaseModel, condecimal
from datetime import date


# class Assign(BaseModel):
#     assig_id: int
    



def assign_shift(db: Session, guard_id: int, post_name: str, postcode: str, lat: float, lon: float):
    shift = Shift(
        guard_id=guard_id,
        post_name=post_name,
        postcode=postcode,
        lat=lat,
        lon=lon
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

# def get_shift(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     return db.query(ShiftAssignment).filter(ShiftAssignment.id == assign_id, ShiftAssignment.user_id == assign_id ).first()



#DATABASE_URL=postgresql+psycopg2://melcombe:fame007dav@localhost:5432/sia
# GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY_HERE



def clock_in(db: Session, guard_lat: condecimal(ge=-90, le=90), guard_lon: condecimal(ge=-180, le=180), max_distance=settings.CLOCKIN_RADIUS_METERS):
    dist = haversine(guard_lat, guard_lon, shift.lat, shift.lon)
    if dist > max_distance:
        raise ValueError(f"Too far from assigned location: {dist:.1f} meters")
    shift.clock_in_time = datetime.utcnow()
    shift.clock_in_lat = guard_lat
    shift.clock_in_lon = guard_lon
    db.commit()
    db.refresh(shift)
    return shift


def generate_random_password(length=6):
    chars = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(random.choices(chars, k=length))





