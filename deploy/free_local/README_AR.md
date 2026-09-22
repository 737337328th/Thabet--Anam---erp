# تشغيل V4 مجانًا محليًا

هذا المسار يحافظ على التكلفة التشغيلية عند **0$** عند تشغيل النظام على جهاز مملوك لك.

## المسار المعتمد
- Windows 11 + WSL2 Ubuntu أو جهاز Linux.
- Frappe/ERPNext v16 مفتوح المصدر.
- مستودع GitHub الحالي.
- الوصول من الهاتف عبر الشبكة المحلية، أو عبر نفق خاص مجاني تختاره لاحقًا.
- لا يحتاج هذا المسار إلى Frappe Cloud أو Oracle Cloud.

## شرط مهم
هذا المستودع هو تطبيق Frappe مخصص، وليس ERPNext كاملًا. يجب أن يكون لديك Bench يعمل عليه Frappe وERPNext v16 أولًا.

## تثبيت التطبيق على Bench موجود
من داخل مجلد bench:

```bash
bench get-app https://github.com/737337328th/Thabet--Anam---erp --branch main
bench --site <SITE_NAME> install-app thabet_anam_v4
bench --site <SITE_NAME> migrate
bench --site <SITE_NAME> list-apps
```

## الفحص قبل التشغيل
```bash
bench --site <SITE_NAME> execute thabet_anam_v4.production_check.run
```

إذا كان الموقع يحتوي أكثر من شركة:
```bash
bench --site <SITE_NAME> execute thabet_anam_v4.production_check.run --kwargs "{\"company\": \"اسم الشركة\"}"
```

## التجهيز التشغيلي الآمن
بعد استيراد دليل الحسابات ومراجعته فقط:

```bash
bench --site <SITE_NAME> execute thabet_anam_v4.production_setup.status --kwargs "{\"company\": \"اسم الشركة\", \"currency\": \"YER\"}"
```

لا تنفذ `production_setup.apply` قبل التأكد من دليل الحسابات. وحتى عند تشغيلها فهي تنشئ مراكز تكلفة وأصناف خدمات فقط ولا ترحّل سندات أو قيودًا مالية.

## سياسة الأمان
- لا يوجد إنشاء تلقائي لـ Journal Entry.
- لا يوجد Submit تلقائي لفواتير أو سندات.
- لا يوجد تعديل مباشر على GL Entry.
- أي عملية مالية حساسة تبقى داخل ERPNext وبأمر صريح من المستخدم.
