from pydantic import BaseModel, constr, condecimal, EmailStr
from typing import Optional
from datetime import datetime
from datetime import date



class ShiftAssign(BaseModel):
    guard_id: int
    post_name: str
    postcode: constr(min_length=5, max_length=10)

class ShiftOut(BaseModel):
    id: int
    guard_id: int
    post_name: str
    postcode: str
    lat: float
    lon: float
    clock_in_time: Optional[datetime]

    class Config:
        orm_mode = True

class ClockInData(BaseModel):
    shift_id: int
    latitude: condecimal(ge=-90, le=90)
    longitude: condecimal(ge=-180, le=180)





class UserCreate(BaseModel):
    email: EmailStr





class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    badge: Optional[str] = None
    badge_exp: Optional[date] = None
    badge_pic: Optional[str] = None
    dob: Optional[date] = None
    acc_num: Optional[str] = None
    right_to_wrk: Optional[str] = None
    ni: Optional[str] = None
    utr: Optional[str] = None
    share_code: Optional[str] = None
    brit_id: Optional[str] = None
    emergency_cntat_name: Optional[str] = None
    emergency_cntact_num: Optional[str] = None
    relationship_wit_cntat: Optional[str] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None
    role: Optional[str] = None



class LoginInput(BaseModel):
    identifier: str  # email or username
    password: str


class RefreshInput(BaseModel):
    refresh_token: str