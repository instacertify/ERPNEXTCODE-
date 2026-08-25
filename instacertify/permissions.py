# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import frappe


def _roles():
	return set(frappe.get_roles(frappe.session.user))


def _is_privileged():
	roles = _roles()
	return bool(roles & {"IC Admin", "IC Ops Manager", "System Manager", "Administrator"})


def quotation_query(user):
	if not user:
		user = frappe.session.user
	if _is_privileged() or "IC Operations Manager" in frappe.get_roles(user):
		return ""
	return f"""(`tabIC Quotation`.sales_person = {frappe.db.escape(user)}
		or `tabIC Quotation`.owner = {frappe.db.escape(user)}
		or `tabIC Quotation`.shared_by = {frappe.db.escape(user)})"""


def quotation_has_permission(doc, user=None, permission_type=None):
	if _is_privileged():
		return True
	user = user or frappe.session.user
	if "IC Sales Person" in frappe.get_roles(user):
		return doc.sales_person == user or doc.owner == user or doc.shared_by == user
	return True


def lead_query(user):
	if not user:
		user = frappe.session.user
	if _is_privileged() or "IC Operations Manager" in frappe.get_roles(user):
		return ""
	return f"""(`tabIC Lead`.assigned_to = {frappe.db.escape(user)}
		or `tabIC Lead`.owner = {frappe.db.escape(user)})"""


def project_query(user):
	if not user:
		user = frappe.session.user
	if _is_privileged() or "IC Operations Manager" in frappe.get_roles(user):
		return ""
	return f"""(`tabIC Project`.sales_person = {frappe.db.escape(user)}
		or `tabIC Project`.operations_owner = {frappe.db.escape(user)}
		or `tabIC Project`.owner = {frappe.db.escape(user)})"""


def customer_query(user):
	if not user:
		user = frappe.session.user
	if _is_privileged() or "IC Operations Manager" in frappe.get_roles(user):
		return ""
	return f"""(`tabIC Customer Profile`.assigned_sales = {frappe.db.escape(user)}
		or `tabIC Customer Profile`.owner = {frappe.db.escape(user)})"""


def lab_has_permission(doc, user=None, permission_type=None):
	"""Purchase price is masked in client JS for non-admins; server still allows write of scopes."""
	return True
