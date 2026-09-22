# نشر ثابت أنعم على Oracle

هذا المسار مخصص لتشغيل ERPNext + V4 بشكل فعلي على خادم Oracle.

## قبل التنفيذ
- أنشئ خادم Ubuntu ARM64 أو AMD64 مناسب.
- افتح TCP 22 و80 و443 فقط.
- اربط اسم نطاق بالخادم.
- لا تحفظ كلمات المرور في GitHub.

## التنفيذ
```bash
cp deploy/oracle/.secrets.example deploy/oracle/.secrets
nano deploy/oracle/.secrets

bash deploy/oracle/01_prepare_server.sh
# سجّل خروج/دخول مرة واحدة بعد إضافة المستخدم إلى مجموعة docker
bash deploy/oracle/02_deploy.sh
```

## النسخ الاحتياطي
```bash
bash deploy/oracle/03_backup.sh
```

## ملاحظات
- يستخدم البناء الرسمي لـ frappe_docker عبر `images/layered/Containerfile`.
- يستخدم MariaDB + Redis + HTTPS عبر `compose.https.yaml`.
- بعد تشغيل الموقع، لا تستورد دليل الحسابات إلا بعد أخذ Backup ومراجعة العملة والشركة.
- V4 لا ينفذ قبضًا أو صرفًا أو ترحيلًا ماليًا تلقائيًا.
