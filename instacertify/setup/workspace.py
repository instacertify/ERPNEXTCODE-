# Copyright (c) 2026, InstaCertify and contributors
# License: MIT
"""Create desk workspaces, print formats, letter head after install."""

from __future__ import annotations

import frappe


def ensure_workspace_and_prints():
	_letter_head()
	_print_formats()
	_number_cards()
	_home_workspace()
	_module_workspaces()


def _letter_head():
	if frappe.db.exists("Letter Head", "InstaCertify Letter Head"):
		return
	frappe.get_doc(
		{
			"doctype": "Letter Head",
			"letter_head_name": "InstaCertify Letter Head",
			"source": "HTML",
			"is_default": 1,
			"content": """
			<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #065175;padding-bottom:8px;">
				<div>
					<div style="font-size:22px;font-weight:700;color:#065175;">InstaCertify</div>
					<div style="font-size:10px;color:#ec6820;letter-spacing:1px;text-transform:uppercase;">Certification &amp; Testing Solutions</div>
				</div>
				<div style="text-align:right;font-size:11px;color:#5b6b78;">
					<div>instacertify.in</div>
					<div>consulting · testing · certification</div>
				</div>
			</div>
			""",
			"footer": """
			<div style="border-top:2px solid #ec6820;padding-top:6px;font-size:10px;color:#5b6b78;">
				InstaCertify — Confidential commercial quotation
			</div>
			""",
		}
	).insert(ignore_permissions=True)


def _print_formats():
	html = frappe.get_app_path("instacertify", "templates", "print_formats", "ic_formal_quotation.html")
	with open(html) as f:
		content = f.read()

	_upsert_print(
		"IC Formal Quotation",
		"IC Quotation",
		content,
		default=1,
	)
	_upsert_print(
		"IC Sample Label",
		"IC Test Request",
		"""
		<div style="width:90mm;padding:8mm;border:2px solid #065175;border-radius:8px;font-family:sans-serif;position:relative;">
			<div style="color:#065175;font-weight:700;font-size:14px;">InstaCertify Sample</div>
			<div style="font-size:12px;margin-top:6px;"><strong>{{ doc.name }}</strong></div>
			<div style="font-size:11px;">{{ doc.title }}</div>
			<div style="font-size:11px;">Samples: {{ doc.no_of_samples }} · {{ doc.applicable_standard }}</div>
			<div style="font-size:11px;">Status: {{ doc.sample_status }}</div>
			<div style="margin-top:8px;font-size:10px;">{{ doc.sample_qr_code }}</div>
			<div style="position:absolute;right:6mm;bottom:6mm;">
				<img src="{{ qr_data_uri(doc.sample_qr_code or doc.name) }}" style="width:22mm;height:22mm;">
			</div>
		</div>
		""",
	)
	_upsert_print(
		"IC Test Request",
		"IC Test Request",
		"""
		<div style="font-family:sans-serif;padding:12mm;">
			<h2 style="color:#065175;border-bottom:2px solid #ec6820;padding-bottom:6px;">Test Request Form</h2>
			<p><strong>{{ doc.name }}</strong> — {{ doc.title }}</p>
			<p>Customer: {{ doc.customer }} · Lab: {{ doc.lab }} · Standard: {{ doc.applicable_standard }}</p>
			<p>Samples: {{ doc.no_of_samples }} · Charges: {{ doc.testing_charges }} {{ doc.currency }}</p>
			<p>Status: {{ doc.sample_status }}</p>
			<div style="position:fixed;right:12mm;bottom:12mm;">
				<img src="{{ qr_data_uri(doc.name) }}" style="width:24mm;height:24mm;">
			</div>
		</div>
		""",
	)
	# Joining letter QR overlay — used with HR Employee; printable stub
	if not frappe.db.exists("Print Format", "IC Joining Letter"):
		frappe.get_doc(
			{
				"doctype": "Print Format",
				"name": "IC Joining Letter",
				"doc_type": "Employee",
				"module": "InstaCertify",
				"standard": "No",
				"custom_format": 1,
				"print_format_type": "Jinja",
				"html": """
				<div style="font-family:sans-serif;padding:16mm;position:relative;min-height:240mm;">
					<div style="border-bottom:3px solid #065175;padding-bottom:8px;">
						<div style="font-size:22px;font-weight:700;color:#065175;">InstaCertify</div>
						<div style="color:#ec6820;font-size:11px;letter-spacing:1px;text-transform:uppercase;">Joining Letter</div>
					</div>
					<p style="margin-top:24px;">Dear <strong>{{ doc.employee_name }}</strong>,</p>
					<p>We are pleased to welcome you to InstaCertify. Your employee ID is <strong>{{ doc.name }}</strong>
					and your date of joining is <strong>{{ doc.date_of_joining }}</strong>.</p>
					<p>Designation: {{ doc.designation or '' }} · Department: {{ doc.department or '' }}</p>
					<p>Please keep this letter for your records. You can download salary slips and view the holiday calendar from your ERP profile.</p>
					<div style="position:absolute;right:16mm;bottom:16mm;text-align:center;font-size:9px;color:#5b6b78;">
						<img src="{{ qr_data_uri(doc.name) }}" style="width:28mm;height:28mm;">
						<div>Scan to verify joining record</div>
					</div>
				</div>
				""",
			}
		).insert(ignore_permissions=True)


