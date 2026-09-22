# مسار التهيئة داخل واجهة ERPNext — thabet-anam.k.frappe.cloud

## 1) Backup
ابدأ بنسخة احتياطية من الموقع قبل أي تغيير.

## 2) Company
افتح Company واقرأ:
- اسم الشركة حرفيًا.
- العملة الأساسية.
- الدولة.
- عدد الشركات.

لا تغيّر العملة في هذه المرحلة.

## 3) فحص المحاسبة الحالية
افتح General Ledger / GL Entry وتأكد هل توجد حركات سابقة.
إذا وجدت حركات، لا تستخدم Chart of Accounts Importer لاستبدال الدليل.

## 4) دليل الحسابات
المسار في ERPNext:
Home > Getting Started > Chart of Accounts Importer

- اختر الشركة.
- نزّل Download Template.
- طابق القالب مع `onyx_source/chart_of_accounts_ar.csv`.
- لا ترفع الملف قبل مطابقة أسماء الأعمدة والقيم المطلوبة.
- لا أرصدة افتتاحية في هذه المرحلة.

## 5) مراكز التكلفة
استخدم `01_cost_centers_source.csv` بعد استبدال `__SITE_COMPANY__` باسم الشركة الحقيقي:
- التخليص الجمركي
- التصاريح
- الطباعة
- الإدارة والمكتب

## 6) طرق الدفع
استخدم `02_modes_of_payment_source.csv`:
- نقدي → 1101
- بنك → 1102
- محفظة إلكترونية → 1103
- حوالة → 1102 مبدئيًا

لا يتم الربط إلا بعد التأكد أن أرقام الحسابات موجودة فعليًا.

## 7) الخدمات
أنشئ مجموعة أصناف:
`خدمات ثابت أنعم`

ثم استخدم `03_service_items_source.csv`.

## 8) الحقول المخصصة
المسار:
Home > Customization > Form Customization > Customize Form

أنشئ الحقول الموجودة في `04_custom_fields_source.csv`.
كل الحقول قياسية داخل Customer / Sales Invoice / Payment Entry ولا تعتمد على V4.

## 9) صيغ الطباعة
المسار:
Home > Settings > Print Format

أنشئ:
- ثابت أنعم - فاتورة خدمات → Sales Invoice
- ثابت أنعم - سند قبض وصرف → Payment Entry

Standard = No
Custom Format = نعم
Print Format Type = Jinja

ثم الصق القوالب:
- `09_sales_invoice_print_format.html`
- `10_payment_entry_print_format.html`

## 10) Workspace
أنشئ Workspace باسم:
`حسابات ثابت أنعم`

وفق `07_workspace_spec.json`.

## 11) أول اختبار
ينشأ عميل اختبار وفاتورة **مسودة فقط**.
لا Submit، لا Payment Entry مرحّل، لا Journal Entry، ولا أرصدة افتتاحية حتى أمر المستخدم.
