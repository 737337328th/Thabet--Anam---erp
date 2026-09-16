# تشغيل ثابت أنعم من الجوال

## أسرع مسار
1. ارفع المشروع إلى خادم Linux يدعم Docker.
2. انسخ `.env.example` إلى `.env` وعدّل كلمات المرور والأسرار.
3. شغّل `docker compose up -d --build`.
4. افتح عنوان الخادم على المنفذ 8080.
5. غيّر كلمة مرور `admin` الافتراضية فورًا.

## النسخ الاحتياطي
- `scripts/backup_postgres.sh` ينشئ نسخة PostgreSQL بصيغة dump مع SHA-256.
- `scripts/restore_postgres.sh FILE` يستعيد النسخة.

## Android
الواجهة الحالية Web responsive، ويمكن لاحقًا تغليفها كتطبيق Android (WebView/Capacitor) دون إعادة بناء منطق النظام.
