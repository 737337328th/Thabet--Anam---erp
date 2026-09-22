import frappe


SALES_INVOICE_HTML = r"""
<div dir="rtl" style="font-family: Arial, sans-serif;">
  <div style="text-align:center; margin-bottom:12px;">
    <h2 style="margin:0;">{{ doc.company }}</h2>
    <div style="font-size:16px; font-weight:700;">فاتورة خدمات</div>
  </div>

  <table class="table table-bordered" style="font-size:12px;">
    <tr>
      <td><b>رقم الفاتورة</b><br>{{ doc.name }}</td>
      <td><b>التاريخ</b><br>{{ frappe.utils.formatdate(doc.posting_date) }}</td>
      <td><b>العميل</b><br>{{ doc.customer_name or doc.customer }}</td>
    </tr>
    <tr>
      <td><b>اسم المستورد</b><br>{{ doc.get("ta_importer_name") or "" }}</td>
      <td><b>رقم قيد البوابة</b><br>{{ doc.get("ta_gateway_entry_no") or "" }}</td>
      <td><b>رقم البيان</b><br>{{ doc.get("ta_declaration_no") or "" }}</td>
    </tr>
    <tr>
      <td><b>عدد وسائل النقل</b><br>{{ doc.get("ta_transport_count") or "" }}</td>
      <td colspan="2"><b>نوع البضاعة</b><br>{{ doc.get("ta_goods_type") or "" }}</td>
    </tr>
  </table>

  <table class="table table-bordered" style="font-size:12px;">
    <thead>
      <tr>
        <th style="width:6%;">م</th>
        <th>البيان</th>
        <th style="width:14%;">الوحدة</th>
        <th style="width:16%;">المبلغ</th>
      </tr>
    </thead>
    <tbody>
      {% for row in doc.items %}
      <tr>
        <td>{{ row.idx }}</td>
        <td>{{ row.item_name or row.description }}</td>
        <td>{{ row.uom or row.stock_uom or "" }}</td>
        <td style="text-align:left;">{{ row.get_formatted("amount", doc) }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <table class="table table-bordered" style="font-size:12px;">
    <tr>
      <td><b>الإجمالي</b></td>
      <td style="text-align:left;"><b>{{ doc.get_formatted("grand_total") }}</b></td>
    </tr>
    <tr>
      <td><b>المدفوع</b></td>
      <td style="text-align:left;">{{ doc.get_formatted("paid_amount") }}</td>
    </tr>
    <tr>
      <td><b>المتبقي</b></td>
      <td style="text-align:left;">{{ doc.get_formatted("outstanding_amount") }}</td>
    </tr>
  </table>

  {% if doc.remarks %}
  <div><b>ملاحظات:</b> {{ doc.remarks }}</div>
  {% endif %}

  <div style="margin-top:35px; display:flex; justify-content:space-between;">
    <div>توقيع المستلم: __________________</div>
    <div>توقيع المدير: __________________</div>
  </div>
</div>
"""

PAYMENT_ENTRY_HTML = r"""
<div dir="rtl" style="font-family: Arial, sans-serif;">
  <div style="text-align:center; margin-bottom:14px;">
    <h2 style="margin:0;">{{ doc.company }}</h2>
    <div style="font-size:17px; font-weight:700;">
      {% if doc.payment_type == "Receive" %}سند قبض
      {% elif doc.payment_type == "Pay" %}سند صرف
      {% else %}سند تحويل داخلي{% endif %}
    </div>
  </div>

  <table class="table table-bordered" style="font-size:12px;">
    <tr>
      <td><b>رقم السند</b><br>{{ doc.name }}</td>
      <td><b>التاريخ</b><br>{{ frappe.utils.formatdate(doc.posting_date) }}</td>
      <td><b>طريقة الدفع</b><br>{{ doc.mode_of_payment or "" }}</td>
    </tr>
    <tr>
      <td colspan="2"><b>الطرف</b><br>{{ doc.party_name or doc.party or "" }}</td>
      <td><b>المرجع</b><br>{{ doc.get("ta_reference_invoice") or doc.reference_no or "" }}</td>
    </tr>
    <tr>
      <td><b>المبلغ المدفوع</b><br>{{ doc.get_formatted("paid_amount") }}</td>
      <td><b>المبلغ المستلم</b><br>{{ doc.get_formatted("received_amount") }}</td>
      <td><b>العملة</b><br>{{ doc.paid_from_account_currency or doc.paid_to_account_currency or "" }}</td>
    </tr>
  </table>

  {% if doc.remarks %}
  <div style="margin-top:8px;"><b>البيان:</b> {{ doc.remarks }}</div>
  {% endif %}

  <div style="margin-top:40px; display:flex; justify-content:space-between;">
    <div>المستلم: __________________</div>
    <div>المحاسب: __________________</div>
    <div>المدير: __________________</div>
  </div>
</div>
"""

PRINT_FORMATS = [
    ("ثابت أنعم - فاتورة خدمات", "Sales Invoice", SALES_INVOICE_HTML),
    ("ثابت أنعم - سند قبض وصرف", "Payment Entry", PAYMENT_ENTRY_HTML),
]


def _ensure_print_format(name, doctype, html):
    values = {
        "print_format_for": "DocType",
        "doc_type": doctype,
        "module": "Thabet Anam V4",
        "standard": "No",
        "custom_format": 1,
        "print_format_type": "Jinja",
        "html": html,
        "disabled": 0,
        "align_labels_right": 1,
        "margin_top": 10,
        "margin_bottom": 10,
        "margin_left": 10,
        "margin_right": 10,
        "pdf_generator": "chrome",
        "css": """
            .print-format { font-size: 12px; }
            .print-format table { width: 100%; border-collapse: collapse; }
            .print-format th, .print-format td { vertical-align: top; }
            .print-format th { text-align: center; }
        """,
    }

    if frappe.db.exists("Print Format", name):
        doc = frappe.get_doc("Print Format", name)
        for key, value in values.items():
            setattr(doc, key, value)
        doc.save(ignore_permissions=True)
        return {"name": name, "created": False}

    doc = frappe.get_doc({"doctype": "Print Format", "name": name, **values})
    doc.insert(ignore_permissions=True)
    return {"name": name, "created": True}


def ensure_print_formats():
    return [
        _ensure_print_format(name, doctype, html)
        for name, doctype, html in PRINT_FORMATS
    ]
