import frappe
from lxml import etree
from lxml.builder import E

from ups.rating_package import RatingService
from frappe_subscription.frappe_subscription.ups_helper import UPSHelper as Helper

@frappe.whitelist()
def get_shipping_rates(delivery_note):
    # get packages Information from delivery note
    # create the xml request to fetch the ups rates

    dn = frappe.get_doc("Delivery Note",delivery_note)

    params = Helper.get_ups_api_params()
    rating_api = get_rating_service(params)
    request = get_ups_rating_request(dn, params)
    response = rating_api.request(request)

    frappe.errprint(etree.tostring(response, pretty_print=True))
    s

    shipping_rates = parse_xml_response_to_json(response)

    dn.ups_rates = shipping_rates
    dn.save(ignore_permissions= True)

def get_rating_service(params):
    return RatingService(
        params.get("ups_license"),
        params.get("ups_user_name"),
        params.get("ups_password"),
        True                        # sandbox for testing purpose set as True for production set it to False
    )

def get_ups_rating_request(delivery_note, params):
    # prepate the ups rating request

    dn = delivery_note

    packing_slips = [row.packing_slip for row in dn.packing_slip_details]
    if not packing_slips:
        frappe.throw("Can not find the linked Packing Slip ...")

    ship_from_address_name = params.get("default_warehouse")
    shipper_number = params.get("shipper_number")
    package_type = params.get("package_type")
    ship_to_params = {
        "customer":dn.customer,
        "contact_display":dn.contact_display,
        "contact_mobile":dn.contact_mobile
    }

    shipment = E.Shipment(
                    Helper.get_shipper(params),
                    Helper.get_ship_to_address(ship_to_params, dn.shipping_address_name,),
                    Helper.get_ship_from_address(params, ship_from_address_name),
                    RatingService.service_type(Code='01'),
                )
    # packages = Helper.get_packages(packing_slips, package_type)
    packages = Helper.get_packages(packing_slips, "02")
    shipment.extend(packages)

    rating_request = RatingService.rating_request_type(
        shipment,
    )

    return rating_request