# admin_panel/setup.py

from fastapi import FastAPI
from sqladmin import Admin
# ما دیگر نیازی به ایمپورت Environment از Jinja2 در اینجا نداریم
# from jinja2 import Environment, FileSystemLoader
import os

from fastapi.staticfiles import StaticFiles
from admin_panel.dependencies import admin_instance
from admin_panel import views
from .admin_auth import AdminAuth
from .views import DashboardView, UsersAdmin, DrugsAdmin, DiseaseTypeAdmin, OrdersAdmin, OrderListAdmin


def format_price_filter(value: float) -> str:
    """یک فیلتر سفارشی Jinja2 برای فرمت کردن قیمت."""
    if value is None:
        return "0"
    # جداکننده هزارگان را اضافه می‌کند (e.g., 1000000 -> 1,000,000)
    return f"{int(value):,}"


def init_admin(app: FastAPI, engine):
    """
    پنل ادمین را راه‌اندازی و به اپلیکیشن FastAPI متصل می‌کند.
    """
    SECRET_KEY = os.getenv("SECRET_KEY")
    authentication_backend = AdminAuth(secret_key=SECRET_KEY)

    # --- مرحله ۱: ساخت آبجکت ادمین با پارامتر قدیمی ---
    # در نسخه‌های قدیمی، به جای jinja_env از templates_dir استفاده می‌کنیم
    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        templates_dir="admin_panel/templates"  # <-- تغییر: استفاده از پارامتر قدیمی

    )
    views.admin_instance = admin  # 🔥 مهم‌ترین خط (رجیسترکردن instance)

    # --- مرحله ۲: تزریق فیلتر سفارشی پس از ساخت آبجکت ---
    # حالا که آبجکت admin ساخته شده، به محیط Jinja2 داخلی آن دسترسی پیدا کرده
    # و فیلتر خود را به آن اضافه می‌کنیم.
    admin.templates.env.filters["format_price"] = format_price_filter


    # اتصال فایل‌های استاتیک ادمین (این بخش بدون تغییر باقی می‌ماند)
    app.mount(
        "/admin_panel/static",
        StaticFiles(directory="admin_panel/static"),
        name="admin_static"
    )

    # افزودن تمام View ها به پنل ادمین
    admin.add_view(DashboardView)
    admin.add_view(UsersAdmin)
    admin.add_view(DrugsAdmin)
    admin.add_view(DiseaseTypeAdmin)
    admin.add_view(OrdersAdmin)
    admin.add_view(OrderListAdmin)



