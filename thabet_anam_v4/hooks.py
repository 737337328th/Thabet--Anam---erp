app_name = "thabet_anam_v4"
app_title = "ثابت أنعم V4"
app_publisher = "Thabet Anam Customs Clearance"
app_description = "Customs clearance layer for ERPNext"
app_email = "Thabet.anam@gmail.com"
app_license = "MIT"
required_apps = ["erpnext"]

after_install = "thabet_anam_v4.install.after_install"
after_migrate = "thabet_anam_v4.install.after_migrate"

doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js",
    "Payment Entry": "public/js/payment_entry.js",
}
