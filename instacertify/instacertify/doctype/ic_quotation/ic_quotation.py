# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import json
from secrets import token_urlsafe

import frappe
from frappe.model.document import Document
from frappe.utils import flt, now_datetime


class ICQuotation(Document):
	def validate(self):
		self._ensure_barcode()
		self._load_template_if_needed()
		self._recompute_totals()

	def before_submit(self):
		if self.status == "Draft":
			self.status = "Draft"

	def _ensure_barcode(self):
		if not self.unique_barcode:
			self.unique_barcode = f"ICQ-{frappe.generate_hash(length=10).upper()}"

	def _load_template_if_needed(self):
		if not self.template or self.items:
			return
		# only auto-fill when items empty
		tpl = frappe.get_doc("IC Quotation Template", self.template)
		self.quote_type = self.quote_type or tpl.quote_type
		self.currency = self.currency or tpl.currency
		self.force_majeure = self.force_majeure or tpl.force_majeure
		self.terms_and_conditions = self.terms_and_conditions or tpl.terms_and_conditions
		if tpl.items_json:
			try:
				rows = json.loads(tpl.items_json)
			except Exception:
				rows = []
			for row in rows:
				self.append("items", row)

	def _recompute_totals(self):
		consulting = testing = govt = other = 0
		for item in self.items or []:
			c = flt(item.consulting_amount)
			t = flt(item.testing_charges)
			g = flt(item.government_fees)
			o = flt(item.other_charges)
			item.line_total = c + t + g + o
			consulting += c
			testing += t
			govt += g
			other += o
		self.consulting_total = consulting
		self.testing_lab_total = testing
		self.government_fees_total = govt
		self.other_charges_total = other
		self.our_revenue_total = consulting + testing
		self.grand_total = consulting + testing + govt + other


def validate(doc, method=None):
	pass


def on_update(doc, method=None):
	pass


@frappe.whitelist()
def apply_template(quotation: str, template: str):
	doc = frappe.get_doc("IC Quotation", quotation)
	tpl = frappe.get_doc("IC Quotation Template", template)
	doc.quote_type = tpl.quote_type
	doc.currency = tpl.currency or doc.currency
	doc.force_majeure = tpl.force_majeure
	doc.terms_and_conditions = tpl.terms_and_conditions
	doc.template = template
	doc.items = []
	if tpl.items_json:
		for row in json.loads(tpl.items_json):
			doc.append("items", row)
	doc.save()
	return doc.as_dict()


@frappe.whitelist()
def save_as_template(quotation: str, template_name: str):
	q = frappe.get_doc("IC Quotation", quotation)
	if frappe.db.exists("IC Quotation Template", template_name):
		frappe.throw(f"Template {template_name} already exists")
	items = []
	for i in q.items:
		items.append(
			{
				"item_type": i.item_type,
				"service": i.service,
				"description": i.description,
				"lab": i.lab,
				"lab_scope": i.lab_scope,
				"applicable_standard": i.applicable_standard,
				"accreditation": i.accreditation,
				"no_of_samples": i.no_of_samples,
				"testing_timeline": i.testing_timeline,
				"certification_timeline": i.certification_timeline,
				"consulting_amount": i.consulting_amount,
				"testing_charges": i.testing_charges,
				"government_fees": i.government_fees,
				"govt_paid_to": i.govt_paid_to,
				"other_charges": i.other_charges,
			}
		)
	tpl = frappe.get_doc(
		{
			"doctype": "IC Quotation Template",
			"template_name": template_name,
			"quote_type": q.quote_type,
			"currency": q.currency,
			"force_majeure": q.force_majeure,
			"terms_and_conditions": q.terms_and_conditions,
			"items_json": json.dumps(items),
			"is_active": 1,
		}
	).insert()
	return tpl.name


@frappe.whitelist()
def create_share_link(quotation: str):
	doc = frappe.get_doc("IC Quotation", quotation)
	doc.check_permission("write")
	if not doc.share_token:
		doc.share_token = token_urlsafe(24)
	doc.shared_by = frappe.session.user
	doc.status = "Shared"
	host = frappe.utils.get_url()
	doc.share_link = f"{host}/ic-quote?token={doc.share_token}"
	doc.save(ignore_permissions=True)
	return {"share_link": doc.share_link, "token": doc.share_token}


