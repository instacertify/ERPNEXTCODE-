# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

from secrets import token_urlsafe

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class ICTestRequest(Document):
	def validate(self):
		if self.sample_status == "Sample Received" and not self.sample_qr_code:
			self._generate_sample_qr()

	def _generate_sample_qr(self):
		self.share_token = self.share_token or token_urlsafe(16)
		self.sample_qr_code = f"ICSAMPLE-{self.name or 'NEW'}-{frappe.generate_hash(length=8).upper()}"
		self.sample_qr_link = f"{frappe.utils.get_url()}/ic-sample?token={self.share_token}"

	def on_update(self):
		pass


def on_update(doc, method=None):
	# append status history when status changes
	if doc.has_value_changed("sample_status"):
		doc.append(
			"status_history",
			{
				"status": doc.sample_status,
				"at": now_datetime(),
				"by_user": frappe.session.user,
			},
		)
		# avoid recursion: use db_insert of child via sql-safe path
		frappe.db.sql(
			"""
			insert into `tabIC Sample Status Log`
			(name, creation, modified, modified_by, owner, parent, parentfield, parenttype, idx, status, at, by_user)
			values (%s, %s, %s, %s, %s, %s, 'status_history', 'IC Test Request', %s, %s, %s, %s)
			""",
			(
				frappe.generate_hash(length=10),
				now_datetime(),
				now_datetime(),
				frappe.session.user,
				frappe.session.user,
				doc.name,
				len(doc.status_history or []) + 1,
				doc.sample_status,
				now_datetime(),
				frappe.session.user,
			),
		)
		if doc.sample_status == "Sample Received" and not doc.sample_qr_code:
			doc._generate_sample_qr()
			doc.db_set("sample_qr_code", doc.sample_qr_code)
			doc.db_set("sample_qr_link", doc.sample_qr_link)
			doc.db_set("share_token", doc.share_token)

	if doc.sample_status == "Report Uploaded" and doc.report_file and not doc.report_share_link:
		token = doc.share_token or token_urlsafe(16)
		link = f"{frappe.utils.get_url()}/ic-report?token={token}"
		doc.db_set("share_token", token)
		doc.db_set("report_share_link", link)


@frappe.whitelist()
def generate_sample_qr(test_request: str):
	doc = frappe.get_doc("IC Test Request", test_request)
	doc.check_permission("write")
	doc._generate_sample_qr()
	doc.save()
	return {"sample_qr_code": doc.sample_qr_code, "sample_qr_link": doc.sample_qr_link}


@frappe.whitelist()
def share_report(test_request: str):
	doc = frappe.get_doc("IC Test Request", test_request)
	doc.check_permission("write")
	if not doc.report_file:
		frappe.throw("Upload the report before sharing")
	token = doc.share_token or token_urlsafe(16)
	link = f"{frappe.utils.get_url()}/ic-report?token={token}"
	doc.db_set("share_token", token)
	doc.db_set("report_share_link", link)
	doc.db_set("sample_status", "Shared with Customer")
	return {"report_share_link": link}
