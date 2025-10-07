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



app = FastAPI()

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







