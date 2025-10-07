from fastapi import FastAPI
from app.routes import user
from app.routes import patient


app = FastAPI()

app.include_router(user.router, prefix="/user", tags=["Users"])
app.include_router(patient.router, prefix="/patient", tags=["Patients"])
