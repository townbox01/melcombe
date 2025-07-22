from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Time, Date, Boolean
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime





Base = declarative_base()






class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    email = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    acc_num = Column(String, nullable=True)
    acc_name = Column(String, nullable=True)
    sort_code = Column(String, nullable=True)
    role = Column(String, default="guard")  # e.g., "admin", "guard", "supervisor"
    dob = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    badge = Column(String, nullable=True)
    badge_exp = Column(Date, nullable=True)
    badge_pic = Column(String, nullable=True)
    right_to_wrk = Column(String, nullable=True)
    ni = Column(String, nullable=True)
    utr = Column(String, nullable=True)
    share_code = Column(String, nullable=True)
    brit_id = Column(String, nullable=True)
    emergency_cntat_name = Column(String, nullable=True)
    emergency_cntact_num = Column(String, nullable=True)
    relationship_wit_cntat = Column(String, nullable=True)
    is_completed = Column(Boolean, default=True)
    default_pass_changed = Column(Boolean, default=False)




class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True)
    place_name = Column(String, nullable=False)
    postcode = Column(String, nullable=False)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    location = Column(Geography("POINT"), nullable=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    assignments = relationship("ShiftAssignment", back_populates="shift", cascade="all, delete-orphan")




class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    id = Column(Integer, primary_key=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    shift = relationship("Shift", back_populates="assignments")
    user = relationship("User", backref="assignments")





class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    clock_in_time = Column(DateTime, nullable=True)
    clock_in_lat = Column(Float, nullable=True)
    clock_in_lon = Column(Float, nullable=True)
    clock_out_time = Column(DateTime, nullable=True)
    clock_out_lat = Column(Float, nullable=True)
    clock_out_lon = Column(Float, nullable=True)

    status = Column(String, default="pending")  # pending, completed, missed, etc.
