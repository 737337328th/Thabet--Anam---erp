import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
    "Customer": [
        {
            "fieldname": "ta_importer_name",
            "label": "اسم المستورد",
            "fieldtype": "Data",
            "insert_after": "customer_name",
        },
        {
            "fieldname": "ta_customs_notes",
            "label": "ملاحظات التخليص",
            "fieldtype": "Small Text",
            "insert_after": "ta_importer_name",
        },
    ],
    "Sales Invoice": [
        {
            "fieldname": "ta_customs_section",
            "label": "بيانات التخليص الجمركي",
            "fieldtype": "Section Break",
            "insert_after": "customer_name",
        },
        {
            "fieldname": "ta_customs_file",
            "label": "ملف التخليص",
            "fieldtype": "Link",
            "options": "Customs Clearance File",
            "insert_after": "ta_customs_section",
        },
        {
            "fieldname": "ta_importer_name",
            "label": "اسم المستورد",
            "fieldtype": "Data",
            "fetch_from": "ta_customs_file.importer_name",
            "insert_after": "ta_customs_file",
        },
        {
            "fieldname": "ta_gateway_entry_no",
            "label": "رقم قيد البوابة",
            "fieldtype": "Data",
            "fetch_from": "ta_customs_file.gateway_entry_no",
            "insert_after": "ta_importer_name",
        },
        {
            "fieldname": "ta_declaration_no",
            "label": "رقم البيان",
            "fieldtype": "Data",
            "fetch_from": "ta_customs_file.declaration_no",
            "insert_after": "ta_gateway_entry_no",
        },
        {
            "fieldname": "ta_transport_count",
            "label": "عدد وسائل النقل",
            "fieldtype": "Int",
            "fetch_from": "ta_customs_file.transport_count",
            "insert_after": "ta_declaration_no",
        },
        {
            "fieldname": "ta_goods_type",
            "label": "نوع البضاعة",
            "fieldtype": "Data",
            "fetch_from": "ta_customs_file.goods_type",
            "insert_after": "ta_transport_count",
        },
    ],
    "Payment Entry": [
        {
            "fieldname": "ta_customs_file",
            "label": "ملف التخليص",
            "fieldtype": "Link",
            "options": "Customs Clearance File",
            "insert_after": "party",
        },
        {
            "fieldname": "ta_reference_invoice",
            "label": "رقم الفاتورة المرجعية",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "insert_after": "ta_customs_file",
        },
    ],
}

CUSTOM_ROLES = ["مدير ثابت أنعم", "محاسب ثابت أنعم", "مدخل بيانات التخليص"]


def ensure_roles():
    for role_name in CUSTOM_ROLES:
        if not frappe.db.exists("Role", role_name):
            frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(
                ignore_permissions=True
            )


def apply_custom_fields():
    create_custom_fields(CUSTOM_FIELDS, update=True)


def after_install():
    ensure_roles()
    apply_custom_fields()
    frappe.db.commit()


def after_migrate():
    ensure_roles()
    apply_custom_fields()
