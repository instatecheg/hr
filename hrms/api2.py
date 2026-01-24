import frappe
from frappe import _

@frappe.whitelist()
def submit_timesheet(name):
    """
    Force-submit Timesheet without validation.
    """
    if not name:
        frappe.throw(_("Timesheet name is required"))

    frappe.db.set_value("Timesheet", name, "docstatus", 1)
    frappe.db.commit()

    return {"message": f"Timesheet {name} force-submitted successfully!"}
