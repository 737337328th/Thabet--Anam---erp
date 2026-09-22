frappe.ui.form.on("Payment Entry", {
    refresh(frm) {
        if (frm.doc.ta_customs_file) {
            frm.add_custom_button(__("فتح ملف التخليص"), () => {
                frappe.set_route("Form", "Customs Clearance File", frm.doc.ta_customs_file);
            });
        }
    }
});
