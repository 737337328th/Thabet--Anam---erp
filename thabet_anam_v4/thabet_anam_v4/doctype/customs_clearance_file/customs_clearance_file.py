import frappe
from frappe.model.document import Document


class CustomsClearanceFile(Document):
    def validate(self):
        self.customer_balance = get_customer_balance(self.customer, self.company)


def get_customer_balance(customer, company):
    if not customer or not company:
        return 0

    result = frappe.db.sql(
        """
        select coalesce(sum(debit_in_account_currency - credit_in_account_currency), 0)
        from `tabGL Entry`
        where party_type = 'Customer'
          and party = %s
          and company = %s
          and is_cancelled = 0
        """,
        (customer, company),
    )
    return result[0][0] if result else 0
