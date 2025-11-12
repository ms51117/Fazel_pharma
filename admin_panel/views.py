# admin_panel/views.py

from sqladmin import ModelView, BaseView, expose
from starlette.requests import Request
from sqlalchemy import func, select
from datetime import date

from wtforms.validators import Optional

from admin_panel.dependencies import admin_instance
# --- ایمپورت‌های لازم ---
from database import async_session_maker
from app.models.user import User
from app.models.patient import Patient
from app.models.drug import Drug
from app.models.order import Order
from app.models.order_list import OrderList
from app.core.enums import OrderStatusEnum
from markupsafe import Markup

from sqladmin.widgets import AjaxSelect2Widget
from app.models.disease_type import DiseaseType

from jinja2 import Environment, ChoiceLoader, FileSystemLoader

# admin_panel/views.py
from wtforms.fields import PasswordField  # <--- این را اضافه کنید
from security import get_password_hash         # <--- و این را هم اضافه کنید


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

    # ستون‌هایی که در نمای لیست و جزئیات "نمایش داده نمی‌شوند".
    # این مهم‌ترین بخش برای مخفی کردن هش است.
    # column_exclude_list = [User.hashed_password,User.is_verified,User.is_active,User.last_login,User.login_attempts,User.updated_at,User.created_at]
    column_details_exclude_list = [User.hashed_password,
                                   User.is_verified,
                                   User.is_active,
                                   User.last_login,
                                   User.login_attempts,
                                   User.updated_at,
                                   User.created_at,
                                   User.payment_list,
                                   User.order,
                                   User.messages,
                                   User.role_id
                                   ]


    form_columns = [
        User.full_name,
        User.mobile_number,
        User.national_code,
        User.telegram_id,
        User.address,
        User.role,
    ]



    column_labels = {User.national_code: "کد ملی",
                     User.full_name: "نام کاربر" ,
                     "role.role_name" : "نقش کاربر",
                     User.address: "آدرس",
                     User.mobile_number: "شماره همراه",
                     User.user_id : "کد کاربر",
                     User.role: "نقش کاربر",
                     User.telegram_id:"ایدی تلگرام"

                     }
    column_searchable_list = [User.mobile_number]
    column_sortable_list = [User.user_id, User.full_name]
    name = "کاربر"
    name_plural = "کاربران"
    icon = "fa-solid fa-user"



class DiseaseTypeAdmin(PermissionAwareModelView, model=DiseaseType):
    name = "نوع بیماری"
    name_plural = "انواع بیماری"
    icon = "fa-solid fa-tags"
    column_list = [DiseaseType.diseases_type_id,DiseaseType.diseases_name,DiseaseType.diseases_explain]
    column_labels = {DiseaseType.diseases_type_id : "کد دسته بندی",
                     DiseaseType.diseases_name:"نام دسته بندی",
                     DiseaseType.diseases_explain:"توضیحات دسته بندی"
                     }
    column_details_exclude_list = [DiseaseType.updated_at,
                                   DiseaseType.created_at,
                                   DiseaseType.drug,
                                   ]
    form_excluded_columns = [DiseaseType.updated_at,
                                   DiseaseType.created_at,
                                   DiseaseType.drug,
                                   ]
    # این خط بسیار مهم است
    # به sqladmin می‌گوید که فیلد 'name' از این مدل برای جستجوی ایجکس قابل استفاده است
    # 'name' را با نام فیلدی که می‌خواهید در آن جستجو کنید جایگزین کنید
    column_ajax_lookups = ["diseases_name"] # برای مثال: نام نوع بیماری

class DrugsAdmin(PermissionAwareModelView, model=Drug):
    column_list = [Drug.drugs_id, Drug.drug_pname,Drug.drug_lname,Drug.price]
    name = "دارو ها"
    name_plural = "دارو ها"
    icon = "fa-solid fa-folder-open"

    column_details_exclude_list = [Drug.updated_at,
                                   Drug.created_at,
                                   Drug.order_list,
                                   ]
    form_excluded_columns = [Drug.updated_at,
                            Drug.created_at,
                            Drug.order_list,
                            ]

    column_labels = {Drug.drugs_id : "کد دارو",
                     Drug.drug_pname : "نام فارسی",
                     Drug.drug_lname : "نام لاتین",
                     Drug.drug_explain : "توضیحات",
                     Drug.drug_how_to_use : "نحوه استفاده",
                     Drug.unit : "واحد",
                     Drug.price : "قیمت (تومان)",
                     Drug.disease_type : "دسته‌بندی‌ها"

    }


    form_ajax_refs = {
        'disease_type': {
            'fields': ('diseases_name',),  # فیلدی که در جستجو نمایش داده می‌شود
            'order_by': 'diseases_type_id'  # مرتب‌سازی بر اساس آیدی
        }
    }

    column_formatters = {
        Drug.price: lambda model, name: f"{int(getattr(model, name)):,}" if getattr(model,
                                                                                    name) is not None else "وارد نشده"
    }

    column_formatters_detail = {
        Drug.price: lambda model, name: f"{int(getattr(model, name)):,}" if getattr(model,
                                                                                    name) is not None else "وارد نشده"
    }