def _upsert_print(name, dt, html, default=0):
	if frappe.db.exists("Print Format", name):
		frappe.db.set_value("Print Format", name, {"html": html, "custom_format": 1})
		return
	frappe.get_doc(
		{
			"doctype": "Print Format",
			"name": name,
			"doc_type": dt,
			"module": "InstaCertify",
			"standard": "No",
			"custom_format": 1,
			"print_format_type": "Jinja",
			"html": html,
			"default_print_language": "en",
			"font": "Default",
			"margin_top": 5,
			"margin_bottom": 5,
			"margin_left": 8,
			"margin_right": 8,
		}
	).insert(ignore_permissions=True)


def _number_cards():
	cards = [
		("IC Leads", "IC Lead", "count"),
		("IC Quotes", "IC Quotation", "count"),
		("IC Projects", "IC Project", "count"),
		("IC Labs", "IC Lab", "count"),
	]
	for label, dt, func in cards:
		if frappe.db.exists("Number Card", label):
			continue
		frappe.get_doc(
			{
				"doctype": "Number Card",
				"label": label,
				"document_type": dt,
				"function": "Count",
				"is_public": 1,
				"module": "InstaCertify",
				"show_percentage_stats": 0,
				"stats_time_interval": "Daily",
			}
		).insert(ignore_permissions=True)


