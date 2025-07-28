from sqladmin import Admin, ModelView
from fastapi import FastAPI
from models import User, Shift, ShiftAssignment, Attendance
from database import engine

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.staff_id]
    column_searchable_list = [User.email, User.staff_id]
    column_sortable_list = [User.id, User.email]
    can_delete = True
    icon = "fa fa-user"



class ShiftAdmin(ModelView, model=Shift):
    column_list = [
        Shift.id,
        Shift.place_name,
        Shift.postcode,
        Shift.date,
        Shift.start_time,
        Shift.end_time,
        Shift.created_by
    ]

    column_labels = {
        Shift.id: "ID",
        Shift.place_name: "Place Name",
        Shift.postcode: "Postcode",
        Shift.date: "Date",
        Shift.start_time: "Start Time",
        Shift.end_time: "End Time",
        Shift.created_by: "Created By",
    }

    column_sortable_list = [Shift.date, Shift.start_time, Shift.end_time]
    form_excluded_columns = [Shift.assignments]




class ShiftAssignmentAdmin(ModelView, model=ShiftAssignment):
    column_list = [
        ShiftAssignment.id,
        ShiftAssignment.shift_id,
        ShiftAssignment.user_id,
        ShiftAssignment.assigned_by,
        ShiftAssignment.assigned_at,
        ShiftAssignment.response,
        ShiftAssignment.status
    ]

    column_labels = {
        ShiftAssignment.id: "ID",
        ShiftAssignment.shift_id: "Shift",
        ShiftAssignment.user_id: "User",
        ShiftAssignment.assigned_by: "Assigned By",
        ShiftAssignment.assigned_at: "Assigned At",
        ShiftAssignment.response: "Response",
        ShiftAssignment.status: "Status",
    }

    column_sortable_list = [
        ShiftAssignment.assigned_at,
        ShiftAssignment.status,
        ShiftAssignment.response
    ]

    form_excluded_columns = [
        ShiftAssignment.shift,
        ShiftAssignment.user,
        ShiftAssignment.assigned_by_user
    ]




class AttendanceAdmin(ModelView, model=Attendance):
    column_list = [
        Attendance.id,
        Attendance.assign_id,
        Attendance.user_id,
        Attendance.clock_in_time,
        Attendance.clock_in_lat,
        Attendance.clock_in_lon,
        Attendance.clock_out_time,
        Attendance.clock_out_lat,
        Attendance.clock_out_lon,
        Attendance.status,
    ]

    column_searchable_list = [Attendance.user_id, Attendance.assign_id, Attendance.status]
    column_sortable_list = [Attendance.id, Attendance.clock_in_time, Attendance.clock_out_time]
    can_delete = True
    name = "Attendance"
    name_plural = "Attendances"
    icon = "fa-solid fa-calendar-check"



def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(ShiftAdmin)
    admin.add_view(ShiftAssignmentAdmin)
    admin.add_view(AttendanceAdmin)




