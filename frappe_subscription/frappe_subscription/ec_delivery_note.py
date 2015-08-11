import frappe

def on_delivery_note_cancel(doc, method):
    # check the freeze state of the delivery note
    # cancel and delete all the packing slip

    if doc.dn_status == "Shipping Labels Created":
        frappe.throw("Can not cancel Delivery Note Shipping Labels are already created !!!")
    else:
        # delete the packing slips
        ps_to_cancel = []
        ch_to_remove = []
        bin_items = {}

        for ps_details in doc.packing_slip_details:
            ps_to_cancel.append(ps_details.packing_slip)
            bin_qty = (bin_items.get(ps_details.item_code) or 0) + 1
            bin_items.update({
                ps_details.item_code:bin_qty
            })
            ch_to_remove.append(ps_details)

        [doc.remove(ch) for ch in ch_to_remove]
        [frappe.delete_doc("Packing Slip", ps_name) for ps_name in ps_to_cancel]

        doc.dn_status = "Draft"
        # update stock ledger