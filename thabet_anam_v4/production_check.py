import frappe


def run(company="Thabit Anam"):
    checks = {}

    checks["company_exists"] = bool(frappe.db.exists("Company", company))
    checks["app_installed"] = "thabet_anam_v4" in frappe.get_installed_apps()
    checks["customs_doctype_exists"] = bool(frappe.db.exists("DocType", "Customs Clearance File"))
    checks["sales_invoice_custom_field"] = bool(
        frappe.db.exists("Custom Field", {"dt": "Sales Invoice", "fieldname": "ta_customs_file"})
    )
    checks["payment_entry_custom_field"] = bool(
        frappe.db.exists("Custom Field", {"dt": "Payment Entry", "fieldname": "ta_customs_file"})
    )

    if checks["company_exists"]:
        checks["company_currency"] = frappe.db.get_value("Company", company, "default_currency")
        checks["gl_entries"] = frappe.db.count("GL Entry", {"company": company, "is_cancelled": 0})
    else:
        checks["company_currency"] = None
        checks["gl_entries"] = None

    checks["all_core_checks_pass"] = all(
        checks[k]
        for k in (
            "company_exists",
            "app_installed",
            "customs_doctype_exists",
            "sales_invoice_custom_field",
            "payment_entry_custom_field",
        )
    )
    return checks
