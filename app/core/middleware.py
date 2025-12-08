# app/core/middleware.py

import time
from fastapi import Request, Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

# ============================================================
#  🛡️ تنظیمات Rate Limit (حافظه موقت RAM)
# ============================================================

# دیکشنری برای ذخیره IP و زمان‌ها
# ساختار: { "192.168.1.1": [time1, time2, ...] }
REQUEST_HISTORY = {}

# تنظیمات: حداکثر ۶۰ درخواست در هر ۶۰ ثانیه (میانگین ۱ در ثانیه)
LIMIT_COUNT = 500
LIMIT_SECONDS = 60


async def global_rate_limit_middleware(request: Request, call_next):
    """
    این تابع به عنوان میدل‌ور در FastAPI ثبت می‌شود.
    قبل از رسیدن درخواست به روترها یا دیتابیس، IP کاربر را چک می‌کند.
    """

    # 1. دریافت IP کاربر
    # اگر پشت پروکسی (مانند Nginx/Cloudflare) هستید ممکن است نیاز به هدر X-Forwarded-For باشد
    # اما برای حالت عادی client.host کافی است.
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()

    # 2. اگر IP جدید است، لیست خالی برایش بساز
    if client_ip not in REQUEST_HISTORY:
        REQUEST_HISTORY[client_ip] = []

    # 3. دریافت لیست زمان‌های درخواست این IP
    history = REQUEST_HISTORY[client_ip]

    # 4. پاکسازی زمان‌های قدیمی (خارج از پنجره زمانی ۶۰ ثانیه)
    # فقط زمان‌هایی که فاصله آن‌ها تا الان کمتر از LIMIT_SECONDS است نگه داشته می‌شوند
    valid_history = [t for t in history if now - t < LIMIT_SECONDS]
    REQUEST_HISTORY[client_ip] = valid_history

    # 5. بررسی تعداد درخواست‌ها
    if len(valid_history) >= LIMIT_COUNT:
        # ⛔ بلاک کردن درخواست: بازگرداندن ارور ۴۲۹ بدون درگیر کردن دیتابیس
        return Response(
            content=f"Too Many Requests. Limit is {LIMIT_COUNT} per minute.",
            status_code=HTTP_429_TOO_MANY_REQUESTS
        )

    # 6. ثبت زمان درخواست فعلی در لیست
    valid_history.append(now)

    # 7. ادامه مسیر به سمت اپلیکیشن اصلی (روترها و ...)
    response = await call_next(request)
    return response
