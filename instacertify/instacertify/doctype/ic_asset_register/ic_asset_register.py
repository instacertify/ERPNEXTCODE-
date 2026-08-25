# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import frappe
from frappe.model.document import Document


class ICAssetRegister(Document):
	pass


def before_insert(doc, method=None):
	if not doc.asset_code:
		year = frappe.utils.now_datetime().year
		seq = frappe.db.count("IC Asset Register") + 1
		doc.asset_code = f"IC-AST-{year}-{seq:05d}"