class PatientsAdmin(PermissionAwareModelView, model=Patient):
    column_list = [Patient.patient_id, Patient.full_name, Patient.telegram_id]
    column_labels = {Patient.patient_id: "ایدی بیمار", Patient.full_name: "نام بیمار"}
    name = "بیمار"
    name_plural = "بیماران"
    icon = "fa-solid fa-user-injured"

# ... هر ModelView جدیدی که می‌خواهید اضافه کنید را اینجا قرار دهید


# admin_panel/views.py

# ... سایر کلاس‌های ادمین شما ...

class OrderListAdmin(ModelView, model=OrderList):
    """
    این کلاس برای مدیریت اقلام سفارش به صورت Inline استفاده می‌شود.
    در منوی اصلی نمایش داده نخواهد شد.
    """
    exclude_from_menu = False


    # ستون‌هایی که در فرم inline نمایش داده می‌شوند
    column_list = [
        OrderList.order_id,
        "drug.drug_lname",  # نمایش نام دارو از طریق رابطه
        OrderList.qty,
        OrderList.price
    ]
    column_labels = {
        OrderList.order_id: "برای سفارش شماره",
        "drug.drug_lname": "نام دارو",
        OrderList.qty: "تعداد",
        OrderList.price: "قیمت واحد"
    }
    column_searchable_list = [
        OrderList.order_id
    ]
    # اجازه تمام عملیات‌ها روی اقلام سفارش
    can_create = False
    # can_create = True
    # can_edit = True
    # can_delete = True
    #
    # # برای اینکه فیلد "دارو" به صورت جستجوی ایجکس کار کند
    # form_ajax_refs = {
    #     'drug': {
    #         'fields': ('drug_pname', 'drug_lname'),  # با این فیلدها جستجو کن
    #         'order_by': 'drugs_id'
    #     }
    # }


class OrdersAdmin(PermissionAwareModelView, model=Order):
    name = "سفارش"
    name_plural = "سفارشات"
    icon = "fa-solid fa-cart-shopping"

    # ستون‌هایی که در لیست اصلی نمایش داده می‌شوند
    column_list = [
        Order.order_id,
        "patient.full_name",  # نمایش نام بیمار به جای آیدی
        "user.full_name",  # نمایش نام کاربر به جای آیدی
        Order.order_status,
        Order.created_at,
        'items_link'  # <-- ستون مجازی جدید ما

    ]
    column_formatters = {
        'items_link': lambda model, name: Markup(
            f'<a href="/admin/order-list/list?search={model.order_id}" class="btn btn-sm btn-info">مشاهده اقلام</a>'
        )
    }
    # برچسب‌های فارسی برای ستون‌ها
    column_labels = {
        Order.order_id: "شماره سفارش",
        "patient.full_name": "بیمار",
        "user.full_name": "ثبت کننده",
        Order.order_status: "وضعیت سفارش",
        Order.created_at: "تاریخ ثبت",
    }

    # ستون‌هایی که می‌توان بر اساس آنها مرتب‌سازی کرد
    column_sortable_list = [Order.order_id, Order.created_at]

    # قابلیت جستجو بر اساس نام بیمار و کاربر
    column_searchable_list = [
        "patient.full_name",
        "user.full_name",
    ]

    # # فرمت‌دهی تاریخ برای نمایش بهتر
    # column_formatters = {
    #     # Order.created_at: lambda m, a: getattr(m, a.key).strftime("%Y-%m-%d %H:%M")
    #     Order.created_at: lambda model, name: getattr(model, name).strftime("%Y-%m-%d %H:%M") if getattr(model,
    #                                                                                                      name) else ""
    # }

    # +++ بخش کلیدی: اضافه کردن اقلام سفارش به صورت inline +++

    inlines = [OrderListAdmin]

    # ستون‌هایی که در فرم ایجاد/ویرایش سفارش نمایش داده می‌شوند
    form_columns = [
        Order.patient,
        Order.user,
        Order.order_status,
    ]

    # برای اینکه فیلدهای "بیمار" و "کاربر" به صورت جستجوی ایجکس کار کنند
    form_ajax_refs = {
        'patient': {
            'fields': ('full_name', 'telegram_id'),
            'order_by': 'patient_id',
        },
        'user': {
            'fields': ('full_name', 'mobile_number'),
            'order_by': 'user_id',
        }
    }
