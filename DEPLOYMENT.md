# راهنمای دیپلوی Law Platform API

این راهنما مراحل دیپلوی پروژه روی Coolify را شرح می‌دهد.

## پیش‌نیازها

- یک سرور با Docker نصب شده
- Coolify نصب شده روی سرور
- دسترسی به GitHub یا Git repository

## روش 1: استفاده از Dockerfile (پیشنهادی برای Coolify)

### مرحله 1: آماده‌سازی Repository

1. کد را به Git repository خود push کنید
2. فایل‌های زیر در repository موجود هستند:
   - `Dockerfile`
   - `.dockerignore`
   - `.env.production` (نمونه - نباید commit شود)

### مرحله 2: پیکربندی Coolify

1. وارد Coolify شوید
2. یک پروژه جدید بسازید
3. یک Application جدید اضافه کنید:
   - Source: GitHub/GitLab repository
   - Branch: main (یا branch مورد نظر)
   - Build Pack: Dockerfile

### مرحله 3: اضافه کردن PostgreSQL Database

1. در همان پروژه، یک Database جدید اضافه کنید
2. نوع: PostgreSQL 15
3. نام database: `law_platform`
4. بعد از ساخت، connection string را کپی کنید

### مرحله 4: تنظیم Environment Variables

در تنظیمات Application، متغیرهای زیر را اضافه کنید:

```env
DATABASE_URL=postgresql://[کپی شده از Coolify]
JWT_SECRET_KEY=[یک کلید بسیار قوی و تصادفی]
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=["*"]
APP_NAME=Law Platform API
APP_VERSION=1.0.0
DEBUG=False
```

**نکات امنیتی:**
- `JWT_SECRET_KEY` باید یک رشته تصادفی و قوی باشد (حداقل 32 کاراکتر)
- `ALLOWED_ORIGINS=["*"]` به همه domainها اجازه دسترسی می‌دهد
- برای امنیت بیشتر، domainهای خاص را مشخص کنید: `["https://yourdomain.com","https://app.yourdomain.com"]`

### مرحله 5: تنظیم Port

- Internal Port: `8000`
- Coolify به طور خودکار port external را تنظیم می‌کند

### مرحله 6: Health Check

Coolify به طور خودکار health check را از Dockerfile می‌خواند، اما می‌توانید دستی تنظیم کنید:
- Health Check Path: `/health`
- Health Check Interval: 30s

### مرحله 7: Deploy

1. روی دکمه "Deploy" کلیک کنید
2. Coolify شروع به build و deploy می‌کند
3. بعد از اتمام، URL application را مشاهده خواهید کرد

## روش 2: استفاده از Docker Compose (اختیاری)

اگر می‌خواهید همه چیز (app + database) را با Docker Compose deploy کنید:

### مرحله 1: ویرایش docker-compose.yml

فایل `docker-compose.yml` را ویرایش کنید:

```yaml
# در قسمت environment سرویس postgres
POSTGRES_PASSWORD: [یک پسورد قوی]

# در قسمت environment سرویس web
DATABASE_URL: postgresql://lawplatform:[همان پسورد]@postgres:5432/law_platform
JWT_SECRET_KEY: [یک کلید بسیار قوی]
```

### مرحله 2: Deploy با Docker Compose

```bash
docker-compose up -d
```

## مایگریشن دیتابیس

بعد از deploy، باید مایگریشن‌های Prisma را اجرا کنید:

### روش 1: از طریق Coolify Console

1. وارد Console سرویس شوید
2. دستور زیر را اجرا کنید:

```bash
prisma migrate deploy
```

### روش 2: SSH به سرور

```bash
docker exec -it law_platform_api prisma migrate deploy
```

## تست API

بعد از deploy موفق، می‌توانید API را تست کنید:

- Health Check: `https://your-domain.com/health`
- API Docs: `https://your-domain.com/docs`
- Root: `https://your-domain.com/`

## CORS Configuration

### دسترسی آزاد از همه سرورها

در `.env.production` یا Environment Variables:

```env
ALLOWED_ORIGINS=["*"]
```

**هشدار:** این روش برای همه domainها اجازه دسترسی می‌دهد و ممکن است خطر امنیتی داشته باشد.

### دسترسی محدود (امن‌تر)

```env
ALLOWED_ORIGINS=["https://yourdomain.com","https://app.yourdomain.com","https://admin.yourdomain.com"]
```

## نکات مهم

1. **Secret Key:** حتماً `JWT_SECRET_KEY` را تغییر دهید
2. **Database Password:** از پسورد قوی برای database استفاده کنید
3. **Environment Files:** فایل `.env` را در `.gitignore` قرار دهید
4. **Logs:** در Coolify می‌توانید logs را مشاهده کنید
5. **Backup:** از database خود backup منظم بگیرید

## عیب‌یابی

### خطای Connection به Database

- بررسی کنید `DATABASE_URL` صحیح باشد
- در Coolify، connection string database را چک کنید
- مطمئن شوید که database سرویس running است

### خطای CORS

- `ALLOWED_ORIGINS` را بررسی کنید
- مطمئن شوید که domain frontend در لیست باشد
- برای تست، می‌توانید موقتاً از `["*"]` استفاده کنید

### خطای 500

- Logs را در Coolify چک کنید
- بررسی کنید همه environment variables تنظیم شده باشند
- مطمئن شوید Prisma migrations اجرا شده باشد

## بروزرسانی

برای deploy نسخه جدید:

1. تغییرات را به repository push کنید
2. در Coolify روی "Redeploy" کلیک کنید
3. Coolify به طور خودکار نسخه جدید را build و deploy می‌کند

## Local Development

برای توسعه local، از فایل `.env.local` استفاده کنید:

```bash
# کپی کردن .env.local به .env
cp .env.local .env

# نصب dependencies
pip install -r requirements.txt

# Generate Prisma client
prisma generate

# Run migrations
prisma migrate dev

# اجرای سرور
uvicorn app.main:app --reload
```

## پشتیبانی

در صورت بروز مشکل:

1. Logs را بررسی کنید
2. Health check endpoint را تست کنید
3. Database connection را چک کنید
4. Environment variables را مجدداً بررسی کنید
