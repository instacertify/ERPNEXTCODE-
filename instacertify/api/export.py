# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import frappe
from frappe.utils.csvutils import to_csv


@frappe.whitelist()
def download_doctype_csv(doctype: str, filters: str | None = None):
	"""IC Admin bulk CSV download for any InstaCertify DocType."""
	roles = frappe.get_roles()
	if not (set(roles) & {"IC Admin", "System Manager", "Administrator"}):
		frappe.throw("Only IC Admin can download full data exports", frappe.PermissionError)

	allowed = {
		"IC Lead",
		"IC Quotation",
		"IC Customer Profile",
		"IC Project",
		"IC Lab",
		"IC Test Request",
		"IC Asset Register",
		"IC Planner Entry",
	}
	if doctype not in allowed:
		frappe.throw("DocType not allowed for export")

	import json

	flt = json.loads(filters) if filters else None
	meta = frappe.get_meta(doctype)
	fields = ["name"] + [df.fieldname for df in meta.fields if df.fieldtype not in ("Table", "Section Break", "Column Break", "HTML", "Button", "Tab Break")]
	rows = frappe.get_all(doctype, filters=flt, fields=fields, limit=10000)
	data = [fields] + [[r.get(f) for f in fields] for r in rows]
	frappe.response["filename"] = f"{doctype.replace(' ', '_').lower()}.csv"
	frappe.response["filecontent"] = to_csv(data)
	frappe.response["type"] = "csv"
