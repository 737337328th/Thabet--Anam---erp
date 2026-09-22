import frappe
from frappe import _


REQUIRED_ACCOUNT_NUMBERS = [
    "1101", "1102", "1103", "1201",
    "2101", "3101",
    "4101", "4102", "4103", "4104",
    "5001",
    "5101", "5102", "5103", "5104", "5105", "5106", "5107",
    "5201", "5202", "5203", "5204", "5205", "5206", "5207",
    "5301", "5302", "5303", "5304", "5399",
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
    if name:
        return name

    name = frappe.db.get_value(
        "Cost Center",
        {"company": company, "is_group": 1},
        "name",
    )
    if not name:
        frappe.throw(_("No group Cost Center found for {0}").format(company))
    return name


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
            existing_row = next(
                (row for row in doc.accounts if row.company == company),
                None,
            )
            if existing_row:
                if existing_row.default_account != account:
                    existing_row.default_account = account
                    changed = True
            else:
                doc.append(
                    "accounts",
                    {"company": company, "default_account": account},
                )
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
        doc.append(
            "accounts",
            {"company": company, "default_account": account},
        )

    doc.insert(ignore_permissions=True)
    return {"name": label, "account": account, "created": True}


def status(company="Thabit Anam", currency="YER"):
    info = _company(company)
    missing = [
        number
        for number in REQUIRED_ACCOUNT_NUMBERS
        if not frappe.db.exists(
            "Account",
            {"company": company, "account_number": number},
        )
    ]

    gl_count = frappe.db.count(
        "GL Entry",
        {"company": company, "is_cancelled": 0},
    )

    return {
        "plan": "Thabet Anam Onyx-style Accounting",
        "company": info.name,
        "abbr": info.abbr,
        "country": info.country,
        "default_currency": info.default_currency,
        "expected_currency": currency,
        "currency_matches": info.default_currency == currency,
        "posted_gl_entries": gl_count,
        "missing_required_accounts": missing,
        "safe_to_apply_foundation": info.default_currency == currency and not missing,
    }


def apply(company="Thabit Anam", currency="YER"):
    """
    Idempotent accounting foundation for the Onyx-style ERPNext plan.

    It does NOT:
    - replace an existing chart of accounts,
    - change company currency,
    - submit/cancel financial vouchers,
    - create opening balances.
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
        if not frappe.db.exists(
            "Account",
            {"company": company, "account_number": number},
        )
    ]
    if missing:
        frappe.throw(
            _("Required account numbers are missing: {0}")
            .format(", ".join(missing))
        )

    cost_centers = [
        _ensure_cost_center(company, label)
        for label in COST_CENTERS
    ]

    payment_modes = [
        _ensure_mode_of_payment(company, label, mop_type, account_number)
        for label, mop_type, account_number in PAYMENT_MODES
    ]

    frappe.db.commit()

    return {
        "status": "ok",
        "company": company,
        "cost_centers": cost_centers,
        "payment_modes": payment_modes,
        "financial_vouchers_posted": 0,
        "opening_balances_created": 0,
    }
