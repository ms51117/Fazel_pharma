from app.routes import user
from app.routes import patient
from app.routes import user_role_permission
from app.routes import user_role
from app.routes import payment_list
from app.routes import order
from app.routes import order_list
from app.routes import disease_type
from app.routes import drug
from app.routes import drug_map
from app.routes import message
from app.routes import login
from contextlib import asynccontextmanager


# -------------تست
from dotenv import load_dotenv
import os

from fastapi.staticfiles import StaticFiles
from admin_panel.setup import init_admin

from starlette.middleware.sessions import SessionMiddleware # برای فعال کردن session
from fastapi import FastAPI
from database import engine  # engine را از فایل دیتابیس خود ایمپورت کنید



import logging
from app.core.logging_config import setup_logging



load_dotenv()  # این تابع متغیرها را از فایل .env بارگذاری می‌کند

SECRET_KEY = os.getenv("SECRET_KEY")

# ------------- mange life span ------------------


@asynccontextmanager
async def event_life_span(app: FastAPI):
    # Setup logging on startup
    setup_logging()  # <-- فراخوانی تابع تنظیمات لاگ

    # Get our custom logger
    logger = logging.getLogger("app")
    logger.info("Application startup......................................")
    # setup_admin(app, engine)

    yield
    logger.info("Application shutdown.....................................")

app = FastAPI(
    lifespan=event_life_span,
    title="Fazel Pharma API",
    # ------ جدید: این بخش را به تنظیمات FastAPI اضافه کنید ------
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False,
        "clientId": "your-client-id", # این یک مقدار نمایشی است، مهم نیست چه باشد
        "scopes": "openid profile email"
    },
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)



#  ---------------- assign rout to app -------------------
app.include_router(user.router, prefix="/user", tags=["Users"])
app.include_router(patient.router, prefix="/patient", tags=["Patients"])
app.include_router(user_role_permission.router,prefix="/permission", tags=["permissions"])
app.include_router(user_role.router, prefix="/role", tags=["Roles"])
app.include_router(payment_list.router, prefix="/payment", tags=["Payments"])
app.include_router(order.router, prefix="/order", tags=["orders"])
app.include_router(order_list.router, prefix="/order-list", tags=["orders-list"])
app.include_router(disease_type.router, prefix="/disease", tags=["Diseases"])
app.include_router(drug.router, prefix="/drug", tags=["Drugs"])
app.include_router(drug_map.router, prefix="/drug-map", tags=["Drugs-Map"])
app.include_router(message.router, prefix="/message", tags=["Messages"])
app.include_router(login.router, prefix="/login", tags=["login"])



# ---------------------------------



# app.mount("/admin_panel/static", StaticFiles(directory="static"), name="static")

init_admin(app, engine)

