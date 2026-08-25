import frappe

no_cache = 1


def get_context(context):
	token = frappe.form_dict.get("token")
	context.token = token
	context.no_header = True
	name = frappe.db.get_value("IC Test Request", {"share_token": token}, "name") if token else None
	if not name:
		context.error = "Invalid sample tracking link"
		return context
	doc = frappe.get_doc("IC Test Request", name)
	context.doc = doc
	context.customer_name = frappe.db.get_value("IC Customer Profile", doc.customer, "company_name")
	context.qr = frappe.call("instacertify.utils.qr.make_qr", payload=doc.sample_qr_code or doc.name)
	return context
