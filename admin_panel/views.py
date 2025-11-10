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

from sqladmin import ModelView, BaseView, expose
from starlette.requests import Request
from .admin_permissions import get_permission_for_table

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




#---------- permission model-------------

# =====> این کلاس پایه جدید را اضافه کنید <=====
class PermissionAwareModelView(ModelView):
    """
    یک کلاس پایه برای ModelView که به صورت خودکار دسترسی‌ها را
    بر اساس جدول UserRolePermission چک می‌کند.
    """

    def is_accessible(self, request: Request) -> bool:
        """کاربر فقط در صورتی این بخش را در منو می‌بیند که حداقل دسترسی "مشاهده" را داشته باشد."""
        permission = get_permission_for_table(request, self.model.__name__)
        # اگر شیء دسترسی وجود داشت و can_view برابر True بود، اجازه دسترسی صادر می‌شود
        return permission is not None and permission.view

    def can_create(self, request: Request) -> bool:
        """دکمه "Create" فقط برای کاربرانی که دسترسی ساختن دارند نمایش داده می‌شود."""
        permission = get_permission_for_table(request, self.model.__name__)
        return permission is not None and permission.insert

    def can_edit(self, request: Request) -> bool:
        """دکمه "Edit" فقط برای کاربرانی که دسترسی ویرایش دارند نمایش داده می‌شود."""
        permission = get_permission_for_table(request, self.model.__name__)
        return permission is not None and permission.update

    def can_delete(self, request: Request) -> bool:
        """دکمه "Delete" فقط برای کاربرانی که دسترسی حذف دارند نمایش داده می‌شود."""
        permission = get_permission_for_table(request, self.model.__name__)
        return permission is not None and permission.delete

    def can_view_details(self, request: Request) -> bool:
        """دکمه "Details" به دسترسی can_view وابسته است."""
        permission = get_permission_for_table(request, self.model.__name__)
        return permission is not None and permission.view

# ---------------------------------


# --- بخش جدید: ساخت موتور تمپلیت هوشمند (نسخه اصلاح شده) ---

# 1. مسیر پوشه تمپلیت‌های داخلی کتابخانه sqladmin را پیدا می‌کنیم
templates_path = Path(__file__).parent / "templates"

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
class UsersAdmin(PermissionAwareModelView, model=User):
    column_list = [User.full_name, User.national_code, User.mobile_number,"role.role_name"]
    column_labels = {User.national_code: "کد ملی", User.full_name: "نام کاربر" , "role.role_name" : "نقش کاربر"}
    column_searchable_list = [User.mobile_number]
    column_sortable_list = [User.user_id, User.full_name]
    name = "کاربر"
    name_plural = "کاربران"
    icon = "fa-solid fa-user"

class DrugsAdmin(PermissionAwareModelView, model=Drug):
    column_list = [Drug.drugs_id, Drug.drug_lname]
    name = "دسته بندی"
    name_plural = "دسته بندی ها"
    icon = "fa-solid fa-folder-open"

class PatientsAdmin(PermissionAwareModelView, model=Patient):
    column_list = [Patient.patient_id, Patient.full_name, Patient.telegram_id]
    column_labels = {Patient.patient_id: "ایدی بیمار", Patient.full_name: "نام بیمار"}
    name = "بیمار"
    name_plural = "بیماران"
    icon = "fa-solid fa-user-injured"

# ... هر ModelView جدیدی که می‌خواهید اضافه کنید را اینجا قرار دهید

