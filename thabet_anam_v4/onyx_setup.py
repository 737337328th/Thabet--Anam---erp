import frappe
from frappe import _

from thabet_anam_v4.onyx_print_formats import ensure_print_formats


REQUIRED_ACCOUNT_NUMBERS = [
    "1101", "1102", "1103", "1201",
    "2101", "3101",
    "4101", "4102", "4103", "4104",
    "5001",
    "5101", "5102", "5103", "5104", "5105", "5106", "5107",
    "5201", "5202", "5203", "5204", "5205", "5206", "5207",
    "5301", "5302", "5303", "5304", "5399",
]

CUSTOM_ROLES = [
    "مدير ثابت أنعم",
    "محاسب ثابت أنعم",
    "مدخل بيانات ثابت أنعم",
]

COST_CENTERS = [
    "التخليص الجمركي",
    "التصاريح",
    "الطباعة",
    "الإدارة والمكتب",
]

PAYMENT_MODES = [
    ("نقدي", "Cash", "1101"),
    ("بنك", "Bank", "1102"),
    ("محفظة إلكترونية", "Phone", "1103"),
    ("حوالة", "General", "1102"),
]

SERVICE_ITEMS = [
    ("TA-SVC-CLEARANCE", "أجور تخليص جمركي", "4101", "5001", "التخليص الجمركي"),
    ("TA-SVC-PERMIT", "أجور التصاريح", "4102", "5107", "التصاريح"),
    ("TA-SVC-PRINT", "أجور الطباعة", "4103", "5206", "الطباعة"),
    ("TA-SVC-FOLLOWUP", "أجور متابعة المعاملات", "4104", "5105", "التخليص الجمركي"),
]


def _company(company):
    row = frappe.db.get_value(
        "Company",
        company,
        ["name", "abbr", "default_currency", "country"],
        as_dict=True,
    )
    if not row:
        frappe.throw(_("Company {0} does not exist").format(company))
    return row


def _account_by_number(company, account_number):
    return frappe.db.get_value(
        "Account",
        {"company": company, "account_number": account_number, "is_group": 0},
        "name",
    )


def _root_cost_center(company):
    name = frappe.db.get_value(
        "Cost Center",
        {"company": company, "parent_cost_center": ["is", "not set"], "is_group": 1},
        "name",
    )
    if not name:
        name = frappe.db.get_value(
            "Cost Center",
            {"company": company, "is_group": 1},
            "name",
        )
    if not name:
        frappe.throw(_("No group Cost Center found for {0}").format(company))
    return name


def _ensure_role(role_name):
    if frappe.db.exists("Role", role_name):
        return False
    frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)
    return True


def _ensure_cost_center(company, label):
    existing = frappe.db.get_value(
        "Cost Center",
        {"company": company, "cost_center_name": label},
        "name",
    )
    if existing:
        return existing

    doc = frappe.get_doc(
        {
            "doctype": "Cost Center",
            "cost_center_name": label,
            "company": company,
            "parent_cost_center": _root_cost_center(company),
            "is_group": 0,
        }
    )
    doc.insert(ignore_permissions=True)
    return doc.name


def _ensure_mode_of_payment(company, label, mop_type, account_number):
    account = _account_by_number(company, account_number)

    if frappe.db.exists("Mode of Payment", label):
        doc = frappe.get_doc("Mode of Payment", label)
        changed = False
        if not doc.enabled:
            doc.enabled = 1
            changed = True
        if doc.type != mop_type:
            doc.type = mop_type
            changed = True
        if account:
            row = next((x for x in doc.accounts if x.company == company), None)
            if row and row.default_account != account:
                row.default_account = account
                changed = True
            elif not row:
                doc.append("accounts", {"company": company, "default_account": account})
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
        return {"name": label, "account": account, "created": False}

    doc = frappe.get_doc(
        {
            "doctype": "Mode of Payment",
            "mode_of_payment": label,
            "type": mop_type,
            "enabled": 1,
        }
    )
    if account:
        doc.append("accounts", {"company": company, "default_account": account})
    doc.insert(ignore_permissions=True)
    return {"name": label, "account": account, "created": True}


