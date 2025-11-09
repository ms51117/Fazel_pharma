# admin_panel/views.py

from sqladmin import ModelView, BaseView, expose
from starlette.requests import Request
from sqlalchemy import func, select
from datetime import date
from admin_panel.dependencies import admin_instance
# --- ایمپورت‌های لازم ---
from database import async_session_maker
from app.models.user import User
from app.models.patient import Patient
from app.models.drug import Drug
from app.models.order import Order
from app.models.order_list import OrderList

from jinja2 import Environment, ChoiceLoader, FileSystemLoader

# admin_panel/views.py

import os
import jinja2
import sqladmin
from starlette.templating import Jinja2Templates
from sqladmin import BaseView, expose
from starlette.requests import Request
from sqlalchemy import func, select
from datetime import date

# (مسیرها را از فایل database.py خودتان کپی کنید)
from database import async_session_maker
from app.models.order import Order
from app.models.order_list import OrderList
from pathlib import Path


# --- بخش جدید: ساخت موتور تمپلیت هوشمند (نسخه اصلاح شده) ---

# 1. مسیر پوشه تمپلیت‌های داخلی کتابخانه sqladmin را پیدا می‌کنیم
templates_path = Path(__file__).parent / "templates"
print(templates_path)

env = Environment(loader=FileSystemLoader(str(templates_path)))

# اگر فیلتر سفارشی داری (مثلا format_price)، اینجا می‌تونی اضافه کنی:
# env.filters["format_price"] = lambda x: f"{x:,.0f} تومان"

templates = Jinja2Templates(env=env)


class DashboardView(BaseView):
    name = "Dashboard"
    icon = "fa fa-chart-line"   # آیکون در sidebar

    @expose("/dashboard", methods=["GET"])
    async def dashboard_page(self, request: Request):
        # اینجا داده‌ها رو آماده کن
        total_users = 125
        total_orders = 53
        total_drugs = 18

        context = {
            "request": request,
            "admin": admin_instance,  # الزامی برای sidebar و navbar
            "total_users": total_users,
            "total_orders": total_orders,
            "total_drugs": total_drugs,
        }

        return templates.TemplateResponse("sqladmin/dashboard.html", context)
# --- نماهای مربوط به مدل‌ها ---
class UsersAdmin(ModelView, model=User):
    column_list = [User.user_id, User.full_name, User.is_active, User.mobile_number]
    column_searchable_list = [User.mobile_number, User.full_name]
    column_sortable_list = [User.user_id, User.full_name]
    name = "کاربر"
    name_plural = "کاربران"
    icon = "fa-solid fa-user"

class DrugsAdmin(ModelView, model=Drug):
    column_list = [Drug.drugs_id, Drug.drug_lname]
    name = "دسته بندی"
    name_plural = "دسته بندی ها"
    icon = "fa-solid fa-folder-open"

class PatientsAdmin(ModelView, model=Patient):
    column_list = [Patient.patient_id, Patient.full_name, Patient.telegram_id]
    column_labels = {Patient.patient_id: "ایدی بیمار", Patient.full_name: "نام بیمار"}
    name = "بیمار"
    name_plural = "بیماران"
    icon = "fa-solid fa-user-injured"

# ... هر ModelView جدیدی که می‌خواهید اضافه کنید را اینجا قرار دهید
