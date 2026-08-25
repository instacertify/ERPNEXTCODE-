import frappe

no_cache = 1


def get_context(context):
	token = frappe.form_dict.get("token")
	context.no_header = True
	name = frappe.db.get_value("IC Test Request", {"share_token": token}, "name") if token else None
	if not name:
		context.error = "Invalid report link"
		return context
	doc = frappe.get_doc("IC Test Request", name)
	if doc.sample_status not in ("Report Available", "Report Uploaded", "Shared with Customer"):
		context.error = "Report is not available yet"
		return context
	context.doc = doc
	context.file_url = doc.report_file
	return context
