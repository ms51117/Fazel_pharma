from fastapi import FastAPI
from app.routes import user
from app.routes import patient
from app.routes import user_role_permission
from app.routes import user_role
from app.routes import payment_list
from app.routes import order
from app.routes import order_list




app = FastAPI()

app.include_router(user.router, prefix="/user", tags=["Users"])
app.include_router(patient.router, prefix="/patient", tags=["Patients"])
app.include_router(user_role_permission.router,prefix="/permission", tags=["permissions"])
app.include_router(user_role.router, prefix="/role", tags=["Roles"])
app.include_router(payment_list.router, prefix="/payment", tags=["Payments"])
app.include_router(order.router, prefix="/order", tags=["orders"])
app.include_router(order_list.router, prefix="/order-list", tags=["orders-list"])




