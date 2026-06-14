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



from frappe.utils import nowdate, get_time, get_datetime, time_diff_in_seconds

def autoOvertimeCaculation():
    today = nowdate()

    try:
        employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=[
            "name",
            "employee_name",
            "default_shift"
        ])

        for emp in employees:

            try:
                if not emp.default_shift:
                    continue

                # Get shift end time
                shift = frappe.get_value("Shift Type", emp.default_shift, "end_time")
                if not shift:
                    continue

                today = nowdate()
                shift_end = get_datetime(f"{today} {shift}")

                # Get last OUT checkin for today
                last_checkin = frappe.db.sql("""
                    SELECT time
                    FROM `tabEmployee Checkin`
                    WHERE employee = %s
                      AND DATE(time) = %s
                      AND log_type = 'OUT'
                    ORDER BY time DESC
                    LIMIT 1
                """, (emp.name, today), as_dict=True)

                if not last_checkin:
                    continue

                checkout_time = get_datetime(last_checkin[0].time)

                # No overtime
                if checkout_time <= shift_end:
                    continue

                # Prevent duplicate
                exists = frappe.db.exists("Overtime Request", {
                    "employee": emp.name,
                    "date": today,
                    "docstatus": ["<", 2]
                })

                if exists:
                    continue

                overtime_seconds = time_diff_in_seconds(checkout_time, shift_end)
                total_mins = int(overtime_seconds / 60)

                from_time = shift_end.strftime("%H:%M:%S")
                to_time = checkout_time.strftime("%H:%M:%S")

                doc = frappe.get_doc({
                    "doctype": "Overtime Request",
                    "employee": emp.name,
                    "employee_name": emp.employee_name,
                    "date": today,
                    "from": from_time,
                    "to": to_time,
                    "reason": "Auto-generated overtime based on checkout",
                    "total_mins": total_mins,
                    "has_transportation_allowance": "No",
                    "workflow_state": "Pending"
                })

                doc.insert(ignore_permissions=True)

            except Exception as emp_error:
                frappe.log_error(
                    message=frappe.get_traceback(),
                    title=f"Overtime Auto Creation Failed for Employee {emp.name}"
                )

    except Exception as e:
        frappe.log_error(
            message=frappe.get_traceback(),
            title="Overtime Auto Creation Job Failed"
        )