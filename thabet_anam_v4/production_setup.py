import frappe
from frappe import _


SERVICE_ITEMS = [
    ("TA-SVC-CLEARANCE", "خدمة تخليص جمركي"),
    ("TA-SVC-PERMIT", "خدمة تصريح"),
    ("TA-SVC-PRINT", "خدمة طباعة"),
    ("TA-SVC-FOLLOWUP", "متابعة معاملة"),
]

COST_CENTERS = [
    "التخليص الجمركي",
    "التصاريح",
    "الطباعة",
    "الإدارة والمكتب",
]

REQUIRED_ACCOUNT_NUMBERS = [
    "1101", "1102", "1201", "1301", "1302", "1303", "1304",
    "2101", "3101", "4101", "4102", "4103", "4104",
    "5101", "5102", "5103", "5104", "5105",
    "5201", "5202", "5203", "5204", "5205", "5206", "5207",
    "5301", "5302", "5303", "5304", "5399",
]


def _company_info(company):
    row = frappe.db.get_value(
        "Company",
        company,
        ["name", "abbr", "default_currency", "country"],
        as_dict=True,
    )
    if not row:
        frappe.throw(_("Company {0} does not exist").format(company))
    return row


def _root_cost_center(company):
    row = frappe.db.get_value(
        "Cost Center",
        {"company": company, "parent_cost_center": ["is", "not set"], "is_group": 1},
        "name",
    )
    if row:
        return row

    row = frappe.db.get_value(
        "Cost Center",
        {"company": company, "is_group": 1},
        "name",
    )
    if row:
        return row

    frappe.throw(_("No group Cost Center exists for company {0}").format(company))


def _ensure_cost_center(company, name):
    existing = frappe.db.get_value(
        "Cost Center",
        {"company": company, "cost_center_name": name},
        "name",
    )
    if existing:
        return existing

    doc = frappe.get_doc(
        {
            "doctype": "Cost Center",
            "cost_center_name": name,
            "company": company,
            "parent_cost_center": _root_cost_center(company),
            "is_group": 0,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def _service_item_group():
    group_name = "خدمات ثابت أنعم"
    if frappe.db.exists("Item Group", group_name):
        return group_name

    root = frappe.db.get_value(
        "Item Group",
        {"parent_item_group": ["is", "not set"], "is_group": 1},
        "name",
    )
    if not root:
        root = frappe.db.get_value("Item Group", {"is_group": 1}, "name")

    if not root:
        frappe.throw(_("No root Item Group found"))

    frappe.get_doc(
        {
            "doctype": "Item Group",
            "item_group_name": group_name,
            "parent_item_group": root,
            "is_group": 0,
        }
    ).insert(ignore_permissions=True)
    return group_name


def _default_uom():
    for candidate in ("Nos", "Unit", "Nos."):
        if frappe.db.exists("UOM", candidate):
            return candidate
    row = frappe.db.get_value("UOM", {"enabled": 1}, "name")
    if not row:
        frappe.throw(_("No enabled UOM found"))
    return row


def _ensure_service_items():
    group = _service_item_group()
    uom = _default_uom()

    created = []
    for code, name in SERVICE_ITEMS:
        if frappe.db.exists("Item", code):
            continue
        frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": code,
                "item_name": name,
                "item_group": group,
                "stock_uom": uom,
                "is_stock_item": 0,
                "include_item_in_manufacturing": 0,
            }
        ).insert(ignore_permissions=True)
        created.append(code)
    return created


def _verify_accounts(company):
    missing = []
    for number in REQUIRED_ACCOUNT_NUMBERS:
        if not frappe.db.exists("Account", {"company": company, "account_number": number}):
            missing.append(number)
    return missing


def status(company="Thabit Anam", currency="YER"):
    info = _company_info(company)
    missing_accounts = _verify_accounts(company)
    gl_count = frappe.db.count("GL Entry", {"company": company, "is_cancelled": 0})

    return {
        "company": info.name,
        "abbr": info.abbr,
        "country": info.country,
        "default_currency": info.default_currency,
        "expected_currency": currency,
        "currency_matches": info.default_currency == currency,
        "posted_gl_entries": gl_count,
        "missing_required_accounts": missing_accounts,
        "ready_for_operational_setup": info.default_currency == currency and not missing_accounts,
    }


def apply(company="Thabit Anam", currency="YER"):
    """
    Safe, idempotent operational setup.
    Does not overwrite the Chart of Accounts and does not post financial vouchers.
    Run only after the Chart of Accounts has been imported and verified.
    """
    info = _company_info(company)

    if info.default_currency != currency:
        frappe.throw(
            _("Company currency is {0}; expected {1}. Fix this before go-live.")
            .format(info.default_currency, currency)
        )

    missing_accounts = _verify_accounts(company)
    if missing_accounts:
        frappe.throw(
            _("Required account numbers are missing: {0}. Import and verify the Chart of Accounts first.")
            .format(", ".join(missing_accounts))
        )

    cost_centers = [_ensure_cost_center(company, name) for name in COST_CENTERS]
    items = _ensure_service_items()

    frappe.db.commit()

    return {
        "status": "ok",
        "company": company,
        "cost_centers": cost_centers,
        "new_service_items": items,
        "financial_vouchers_posted": 0,
    }
