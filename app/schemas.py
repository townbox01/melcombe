from pydantic import BaseModel, constr, condecimal, EmailStr, confloat
from typing import Optional
from datetime import datetime
from datetime import date, time
from typing import List

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
    assign_id: int
    user_id: int
    # guard_lat: condecimal(ge=-90, le=90)
    # guard_lon: condecimal(ge=-180, le=180)
    # guard_lat: confloat(ge=-90, le=90)
    # guard_lon: confloat(ge=-180, le=180)

    guard_lat: float
    guard_lon: float





class UserCreate(BaseModel):
    email: EmailStr


class UserTOAssign(BaseModel):
    shift_id: int


class UserTOAssignResponse(BaseModel):
    id: int
    profile_pic: str | None = None
    name: str

    class Config:
        orm_mode = True



class ShiftResponseUpdate(BaseModel):
    assignment_id: int
    response: str  # accept or reject







class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    badge: Optional[str] = None
    badge_exp: Optional[date] = None
    badge_pic: Optional[str] = None
    profile_pic: Optional[str] = None
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







class ShiftCreate(BaseModel):
    place_name: Optional[str]
    company: Optional[str]
    postcode: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    date: date
    start_time: time
    end_time: time






class ShiftAssignRequest(BaseModel):
    shift_id: int
    staff_ids: List[int]
    #assigned_by: int





class UpdateShift(BaseModel):
    shift_id: int
    date: date
    start_time: time
    end_time: time





class AllShifts(BaseModel):
    id: int
    company: Optional[str] = None 
    place_name: str
    postcode: str
    start_time: time
    end_time: time

    class Config:
        orm_mode = True




class ShiftAssignedResponse(BaseModel):
    id: int                      # from Shift
    assign_id: int                      # from Shift
    place_name: Optional[str]
    company: Optional[str]
    postcode: Optional[str]
    latitude: Optional[str]
    longitude: Optional[str]
    date: date
    start_time: time
    end_time: time
    response: Optional[str]      # from ShiftAssignment
    status: Optional[str]        # from ShiftAssignment

    clock_in_time: Optional[datetime] = None
    clock_out_time: Optional[datetime] = None
    attendance_status: Optional[str] = None  # from Attendance

    class Config:
        orm_mode = True