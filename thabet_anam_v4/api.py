import frappe
from frappe.utils import flt


@frappe.whitelist()
def unit_metrics(item_value=0, net_weight=0, additional_units=0):
    """Pure calculation helper. Does not write financial documents."""
    item_value = flt(item_value)
    net_weight = flt(net_weight)
    additional_units = flt(additional_units)
    return {
        "value_per_net_weight": item_value / net_weight if net_weight else None,
        "value_per_additional_unit": item_value / additional_units if additional_units else None,
    }


@frappe.whitelist()
def document_readiness(clearance_file):
    """Read-only readiness summary for one customs file."""
    doc = frappe.get_doc("Customs Clearance File", clearance_file)
    total = len(doc.documents or [])
    received = sum(1 for row in (doc.documents or []) if row.received)
    return {
        "total": total,
        "received": received,
        "missing": total - received,
        "readiness_percent": (received / total * 100) if total else 0,
    }
