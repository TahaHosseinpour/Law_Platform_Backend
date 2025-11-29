# Law Platform Backend

پلتفرم حقوقی با FastAPI و PostgreSQL

## ویژگی‌ها

- 🔐 احراز هویت با JWT
- 👥 سه نوع کاربر: کاربر عادی، وکیل، ادمین
- 🛡️ سیستم RBAC (کنترل دسترسی بر اساس نقش)
- 🗄️ PostgreSQL با Prisma ORM
- 📝 مستندات خودکار با Swagger

## ساختار پروژه

```
Law_Platform_Backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # ثبت‌نام و ورود
│   │   ├── users.py      # مدیریت کاربران
│   │   ├── lawyers.py    # مدیریت وکلا
│   │   └── admin.py      # پنل ادمین
│   ├── core/             # هسته اصلی
│   │   ├── security.py   # JWT و hash password
│   │   ├── permissions.py # سیستم RBAC
│   │   └── deps.py       # Dependencies
│   ├── schemas/          # Pydantic schemas
│   ├── config.py         # تنظیمات
│   ├── database.py       # اتصال به database
│   └── main.py           # نقطه ورود
├── prisma/
│   └── schema.prisma     # مدل‌های database
├── requirements.txt
└── .env
```

## نصب و راه‌اندازی

### پیش‌نیازها

- Python 3.11+
- PostgreSQL 14+

### مراحل نصب

1. کلون کردن پروژه:
```bash
git clone <repository-url>
cd Law_Platform_Backend
```

2. ایجاد محیط مجازی:
```bash
python -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate
```

3. نصب پکیج‌ها:
```bash
pip install -r requirements.txt
```

4. ایجاد فایل `.env`:
```bash
cp .env.example .env
```

سپس `.env` را ویرایش کنید و مقادیر را تنظیم کنید.

5. تولید Prisma Client:
```bash
prisma generate
```

6. اجرای migrations:
```bash
prisma db push
```

7. اجرای سرور:
```bash
uvicorn app.main:app --reload
```

سرور روی `http://localhost:8000` اجرا می‌شود.

## API Documentation

بعد از اجرای سرور، مستندات API در آدرس زیر در دسترس است:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## نقش‌ها و دسترسی‌ها

### کاربر عادی (USER)
- مشاهده و ویرایش پروفایل خود
- ایجاد پرونده
- مشاهده پرونده‌های خود
- مشاهده لیست وکلا

### وکیل (LAWYER)
- تمام دسترسی‌های کاربر عادی
- ایجاد و ویرایش پروفایل وکالت
- مشاهده تمام پرونده‌ها

### ادمین (ADMIN)
- تمام دسترسی‌ها
- مدیریت کاربران
- تایید/رد وکلا
- حذف کاربران

## Endpoints اصلی

### Authentication
- `POST /auth/register` - ثبت‌نام
- `POST /auth/login` - ورود

### Users
- `GET /users/me` - پروفایل من
- `PUT /users/me` - ویرایش پروفایل

### Lawyers
- `POST /lawyers/profile` - ایجاد پروفایل وکالت
- `GET /lawyers/profile/me` - پروفایل وکالت من
- `PUT /lawyers/profile/me` - ویرایش پروفایل وکالت
- `GET /lawyers/` - لیست وکلا
- `GET /lawyers/{id}` - جزئیات وکیل

### Admin
- `GET /admin/users` - لیست کاربران
- `GET /admin/users/{id}` - جزئیات کاربر
- `DELETE /admin/users/{id}` - حذف کاربر
- `PATCH /admin/lawyers/{id}/verify` - تایید وکیل
- `PATCH /admin/lawyers/{id}/unverify` - رد وکیل

## توسعه

### اضافه کردن Permission جدید

1. در `app/core/permissions.py` یک permission جدید اضافه کنید:
```python
class Permission(str, Enum):
    NEW_PERMISSION = "new_permission"
```

2. به `ROLE_PERMISSIONS` اضافه کنید:
```python
ROLE_PERMISSIONS = {
    UserRole.USER: [Permission.NEW_PERMISSION, ...],
    ...
}
```

3. در endpoint استفاده کنید:
```python
@router.get("/endpoint")
async def endpoint(
    current_user: Annotated[User, Depends(require_permission(Permission.NEW_PERMISSION))]
):
    ...
```

## لایسنس

MIT
