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


from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    custom_fields = {
        "Delivery Trip": [
            {
                "fieldname": "lh_ops_tab",
                "label": "Logistics Hub",
                "fieldtype": "Tab Break",
                "insert_after": "amended_from"
            },
            {
                "fieldname": "lh_trip_refs_section",
                "label": "Trip References",
                "fieldtype": "Section Break"
            },
            {
                "fieldname": "lh_loading_order_no",
                "label": "Loading Order No",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_load_id",
                "label": "Load ID",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_factory_dn_no",
                "label": "Factory DN",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_trip_refs_col_2",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "lh_customer_no",
                "label": "Customer No",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_product_no",
                "label": "Product No",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_quantity",
                "label": "Quantity",
                "fieldtype": "Float",
                "precision": "3"
            },
            {
                "fieldname": "lh_trip_refs_col_3",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "lh_customer",
                "label": "Customer",
                "fieldtype": "Link",
                "options": "Customer"
            },
            {
                "fieldname": "lh_broker_customer",
                "label": "Broker Customer",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_product_name",
                "label": "Product Name",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_factory_name",
                "label": "Factory Name",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_factory_scale",
                "label": "Factory Scale",
                "fieldtype": "Data"
            },

            {
                "fieldname": "lh_route_section",
                "label": "Route Details",
                "fieldtype": "Section Break"
            },
            {
                "fieldname": "lh_source_location",
                "label": "Source Location",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_source_city",
                "label": "Source City",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_source_district",
                "label": "Source District",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_route_col_2",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "lh_destination_location",
                "label": "Destination Location",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_destination_city",
                "label": "Destination City",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_destination_district",
                "label": "Destination District",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_route_col_3",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "lh_truck_type",
                "label": "Truck Type",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_service_type",
                "label": "Service Type",
                "fieldtype": "Data"
            },
            {
                "fieldname": "lh_distance_km",
                "label": "Distance (KM)",
                "fieldtype": "Float"
            },

            {
                "fieldname": "lh_weights_section",
                "label": "Weights",
                "fieldtype": "Section Break"
            },
            {
                "fieldname": "lh_first_weight",
                "label": "First Weight",
                "fieldtype": "Float",
                "precision": "3"
            },
            {
                "fieldname": "lh_second_weight",
                "label": "Second Weight",
                "fieldtype": "Float",
                "precision": "3"
            },
            {
                "fieldname": "lh_net_weight",
                "label": "Net Weight",
                "fieldtype": "Float",
                "precision": "3"
            },
            {
                "fieldname": "lh_weights_col_2",
                "fieldtype": "Column Break"
            },
            {
                "fieldname": "lh_customer_first_weight",
                "label": "Customer Scale W1",
                "fieldtype": "Float"
            },
            {
                "fieldname": "lh_customer_second_weight",
                "label": "Customer Scale W2",
                "fieldtype": "Float"
            },
            {
                "fieldname": "lh_customer_net_weight",
                "label": "Customer Net Quantity",
                "fieldtype": "Float"
            },

            {
                "fieldname": "lh_billing_section",
                "label": "Billing",
                "fieldtype": "Section Break"
            },
            {
                "fieldname": "lh_route_fee",
                "label": "Route Fee",
                "fieldtype": "Currency"
            },
            {
                "fieldname": "lh_customer_fee_per_ton",
                "label": "Customer Fee Per Ton",
                "fieldtype": "Currency"
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)