def _service_item_group():
    group = "خدمات ثابت أنعم"
    if frappe.db.exists("Item Group", group):
        return group

    root = frappe.db.get_value(
        "Item Group",
        {"parent_item_group": ["is", "not set"], "is_group": 1},
        "name",
    ) or frappe.db.get_value("Item Group", {"is_group": 1}, "name")

    if not root:
        frappe.throw(_("No root Item Group found"))

    frappe.get_doc(
        {
            "doctype": "Item Group",
            "item_group_name": group,
            "parent_item_group": root,
            "is_group": 0,
        }
    ).insert(ignore_permissions=True)
    return group


def _default_uom():
    for candidate in ("Nos", "Unit", "Nos."):
        if frappe.db.exists("UOM", candidate):
            return candidate
    name = frappe.db.get_value("UOM", {"enabled": 1}, "name")
    if not name:
        frappe.throw(_("No enabled UOM found"))
    return name


def _ensure_service_item(company, code, label, income_no, expense_no, cc_label):
    income = _account_by_number(company, income_no)
    expense = _account_by_number(company, expense_no)
    cost_center = _ensure_cost_center(company, cc_label)

    if frappe.db.exists("Item", code):
        doc = frappe.get_doc("Item", code)
        created = False
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": code,
                "item_name": label,
                "item_group": _service_item_group(),
                "stock_uom": _default_uom(),
                "is_stock_item": 0,
                "include_item_in_manufacturing": 0,
            }
        )
        created = True

    row = next((x for x in doc.item_defaults if x.company == company), None)
    if not row:
        row = doc.append("item_defaults", {"company": company})

    row.income_account = income
    row.expense_account = expense
    row.selling_cost_center = cost_center
    row.buying_cost_center = cost_center

    if created:
        doc.insert(ignore_permissions=True)
    else:
        doc.save(ignore_permissions=True)

    return {
        "item_code": code,
        "income_account": income,
        "expense_account": expense,
        "cost_center": cost_center,
        "created": created,
    }


def status(company="Thabit Anam", currency="YER"):
    info = _company(company)
    missing = [
        number
        for number in REQUIRED_ACCOUNT_NUMBERS
        if not frappe.db.exists("Account", {"company": company, "account_number": number})
    ]

    return {
        "plan": "Thabet Anam Onyx-style Accounting",
        "company": info.name,
        "abbr": info.abbr,
        "country": info.country,
        "default_currency": info.default_currency,
        "expected_currency": currency,
        "currency_matches": info.default_currency == currency,
        "posted_gl_entries": frappe.db.count(
            "GL Entry",
            {"company": company, "is_cancelled": 0},
        ),
        "missing_required_accounts": missing,
        "safe_to_apply_foundation": info.default_currency == currency and not missing,
    }


def apply(company="Thabit Anam", currency="YER"):
    """
    Safe and idempotent foundation for the Onyx-style accounting plan.

    It never submits/cancels vouchers, never changes opening balances, never changes
    company currency, and never replaces an existing Chart of Accounts.
    """
    info = _company(company)

    if info.default_currency != currency:
        frappe.throw(
            _("Company currency is {0}; expected {1}. Review before continuing.")
            .format(info.default_currency, currency)
        )

    missing = [
        number
        for number in REQUIRED_ACCOUNT_NUMBERS
        if not frappe.db.exists("Account", {"company": company, "account_number": number})
    ]
    if missing:
        frappe.throw(
            _("Required account numbers are missing: {0}")
            .format(", ".join(missing))
        )

    roles_created = [r for r in CUSTOM_ROLES if _ensure_role(r)]

    cost_centers = [_ensure_cost_center(company, label) for label in COST_CENTERS]

    payment_modes = [
        _ensure_mode_of_payment(company, label, mop_type, account_number)
        for label, mop_type, account_number in PAYMENT_MODES
    ]

    service_items = [
        _ensure_service_item(company, code, label, income_no, expense_no, cc_label)
        for code, label, income_no, expense_no, cc_label in SERVICE_ITEMS
    ]

    print_formats = ensure_print_formats()

    frappe.db.commit()

    return {
        "status": "ok",
        "company": company,
        "roles_created": roles_created,
        "cost_centers": cost_centers,
        "payment_modes": payment_modes,
        "service_items": service_items,
        "print_formats": print_formats,
        "financial_vouchers_posted": 0,
        "opening_balances_created": 0,
    }
