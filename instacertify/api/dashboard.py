# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import formatdate, now_datetime


@frappe.whitelist()
def home_dashboard():
	user = frappe.session.user
	roles = frappe.get_roles(user)
	privileged = bool(set(roles) & {"IC Admin", "IC Ops Manager", "System Manager", "Administrator"})

	lead_filters = {} if privileged else {"assigned_to": user}
	quote_filters = {} if privileged else [["sales_person", "in", [user]], ["owner", "=", user]]
	project_filters = {} if privileged else {
		"sales_person": user
	}

	# For non-privileged sales, also projects they closed / own — simplified
	projects = frappe.get_all(
		"IC Project",
		filters=None if privileged or "IC Operations Manager" in roles else [
			["sales_person", "=", user]
		],
		fields=[
			"name",
			"project_name",
			"customer",
			"priority",
			"status",
			"progress_percent",
			"card_color",
			"expected_end",
		],
		order_by="modified desc",
		limit=8,
	)
	for p in projects:
		p["customer_name"] = frappe.db.get_value("IC Customer Profile", p.customer, "company_name")

	pending_quotes = frappe.get_all(
		"IC Quotation",
		filters={"status": ("in", ["Shared", "Changes Requested", "Draft"])},
		fields=["name", "subject", "status", "grand_total", "currency", "customer"],
		limit=6,
		order_by="modified desc",
	)

	planner = frappe.get_all(
		"IC Planner Entry",
		filters={"for_user": user, "plan_date": frappe.utils.today()},
		fields=["name", "title", "start_slot", "end_slot", "color", "description"],
		order_by="start_slot asc",
	)

	stats = {
		"leads": frappe.db.count("IC Lead"),
		"quotes": frappe.db.count("IC Quotation"),
		"projects": frappe.db.count("IC Project"),
		"open_projects": frappe.db.count(
			"IC Project", {"status": ("in", ["Pending", "In Progress", "Waiting on Client", "Waiting on Lab"])}
		),
		"labs": frappe.db.count("IC Lab"),
		"test_requests": frappe.db.count("IC Test Request"),
	}

	dt = now_datetime()
	hour = dt.hour
	if hour < 12:
		greet = _("Good morning")
	elif hour < 17:
		greet = _("Good afternoon")
	else:
		greet = _("Good evening")

	return {
		"greeting": f"{greet}, {frappe.utils.get_fullname(user)}",
		"date_label": formatdate(dt, "dddd, d MMMM YYYY"),
		"time_label": dt.strftime("%I:%M %p"),
		"stats": stats,
		"projects": projects,
		"pending_quotes": pending_quotes,
		"planner": planner,
		"roles": roles,
	}


@frappe.whitelist()
def labs_paginated(page: int = 1, page_size: int = 6):
	page = max(1, int(page or 1))
	page_size = min(20, max(1, int(page_size or 6)))
	total = frappe.db.count("IC Lab", {"active": 1})
	labs = frappe.get_all(
		"IC Lab",
		filters={"active": 1},
		fields=["name", "lab_name", "location", "accreditation", "lab_scope_pdf", "accreditation_certificate"],
		order_by="lab_name asc",
		limit_start=(page - 1) * page_size,
		limit_page_length=page_size,
	)
	return {
		"page": page,
		"page_size": page_size,
		"total": total,
		"pages": max(1, (total + page_size - 1) // page_size),
		"labs": labs,
	}


@frappe.whitelist()
def lab_detail(lab: str):
	doc = frappe.get_doc("IC Lab", lab)
	roles = frappe.get_roles()
	show_purchase = bool(set(roles) & {"IC Admin", "System Manager", "Administrator"})
	scopes = []
	for s in doc.scopes:
		scopes.append(
			{
				"test_name": s.test_name,
				"applicable_standard": s.applicable_standard,
				"accreditation_scope": s.accreditation_scope,
				"typical_timeline_days": s.typical_timeline_days,
				"selling_price": s.selling_price,
				"purchase_price": s.purchase_price if show_purchase else None,
				"currency": s.currency,
				"scope_pdf": s.scope_pdf,
			}
		)
	return {
		"name": doc.name,
		"lab_name": doc.lab_name,
		"location": doc.location,
		"accreditation": doc.accreditation,
		"lab_scope_pdf": doc.lab_scope_pdf,
		"accreditation_certificate": doc.accreditation_certificate,
		"scopes": scopes,
		"show_purchase": show_purchase,
	}
