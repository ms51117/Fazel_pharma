# app/admin_panel/resources.py

from fastapi_admin.resources import Model, Field
from fastapi_admin.widgets import displays, inputs

# --- ایمپورت کردن مدل‌های SQLModel از پروژه شما ---
# مسیر ایمپورت‌ها بر اساس ساختار پروژه شما تنظیم شده است.
from app.models.user import User
from app.models.user_role import UserRole
from app.models.disease_type import DiseaseType
from app.models.patient import Patient


class UserResource(Model):
    # این کلاس به fastapi-admin می‌گوید که چگونه مدل User را نمایش و مدیریت کند.

    # مدل SQLModel که این منبع به آن متصل است
    model = User

    # عنوان این بخش در منوی پنل ادمین
    title = "Users"

    # آیکون از کتابخانه fontawesome (اختیاری)
    icon = "fas fa-users"

    # فیلدهایی که در لیست کاربران نمایش داده می‌شوند
    fields = [
        "id",
        Field(name="user_name", label="Username"),
        "telegram_id",
        "role_id",
        Field(name="role", label="Role Name"),  # نمایش نام نقش
        "created_at",
    ]

    # فیلدهایی که در فرم ایجاد/ویرایش کاربر نمایش داده می‌شوند
    fields_create = [
        Field(name="user_name", label="Username", input_=inputs.Text(required=True)),
        Field(name="password", label="Password", input_=inputs.Password(required=True)),
        Field(name="telegram_id", label="Telegram ID", input_=inputs.Number(required=True)),
        # استفاده از Select برای انتخاب نقش از بین نقش‌های موجود
        Field(
            name="role",
            label="Role",
            input_=inputs.Select(
                # این بخش به صورت داینامیک تمام نقش‌ها را از دیتابیس می‌خواند
                # و به صورت یک لیست کشویی نمایش می‌دهد.
                model=UserRole,
                # فیلدی که به عنوان مقدار (value) در <option> استفاده می‌شود (id)
                key="id",
                # فیلدی که به عنوان متن (label) در <option> نمایش داده می‌شود (role_name)
                label="role_name"
            )
        ),
    ]

    # فیلدهای ویرایش (می‌توانیم پسورد را اختیاری کنیم)
    fields_edit = [
        Field(name="user_name", label="Username", input_=inputs.Text(required=True)),
        Field(name="telegram_id", label="Telegram ID", input_=inputs.Number(required=True)),
        Field(
            name="role",
            label="Role",
            input_=inputs.Select(model=UserRole, key="id", label="role_name")
        ),
        # برای تغییر پسورد (اختیاری)
        Field(name="password", label="New Password (optional)", input_=inputs.Password()),
    ]


class UserRoleResource(Model):
    model = UserRole
    title = "Roles"
    icon = "fas fa-user-tag"
    fields = [
        "id",
        "role_name",
        "role_description",
    ]
    # در فرم ایجاد/ویرایش، هر دو فیلد قابل ویرایش هستند
    fields_create = [
        Field(name="role_name", label="Role Name", input_=inputs.Text(required=True)),
        Field(name="role_description", label="Description", input_=inputs.TextArea()),
    ]
    # فرم ویرایش هم مشابه فرم ایجاد است
    fields_edit = fields_create


class DiseaseTypeResource(Model):
    model = DiseaseType
    title = "Disease Types"
    icon = "fas fa-virus"
    fields = [
        "id",
        "disease_name",
        "disease_description",
    ]
    fields_create = [
        Field(name="disease_name", label="Disease Name", input_=inputs.Text(required=True)),
        Field(name="disease_description", label="Description", input_=inputs.TextArea()),
    ]
    fields_edit = fields_create


class PatientResource(Model):
    # این منبع فقط برای نمایش اطلاعات بیمار است (read-only)
    model = Patient
    title = "Patient Profiles"
    icon = "fas fa-user-injured"

    # فیلدهایی که در لیست نمایش داده می‌شوند
    fields = [
        "id",
        "name",
        "family",
        "national_code",
        Field(name="user", label="Linked User"),  # نمایش کاربر مرتبط
        "created_at",
    ]

    # با خالی گذاشتن این لیست‌ها، امکان ایجاد یا ویرایش مستقیم بیمار از ادمین را غیرفعال می‌کنیم.
    # مدیریت پروفایل بیمار بهتر است از طریق ربات انجام شود.
    fields_create = []
    fields_edit = []
