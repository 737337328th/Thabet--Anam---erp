import frappe


def _resolve_company(company=None):
    if company:
        return company if frappe.db.exists("Company", company) else None

    companies = frappe.get_all("Company", pluck="name", limit=2)
    if len(companies) == 1:
        return companies[0]
    return None


def run(company=None):
    checks = {}
    resolved_company = _resolve_company(company)

    checks["company"] = resolved_company
    checks["company_exists"] = bool(resolved_company)
    checks["app_installed"] = "thabet_anam_v4" in frappe.get_installed_apps()
    checks["customs_doctype_exists"] = bool(
        frappe.db.exists("DocType", "Customs Clearance File")
    )
    checks["sales_invoice_custom_field"] = bool(
        frappe.db.exists(
            "Custom Field",
            {"dt": "Sales Invoice", "fieldname": "ta_customs_file"},
        )
    )
    checks["payment_entry_custom_field"] = bool(
        frappe.db.exists(
            "Custom Field",
            {"dt": "Payment Entry", "fieldname": "ta_customs_file"},
        )
    )

    if resolved_company:
        checks["company_currency"] = frappe.db.get_value(
            "Company", resolved_company, "default_currency"
        )
        checks["gl_entries"] = frappe.db.count(
            "GL Entry", {"company": resolved_company, "is_cancelled": 0}
        )
    else:
        checks["company_currency"] = None
        checks["gl_entries"] = None
        checks["company_resolution_error"] = (
            "Pass company explicitly when the site contains zero or multiple companies."
        )

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
