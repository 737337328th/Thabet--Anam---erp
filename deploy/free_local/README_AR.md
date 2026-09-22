# تشغيل ثابت أنعم V4 مجانًا محليًا

هذا هو **المسار المجاني المعتمد** لتشغيل ERPNext v16 + تطبيق ثابت أنعم V4 على جهاز مملوك لك، بدون Frappe Cloud أو خادم مدفوع.

## المتطلبات
- Windows مع Ubuntu/WSL2، أو Ubuntu/Debian.
- Git.
- Docker Engine 23+.
- Docker Compose v2.
- Python 3 على الجهاز لتوليد كلمات مرور محلية قوية.

Frappe v16 نفسها تتطلب Python 3.14 وNode 24 داخل بيئة Frappe، لكن مسار Docker يبني هذه البيئة داخل الحاوية ولا يطلب منك ضبطها يدويًا على Windows.

## الطريقة الأسهل — بناء وتشغيل كامل

من جذر هذا المستودع:

```bash
bash deploy/free_local/docker_zero_cost.sh
```

السكربت يقوم تلقائيًا بـ:
1. تنزيل/تحديث Frappe Docker الرسمي.
2. بناء صورة تحتوي ERPNext v16 وتطبيق `thabet_anam_v4`.
3. إنشاء MariaDB وRedis والحاويات المطلوبة.
4. إنشاء موقع `thabet.localhost` إن لم يكن موجودًا.
5. تثبيت ERPNext وV4.
6. تشغيل `migrate`.
7. تنفيذ فحص إنتاج **للقراءة فقط**.
8. حفظ كلمات المرور محليًا داخل `deploy/free_local/.runtime/.secrets`، وهو مسار مستبعد من Git.

بعد النجاح افتح على اللابتوب:

```text
http://localhost:8080
```

يمكن تغيير المنفذ واسم الموقع دون تعديل السكربت:

```bash
SITE_NAME=thabet.localhost HTTP_PORT=8080 bash deploy/free_local/docker_zero_cost.sh
```

## الوصول من الهاتف
على Linux متصل بنفس الشبكة، استخدم عنوان IP الخاص باللابتوب مع المنفذ 8080. على Windows/WSL قد تحتاج فتح المنفذ في جدار حماية Windows أو إعداد تمرير المنفذ حسب وضع Docker/WSL لديك.

## نسخة احتياطية مجانية

بعد تشغيل النظام:

```bash
bash deploy/free_local/backup_local.sh
```

ينشئ السكربت نسخة تشمل قاعدة البيانات والملفات داخل:

```text
deploy/free_local/backups/
```

ويولد ملف SHA-256 للتحقق من سلامة النسخة.

## إذا كان لديك Bench جاهز بالفعل

```bash
bash deploy/free_local/install_app.sh <SITE_NAME>
```

أو يدويًا:

```bash
bench get-app https://github.com/737337328th/Thabet--Anam---erp --branch main
bench --site <SITE_NAME> install-app thabet_anam_v4
bench --site <SITE_NAME> migrate
bench --site <SITE_NAME> execute thabet_anam_v4.production_check.run
```

## تهيئة الحسابات
فحص التهيئة فقط:

```bash
bench --site <SITE_NAME> execute thabet_anam_v4.onyx_setup.status
```

إذا كان الموقع يحتوي أكثر من شركة، مرر اسم الشركة صراحةً. لا يتم تشغيل `onyx_setup.apply` أو `production_setup.apply` تلقائيًا.

## سياسة الأمان المالي
- لا إنشاء تلقائي لـ Journal Entry.
- لا Submit أو Cancel تلقائي لأي مستند مالي.
- لا تعديل مباشر على GL Entry.
- لا أرصدة افتتاحية تلقائية.
- لا تشغيل `onyx_setup.apply` أو `production_setup.apply` من سكربت التثبيت.
- أي ترحيل مالي أو إلغاؤه يبقى بأمر صريح من المستخدم داخل ERPNext.