@frappe.whitelist(allow_guest=True)
def get_public_quote(token: str):
	name = frappe.db.get_value("IC Quotation", {"share_token": token}, "name")
	if not name:
		frappe.throw("Invalid or expired quote link", frappe.PermissionError)
	doc = frappe.get_doc("IC Quotation", name)
	return {
		"name": doc.name,
		"subject": doc.subject,
		"customer": doc.customer,
		"customer_name": frappe.db.get_value("IC Customer Profile", doc.customer, "company_name"),
		"currency": doc.currency,
		"quote_type": doc.quote_type,
		"status": doc.status,
		"unique_barcode": doc.unique_barcode,
		"certification_timeline": doc.certification_timeline,
		"force_majeure": doc.force_majeure,
		"terms_and_conditions": doc.terms_and_conditions,
		"consulting_total": doc.consulting_total,
		"testing_lab_total": doc.testing_lab_total,
		"government_fees_total": doc.government_fees_total,
		"other_charges_total": doc.other_charges_total,
		"our_revenue_total": doc.our_revenue_total,
		"grand_total": doc.grand_total,
		"items": [
			{
				"item_type": i.item_type,
				"description": i.description,
				"service": i.service,
				"lab_scope": i.lab_scope,
				"applicable_standard": i.applicable_standard,
				"accreditation": i.accreditation,
				"no_of_samples": i.no_of_samples,
				"testing_timeline": i.testing_timeline,
				"certification_timeline": i.certification_timeline,
				"consulting_amount": i.consulting_amount,
				"testing_charges": i.testing_charges,
				"government_fees": i.government_fees,
				"govt_paid_to": i.govt_paid_to,
				"other_charges": i.other_charges,
				"line_total": i.line_total,
			}
			for i in doc.items
		],
		"qr": frappe.call("instacertify.utils.qr.make_qr", payload=doc.unique_barcode),
	}


@frappe.whitelist(allow_guest=True)
def customer_respond(token: str, action: str, remarks: str | None = None):
	name = frappe.db.get_value("IC Quotation", {"share_token": token}, "name")
	if not name:
		frappe.throw("Invalid quote link", frappe.PermissionError)
	doc = frappe.get_doc("IC Quotation", name)
	action = (action or "").lower()
	if action == "accept":
		doc.status = "Accepted"
		doc.accepted_on = now_datetime()
		doc.customer_remarks = remarks
		doc.save(ignore_permissions=True)
		_notify_acceptance(doc)
	elif action == "changes":
		doc.status = "Changes Requested"
		doc.customer_remarks = remarks
		doc.save(ignore_permissions=True)
		_notify_changes(doc)
	else:
		frappe.throw("Unknown action")
	return {"status": doc.status}


def _notify_acceptance(doc):
	recipients = {doc.shared_by or doc.sales_person or doc.owner}
	admins = frappe.get_all(
		"Has Role", filters={"role": "IC Admin", "parenttype": "User"}, pluck="parent"
	)
	recipients.update(admins)
	recipients.discard(None)
	recipients.discard("Guest")
	if not recipients:
		return
	frappe.sendmail(
		recipients=list(recipients),
		subject=f"Quote accepted: {doc.name} — {doc.subject}",
		message=f"<p>Customer accepted quotation <b>{doc.name}</b> ({doc.subject}).</p>",
		now=True,
	)
	for user in recipients:
		frappe.get_doc(
			{
				"doctype": "Notification Log",
				"subject": f"Quote accepted: {doc.name}",
				"email_content": f"Customer accepted {doc.subject}",
				"type": "Alert",
				"document_type": "IC Quotation",
				"document_name": doc.name,
				"for_user": user,
			}
		).insert(ignore_permissions=True)


def _notify_changes(doc):
	user = doc.shared_by or doc.sales_person or doc.owner
	if not user:
		return
	frappe.get_doc(
		{
			"doctype": "Notification Log",
			"subject": f"Changes requested: {doc.name}",
			"email_content": doc.customer_remarks or "",
			"type": "Alert",
			"document_type": "IC Quotation",
			"document_name": doc.name,
			"for_user": user,
		}
	).insert(ignore_permissions=True)


@frappe.whitelist()
def start_project(quotation: str, project_name: str | None = None):
	q = frappe.get_doc("IC Quotation", quotation)
	q.check_permission("write")
	if q.status != "Accepted" and q.docstatus != 1:
		# allow if accepted
		if q.status != "Accepted":
			frappe.throw("Customer must accept the quote before starting a project")
	if q.project:
		return q.project
	name = project_name or f"{q.customer} — {q.subject}"
	project = frappe.get_doc(
		{
			"doctype": "IC Project",
			"project_name": name,
			"customer": q.customer,
			"quotation": q.name,
			"sales_person": q.sales_person,
			"currency": q.currency,
			"priority": "High",
			"status": "Pending",
			"card_color": "Blue",
		}
	).insert()
	q.db_set("project", project.name)
	q.db_set("status", "Converted to Project")
	return project.name


@frappe.whitelist()
def export_quotations_excel():
	"""Admin-only bulk export helper."""
	if "IC Admin" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
		frappe.throw("Only IC Admin can download full data exports", frappe.PermissionError)
	rows = frappe.get_all(
		"IC Quotation",
		fields=[
			"name",
			"subject",
			"customer",
			"quote_type",
			"currency",
			"status",
			"grand_total",
			"our_revenue_total",
			"sales_person",
			"modified",
		],
	)
	return rows
