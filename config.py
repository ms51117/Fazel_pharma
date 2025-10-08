from datetime import datetime

from fastapi import FastAPI
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

import logging
from app.core.logging_config import setup_logging

# ------------- mange life span ------------------


@asynccontextmanager
async def event_life_span(app: FastAPI):
    # Setup logging on startup
    setup_logging()  # <-- فراخوانی تابع تنظیمات لاگ

    # Get our custom logger
    logger = logging.getLogger("app")
    logger.info("Application startup......................................")
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







