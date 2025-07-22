from sqladmin import Admin, ModelView
from fastapi import FastAPI
from models import User
from database import engine

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.staff_id]
    column_searchable_list = [User.email, User.staff_id]
    column_sortable_list = [User.id, User.email]
    can_delete = True
    icon = "fa fa-user"

def setup_admin(app: FastAPI):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