def _home_workspace():
	name = "InstaCertify Home"
	content = [
		{
			"id": "greeting",
			"type": "header",
			"data": {"text": "<span class='h4'><b>InstaCertify Home</b></span>", "col": 12},
		},
		{"id": "spacer1", "type": "spacer", "data": {"col": 12}},
		{
			"id": "shortcut_crm",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Leads",
				"label": "CRM / Leads",
				"link_to": "IC Lead",
				"type": "DocType",
				"col": 3,
				"color": "Blue",
			},
		},
		{
			"id": "shortcut_cust",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Customers",
				"label": "Customers",
				"link_to": "IC Customer Profile",
				"type": "DocType",
				"col": 3,
				"color": "Orange",
			},
		},
		{
			"id": "shortcut_quote",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Quotations",
				"label": "Quotations",
				"link_to": "IC Quotation",
				"type": "DocType",
				"col": 3,
				"color": "Blue",
			},
		},
		{
			"id": "shortcut_proj",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Projects",
				"label": "Projects",
				"link_to": "IC Project",
				"type": "DocType",
				"col": 3,
				"color": "Orange",
			},
		},
		{
			"id": "shortcut_lab",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Labs",
				"label": "Lab Library",
				"link_to": "IC Lab",
				"type": "DocType",
				"col": 3,
				"color": "Blue",
			},
		},
		{
			"id": "shortcut_test",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Tests",
				"label": "Test Requests",
				"link_to": "IC Test Request",
				"type": "DocType",
				"col": 3,
				"color": "Orange",
			},
		},
		{
			"id": "shortcut_cal",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Calendar",
				"label": "Planner / Calendar",
				"link_to": "IC Planner Entry",
				"type": "DocType",
				"col": 3,
				"color": "Blue",
			},
		},
		{
			"id": "shortcut_asset",
			"type": "shortcut",
			"data": {
				"shortcut_name": "Assets",
				"label": "Asset Library",
				"link_to": "IC Asset Register",
				"type": "DocType",
				"col": 3,
				"color": "Orange",
			},
		},
		{
			"id": "nc1",
			"type": "number_card",
			"data": {"number_card_name": "IC Leads", "col": 3},
		},
		{
			"id": "nc2",
			"type": "number_card",
			"data": {"number_card_name": "IC Quotes", "col": 3},
		},
		{
			"id": "nc3",
			"type": "number_card",
			"data": {"number_card_name": "IC Projects", "col": 3},
		},
		{
			"id": "nc4",
			"type": "number_card",
			"data": {"number_card_name": "IC Labs", "col": 3},
		},
	]

	if frappe.db.exists("Workspace", name):
		ws = frappe.get_doc("Workspace", name)
		ws.content = frappe.as_json(content)
		ws.public = 1
		ws.save(ignore_permissions=True)
		return

	frappe.get_doc(
		{
			"doctype": "Workspace",
			"label": name,
			"title": name,
			"name": name,
			"public": 1,
			"module": "InstaCertify",
			"icon": "organization",
			"content": frappe.as_json(content),
			"shortcuts": [
				{"label": "New Quote", "link_to": "IC Quotation", "type": "DocType", "color": "Orange"},
				{"label": "New Lead", "link_to": "IC Lead", "type": "DocType", "color": "Blue"},
				{"label": "Labs", "link_to": "IC Lab", "type": "DocType", "color": "Blue"},
				{"label": "My Planner", "link_to": "IC Planner Entry", "type": "DocType", "color": "Orange"},
			],
			"links": [
				{
					"label": "CRM",
					"type": "Card Break",
				},
				{"label": "Leads", "type": "Link", "link_type": "DocType", "link_to": "IC Lead"},
				{"label": "Customers", "type": "Link", "link_type": "DocType", "link_to": "IC Customer Profile"},
				{"label": "Consultants", "type": "Link", "link_type": "DocType", "link_to": "IC Consultant"},
				{"label": "Commercial", "type": "Card Break"},
				{"label": "Quotations", "type": "Link", "link_type": "DocType", "link_to": "IC Quotation"},
				{"label": "Templates", "type": "Link", "link_type": "DocType", "link_to": "IC Quotation Template"},
				{"label": "Services", "type": "Link", "link_type": "DocType", "link_to": "IC Service Catalog"},
				{"label": "Delivery", "type": "Card Break"},
				{"label": "Projects", "type": "Link", "link_type": "DocType", "link_to": "IC Project"},
				{"label": "Test Requests", "type": "Link", "link_type": "DocType", "link_to": "IC Test Request"},
				{"label": "Labs", "type": "Link", "link_type": "DocType", "link_to": "IC Lab"},
				{"label": "People & Assets", "type": "Card Break"},
				{"label": "Planner", "type": "Link", "link_type": "DocType", "link_to": "IC Planner Entry"},
				{"label": "Assets", "type": "Link", "link_type": "DocType", "link_to": "IC Asset Register"},
			],
		}
	).insert(ignore_permissions=True)


def _module_workspaces():
	defs = [
		("IC CRM", "CRM", [("IC Lead", "Leads"), ("IC Consultant", "Consultants")]),
		("IC Customers", "Customers", [("IC Customer Profile", "Customer Profiles")]),
		("IC Projects", "Projects", [("IC Project", "Projects"), ("IC Test Request", "Test Requests")]),
		("IC Labs", "Labs", [("IC Lab", "Lab Library"), ("IC Service Catalog", "Services")]),
		("IC Calendar", "Calendar", [("IC Planner Entry", "Planner")]),
	]
	for name, _title, links in defs:
		if frappe.db.exists("Workspace", name):
			continue
		frappe.get_doc(
			{
				"doctype": "Workspace",
				"name": name,
				"label": name,
				"title": name,
				"public": 1,
				"module": "InstaCertify",
				"icon": "folder",
				"content": "[]",
				"links": [{"label": "Links", "type": "Card Break"}]
				+ [
					{"label": label, "type": "Link", "link_type": "DocType", "link_to": dt}
					for dt, label in links
				],
			}
		).insert(ignore_permissions=True)
