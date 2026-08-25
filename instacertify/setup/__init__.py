# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


ROLES = [
	"IC Admin",
	"IC Ops Manager",
	"IC Sales Person",
	"IC Operations Manager",
]


def after_install():
	ensure_roles()
	ensure_currencies()
	ensure_company_defaults()
	from instacertify.setup.workspace import ensure_workspace_and_prints
	from instacertify.setup.seed import seed_demo_data

	ensure_workspace_and_prints()
	seed_demo_data()
	frappe.clear_cache()


def after_migrate():
	ensure_roles()
	ensure_currencies()
	from instacertify.setup.workspace import ensure_workspace_and_prints

	ensure_workspace_and_prints()


def ensure_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			doc = frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1})
			doc.insert(ignore_permissions=True)


def ensure_currencies():
	for code, fraction, symbol in (
		("INR", "Paisa", "₹"),
		("USD", "Cent", "$"),
	):
		if not frappe.db.exists("Currency", code):
			frappe.get_doc(
				{
					"doctype": "Currency",
					"currency_name": code,
					"enabled": 1,
					"fraction": fraction,
					"symbol": symbol,
				}
			).insert(ignore_permissions=True)
		else:
			frappe.db.set_value("Currency", code, "enabled", 1)

	# Primary currency INR; multi-currency enabled at company level when present
	companies = frappe.get_all("Company", pluck="name")
	for company in companies:
		frappe.db.set_value("Company", company, "default_currency", "INR")


def ensure_company_defaults():
	"""Soft branding defaults for Instacertify."""
	if frappe.db.exists("Company", "InstaCertify"):
		return
	# Company is created by site installer; avoid forcing if none exists yet
	pass


def boot_session(bootinfo):
	bootinfo.instacertify = {
		"brand": "InstaCertify",
		"primary": "#065175",
		"accent": "#ec6820",
		"roles": ROLES,
	}
