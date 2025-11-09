# admin_panel/views.py

from sqladmin import ModelView, BaseView, expose
from starlette.requests import Request
from sqlalchemy import func, select
from datetime import date

# --- ایمپورت‌های لازم ---
from database import async_session_maker
from app.models.user import User
from app.models.patient import Patient
from app.models.drug import Drug
from app.models.order import Order
from app.models.order_list import OrderList


# --- صفحه سفارشی داشبورد ---
class DashboardView(BaseView):
    name = "داشبورد"
    icon = "fa-solid fa-gauge"

    @expose("/dashboard", methods=["GET"])
    async def dashboard_page(self, request: Request):
        async with async_session_maker() as session:
            stmt_orders_count = select(func.count(Order.order_id)).where(
                func.date(Order.created_at) == date.today()
            )
            result_orders_count = await session.execute(stmt_orders_count)
            today_orders_count = result_orders_count.scalar_one_or_none() or 0

            stmt_sales = (
                select(func.sum(OrderList.price * OrderList.qty))
                .join(Order, OrderList.order_id == Order.order_id)
                .where(func.date(Order.created_at) == date.today())
            )
            result_sales = await session.execute(stmt_sales)
            today_sales = result_sales.scalar_one_or_none() or 0.0

            stats = {
                "today_orders_count": today_orders_count,
                "today_sales": int(today_sales),
            }

        return await self.templates.TemplateResponse(
            request, "admin/dashboard.html", {"stats": stats}
        )


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
