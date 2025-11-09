# app/admin_panel/setup.py

from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from sqlalchemy.ext.asyncio import create_async_engine

# --- ایمپورت کردن منابعی که در مرحله قبل ساختیم ---
from .resources import (
    UserResource,
    UserRoleResource,
    DiseaseTypeResource,
    PatientResource
)


# تابعی برای راه‌اندازی و اتصال پنل ادمین به برنامه اصلی FastAPI
def setup_admin(app: FastAPI, engine):
    """
    این تابع پنل ادمین را با تنظیمات لازم مقداردهی اولیه کرده
    و به نمونه اصلی FastAPI متصل می‌کند.
    """
    # 1. مقداردهی اولیه برنامه ادمین
    #    - engine: موتور دیتابیسی که برای ارتباط با دیتابیس استفاده می‌شود.
    #    - title: عنوانی که در بالای پنل ادمین نمایش داده می‌شود.
    #    - logo_url: آدرس یک لوگو (اختیاری).
    admin_app.init(
        engine=engine,
        title="Fazel Pharma Admin Panel",
        logo_url="https://preview.tabler.io/static/logo-white.svg",  # می‌توانید آدرس لوگوی خود را قرار دهید
    )

    # 2. ثبت کردن منابع (Resources)
    #    هر منبعی که در اینجا ثبت شود، در منوی پنل ادمین قابل مشاهده و مدیریت خواهد بود.
    admin_app.register_resource(UserResource)
    admin_app.register_resource(UserRoleResource)
    admin_app.register_resource(DiseaseTypeResource)
    admin_app.register_resource(PatientResource)

    # 3. اتصال برنامه ادمین به برنامه اصلی FastAPI
    #    این دستور، پنل ادمین را تحت آدرس /admin در دسترس قرار می‌دهد.
    #    مثال: http://127.0.0.1:8000/admin
    app.mount("/admin", admin_app)

    print("Admin panel has been set up and mounted at /admin")
