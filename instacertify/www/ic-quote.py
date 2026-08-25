import frappe

no_cache = 1


def get_context(context):
	token = frappe.form_dict.get("token")
	context.token = token
	context.brand = "InstaCertify"
	context.no_header = True
	context.no_sidebar = True
	if not token:
		context.error = "Missing quote token"
		return context
	try:
		context.quote = frappe.call(
			"instacertify.instacertify.doctype.ic_quotation.ic_quotation.get_public_quote",
			token=token,
		)
	except Exception:
		context.error = "This quote link is invalid or no longer available."
	return context
