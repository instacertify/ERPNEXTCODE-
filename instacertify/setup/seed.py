# Copyright (c) 2026, InstaCertify and contributors
# License: MIT
"""Demo seed — 5–6 quote types, labs, leads, projects, assets."""

from __future__ import annotations

import json
from datetime import date, timedelta

import frappe
from frappe.utils import add_days, now_datetime, random_string


FORCE_MAJEURE = """<p>Neither party shall be liable for any failure or delay in performing its obligations under this quotation if such failure or delay results from circumstances beyond reasonable control, including but not limited to acts of God, natural disasters, war, terrorism, riots, embargoes, acts of civil or military authorities, fire, floods, accidents, pandemic, strikes, or shortages of transportation, facilities, fuel, energy, labor, or materials.</p>"""

TERMS = """<ol>
<li>Quotation validity: 30 days from issue date unless otherwise stated.</li>
<li>Consulting and laboratory testing charges billed by InstaCertify constitute our revenue.</li>
<li>Government / statutory fees may be payable directly on the government portal or to the lab, as indicated line-wise.</li>
<li>Certification timelines are indicative and subject to completeness of documentation and statutory processing.</li>
<li>Sample quantity, applicable standards, and lab accreditation are as stated in the line items.</li>
<li>Taxes (GST / VAT) extra as applicable.</li>
<li>Payment terms: 50% advance to commence work; balance on submission / report release unless agreed otherwise.</li>
</ol>"""


def seed_demo_data(force: bool = False):
	if frappe.db.exists("IC Service Catalog", "BIS-CRS") and not force:
		frappe.logger().info("InstaCertify demo data already present")
		return

	_seed_consultants()
	_seed_services()
	_seed_labs()
	_seed_terms()
	customers = _seed_customers()
	_seed_leads(customers)
	templates = _seed_templates()
	quotes = _seed_quotations(customers, templates)
	projects = _seed_projects(customers, quotes)
	_seed_test_requests(customers, projects, quotes)
	_seed_assets()
	_seed_planner()
	frappe.db.commit()


def _seed_consultants():
	for row in (
		("Aarav Mehta", "BIS / CRS", "aarav.mehta@partner.example", "+91 98100 10001"),
		("Sofia Alvarez", "FCC / UL", "sofia@partner.example", "+1 415 555 0198"),
		("Priya Nair", "ISO / CE", "priya.nair@partner.example", "+91 98200 20002"),
	):
		name, spec, email, phone = row
		if frappe.db.exists("IC Consultant", name):
			continue
		frappe.get_doc(
			{
				"doctype": "IC Consultant",
				"consultant_name": name,
				"specialization": spec,
				"email": email,
				"phone": phone,
				"active": 1,
			}
		).insert(ignore_permissions=True)


def _seed_services():
	services = [
		{
			"service_code": "BIS-CRS",
			"service_name": "BIS CRS Certification",
			"category": "Service",
			"typical_timeline": "8–12 weeks",
			"default_consulting_inr": 85000,
			"default_consulting_usd": 1100,
			"description": "<p>End-to-end BIS CRS consulting for electronic products.</p>",
			"document_checklist": [
				{"item": "Business license / Company registration", "mandatory": 1},
				{"item": "Product photos & labeling artwork", "mandatory": 1},
				{"item": "BOM / critical component list", "mandatory": 1},
				{"item": "Factory address proof", "mandatory": 0},
			],
		},
		{
			"service_code": "BIS-RENEW",
			"service_name": "BIS License Renewal",
			"category": "Renewal",
			"typical_timeline": "3–5 weeks",
			"default_consulting_inr": 35000,
			"default_consulting_usd": 450,
			"description": "<p>Renewal support for existing BIS licenses.</p>",
			"document_checklist": [
				{"item": "Existing license copy", "mandatory": 1},
				{"item": "Production data (last year)", "mandatory": 1},
			],
		},
		{
			"service_code": "TEST-EMC",
			"service_name": "EMC / Safety Testing Package",
			"category": "Testing",
			"typical_timeline": "2–4 weeks",
			"default_consulting_inr": 15000,
			"default_consulting_usd": 200,
			"description": "<p>Coordination of EMC and safety tests at accredited labs.</p>",
			"document_checklist": [
				{"item": "Test Request Form", "mandatory": 1},
				{"item": "Sample photos", "mandatory": 1},
				{"item": "User manual", "mandatory": 0},
			],
		},
		{
			"service_code": "CE-MARK",
			"service_name": "CE Marking Consulting",
			"category": "Service",
			"typical_timeline": "6–10 weeks",
			"default_consulting_inr": 120000,
			"default_consulting_usd": 1450,
			"description": "<p>Technical file, DoC and CE pathway consulting.</p>",
			"document_checklist": [
				{"item": "Technical construction file outline", "mandatory": 1},
				{"item": "Risk assessment draft", "mandatory": 1},
			],
		},
		{
			"service_code": "ISO-CERT",
			"service_name": "ISO 9001 Certification Support",
			"category": "Certificate",
			"typical_timeline": "10–14 weeks",
			"default_consulting_inr": 95000,
			"default_consulting_usd": 1200,
			"description": "<p>Gap analysis, documentation and audit readiness.</p>",
			"document_checklist": [
				{"item": "Org chart", "mandatory": 1},
				{"item": "Process map", "mandatory": 1},
			],
		},
		{
			"service_code": "FCC-ID",
			"service_name": "FCC ID / SDoC Support",
			"category": "Service",
			"typical_timeline": "4–8 weeks",
			"default_consulting_inr": 0,
			"default_consulting_usd": 1800,
			"description": "<p>US market FCC pathway for wireless products.</p>",
			"document_checklist": [
				{"item": "Antenna specs", "mandatory": 1},
				{"item": "Block diagram", "mandatory": 1},
			],
		},
	]
	for s in services:
		if frappe.db.exists("IC Service Catalog", s["service_code"]):
			continue
		frappe.get_doc({"doctype": "IC Service Catalog", **s, "active": 1}).insert(
			ignore_permissions=True
		)


def _seed_labs():
	labs = [
		{
			"lab_name": "NABL Apex Test House — Pune",
			"location": "Pune, India",
			"accreditation": "NABL ISO/IEC 17025",
			"contact_email": "intake@apexlab.example",
			"scopes": [
				{
					"test_name": "EMC Radiated Emission",
					"applicable_standard": "CISPR 32",
					"accreditation_scope": "EMC — IT Equipment",
					"typical_timeline_days": 10,
					"purchase_price": 18000,
					"selling_price": 28000,
					"currency": "INR",
				},
				{
					"test_name": "Safety — IT Equipment",
					"applicable_standard": "IEC 62368-1",
					"accreditation_scope": "Safety",
					"typical_timeline_days": 14,
					"purchase_price": 22000,
					"selling_price": 35000,
					"currency": "INR",
				},
			],
		},
		{
			"lab_name": "GlobalCert Labs — Dubai",
			"location": "Dubai, UAE",
			"accreditation": "ILAC MRA",
			"contact_email": "ops@globalcert.example",
			"scopes": [
				{
					"test_name": "RF Conducted Power",
					"applicable_standard": "EN 300 328",
					"accreditation_scope": "Radio",
					"typical_timeline_days": 12,
					"purchase_price": 420,
					"selling_price": 680,
					"currency": "USD",
				}
			],
		},
		{
			"lab_name": "Pacific Safety Lab — Singapore",
			"location": "Singapore",
			"accreditation": "SAC-SINGLAS",
			"contact_email": "samples@psl.example",
			"scopes": [
				{
					"test_name": "Chemical RoHS screening",
					"applicable_standard": "IEC 62321",
					"accreditation_scope": "Chemical",
					"typical_timeline_days": 7,
					"purchase_price": 300,
					"selling_price": 520,
					"currency": "USD",
				}
			],
		},
	]
	for lab in labs:
		if frappe.db.exists("IC Lab", {"lab_name": lab["lab_name"]}):
			continue
		frappe.get_doc({"doctype": "IC Lab", **lab, "active": 1}).insert(ignore_permissions=True)


def _seed_terms():
	if frappe.db.exists("IC Terms Template", "Standard InstaCertify Terms"):
		return
	frappe.get_doc(
		{
			"doctype": "IC Terms Template",
			"title": "Standard InstaCertify Terms",
			"force_majeure": FORCE_MAJEURE,
			"terms_and_conditions": TERMS,
			"is_default": 1,
		}
	).insert(ignore_permissions=True)


def _seed_customers():
	rows = [
		{
			"company_name": "Nova Electronics Pvt Ltd",
			"company_size": "Medium",
			"gstin": "27AABCN1234A1Z5",
			"country": "India",
			"state": "Maharashtra",
			"billing_address": "Plot 12, MIDC Andheri, Mumbai 400093",
			"factory_address": "Unit 4, Chakan Industrial Area, Pune",
			"default_currency": "INR",
			"onboarded_on": add_days(date.today(), -120),
			"contacts": [
				{
					"person_name": "Rahul Deshmukh",
					"designation": "QA Head",
					"email": "rahul@novaelec.example",
					"phone": "+91 98765 43210",
					"is_primary": 1,
				},
				{
					"person_name": "Sneha Kulkarni",
					"designation": "Purchase",
					"email": "sneha@novaelec.example",
					"phone": "+91 98765 43211",
					"is_primary": 0,
					"factory_location": "Pune Factory",
				},
			],
		},
		{
			"company_name": "BrightWave Devices Inc",
			"company_size": "Large",
			"country": "United States",
			"billing_address": "500 Market St, San Francisco, CA",
			"factory_address": "Shenzhen OEM Partner Line A",
			"default_currency": "USD",
			"onboarded_on": add_days(date.today(), -60),
			"contacts": [
				{
					"person_name": "Emily Carter",
					"designation": "Compliance Manager",
					"email": "emily@brightwave.example",
					"phone": "+1 628 555 0144",
					"is_primary": 1,
				}
			],
		},
		{
			"company_name": "GreenGrid Energy LLP",
			"company_size": "Small",
			"gstin": "07AAGCG9988B1Z2",
			"country": "India",
			"state": "Delhi",
			"billing_address": "Okhla Phase II, New Delhi",
			"default_currency": "INR",
			"onboarded_on": add_days(date.today(), -30),
			"contacts": [
				{
					"person_name": "Imran Qureshi",
					"designation": "Founder",
					"email": "imran@greengrid.example",
					"phone": "+91 98111 22334",
					"is_primary": 1,
				}
			],
		},
		{
			"company_name": "Helios Appliance Co",
			"company_size": "Micro",
			"gstin": "29AABCH5566C1Z9",
			"country": "India",
			"state": "Karnataka",
			"billing_address": "Peenya Industrial Area, Bengaluru",
			"default_currency": "INR",
			"onboarded_on": add_days(date.today(), -200),
			"contacts": [
				{
					"person_name": "Ananya Rao",
					"designation": "Director",
					"email": "ananya@helios.example",
					"phone": "+91 99000 11223",
					"is_primary": 1,
				}
			],
		},
	]
	created = []
	for row in rows:
		existing = frappe.db.exists("IC Customer Profile", {"company_name": row["company_name"]})
		if existing:
			created.append(existing)
			continue
		doc = frappe.get_doc({"doctype": "IC Customer Profile", **row})
		doc.insert(ignore_permissions=True)
		created.append(doc.name)
	return created


def _seed_leads(customers):
	leads = [
		{
			"person_name": "Karan Shah",
			"company_name": "PixelForge Technologies",
			"request_type": "Service Request",
			"company_size": "Small",
			"country": "India",
			"state": "Gujarat",
			"phone": "+91 97277 88990",
			"email": "karan@pixelforge.example",
			"lead_source": "IndiaMART",
			"expected_timeline": "6 weeks",
			"status": "Qualified",
			"currency": "INR",
		},
		{
			"person_name": "Mia Johansson",
			"company_name": "Nordic IoT AB",
			"request_type": "Testing Request",
			"company_size": "Medium",
			"country": "Other",
			"phone": "+46 70 123 4567",
			"email": "mia@nordiciot.example",
			"lead_source": "Google",
			"expected_timeline": "1 month",
			"status": "New",
			"currency": "USD",
			"remarks": "Needs EMC + radio for EU and India.",
		},
		{
			"person_name": "Vikram Iyer",
			"company_name": "Helios Appliance Co",
			"request_type": "Service Request",
			"company_size": "Micro",
			"country": "India",
			"state": "Karnataka",
			"phone": "+91 99000 11224",
			"email": "vikram@helios.example",
			"lead_source": "Referral by Existing Customer",
			"expected_timeline": "Renewal this quarter",
			"status": "Quotation Sent",
			"currency": "INR",
		},
		{
			"person_name": "Chen Wei",
			"company_name": "Shenzhen Orbital Ltd",
			"request_type": "Mixed / Multiple",
			"company_size": "Large",
			"country": "Other",
			"phone": "+86 138 0000 1122",
			"email": "chen.wei@orbital.example",
			"lead_source": "Consultant",
			"consultant": "Sofia Alvarez",
			"status": "Contacted",
			"currency": "USD",
		},
		{
			"person_name": "Neha Gupta",
			"company_name": "UrbanCharge Solutions",
			"request_type": "Testing Request",
			"company_size": "Medium",
			"country": "India",
			"state": "Haryana",
			"phone": "+91 98100 44556",
			"email": "neha@urbancharge.example",
			"lead_source": "Direct Call",
			"status": "New",
			"currency": "INR",
		},
	]
	for lead in leads:
		if frappe.db.exists("IC Lead", {"email": lead["email"]}):
			continue
		frappe.get_doc({"doctype": "IC Lead", **lead}).insert(ignore_permissions=True)


def _seed_templates():
	templates = [
		{
			"template_name": "BIS CRS Standard (INR)",
			"quote_type": "Service",
			"service": "BIS-CRS",
			"currency": "INR",
			"force_majeure": FORCE_MAJEURE,
			"terms_and_conditions": TERMS,
			"items_json": json.dumps(
				[
					{
						"item_type": "Service",
						"service": "BIS-CRS",
						"description": "BIS CRS end-to-end consulting",
						"consulting_amount": 85000,
						"government_fees": 42000,
						"govt_paid_to": "Government Portal",
						"certification_timeline": "8–12 weeks",
					}
				]
			),
		},
		{
			"template_name": "EMC Testing Bundle",
			"quote_type": "Testing",
			"service": "TEST-EMC",
			"currency": "INR",
			"force_majeure": FORCE_MAJEURE,
			"terms_and_conditions": TERMS,
			"items_json": json.dumps(
				[
					{
						"item_type": "Testing",
						"service": "TEST-EMC",
						"description": "EMC radiated emission + safety",
						"lab_scope": "EMC Radiated Emission",
						"applicable_standard": "CISPR 32",
						"no_of_samples": 2,
						"consulting_amount": 15000,
						"testing_charges": 28000,
						"govt_paid_to": "Us",
						"testing_timeline": "10–14 days",
					}
				]
			),
		},
		{
			"template_name": "FCC ID Overseas (USD)",
			"quote_type": "Service",
			"service": "FCC-ID",
			"currency": "USD",
			"force_majeure": FORCE_MAJEURE,
			"terms_and_conditions": TERMS,
			"items_json": json.dumps(
				[
					{
						"item_type": "Service",
						"service": "FCC-ID",
						"description": "FCC ID consulting & filing support",
						"consulting_amount": 1800,
						"testing_charges": 680,
						"govt_paid_to": "Lab Directly",
						"certification_timeline": "4–8 weeks",
					}
				]
			),
		},
	]
	names = []
	for t in templates:
		if frappe.db.exists("IC Quotation Template", t["template_name"]):
			names.append(t["template_name"])
			continue
		doc = frappe.get_doc({"doctype": "IC Quotation Template", **t, "is_active": 1})
		doc.insert(ignore_permissions=True)
		names.append(doc.name)
	return names


def _seed_quotations(customers, templates):
	nova, bright, green, helios = customers[:4]
	specs = [
		{
			"quote_type": "Service",
			"subject": "BIS CRS — Smart Plug Series A",
			"customer": nova,
			"currency": "INR",
			"template": templates[0] if templates else None,
			"certification_timeline": "10 weeks",
			"items": [
				{
					"item_type": "Service",
					"service": "BIS-CRS",
					"description": "BIS CRS consulting for Smart Plug",
					"consulting_amount": 85000,
					"government_fees": 42000,
					"govt_paid_to": "Government Portal",
					"certification_timeline": "8–12 weeks",
				}
			],
		},
		{
			"quote_type": "Testing",
			"subject": "EMC + Safety — Charger PCB",
			"customer": green,
			"currency": "INR",
			"certification_timeline": "3 weeks testing",
			"items": [
				{
					"item_type": "Testing",
					"service": "TEST-EMC",
					"description": "EMC radiated emission",
					"lab_scope": "EMC Radiated Emission",
					"applicable_standard": "CISPR 32",
					"accreditation": "NABL ISO/IEC 17025",
					"no_of_samples": 2,
					"testing_timeline": "10 days",
					"consulting_amount": 15000,
					"testing_charges": 28000,
					"govt_paid_to": "Us",
				},
				{
					"item_type": "Testing",
					"service": "TEST-EMC",
					"description": "Safety IEC 62368-1",
					"lab_scope": "Safety — IT Equipment",
					"applicable_standard": "IEC 62368-1",
					"no_of_samples": 1,
					"testing_timeline": "14 days",
					"consulting_amount": 10000,
					"testing_charges": 35000,
					"govt_paid_to": "Us",
				},
			],
		},
		{
			"quote_type": "Certificate",
			"subject": "ISO 9001 Certificate Support",
			"customer": helios,
			"currency": "INR",
			"items": [
				{
					"item_type": "Certificate",
					"service": "ISO-CERT",
					"description": "ISO 9001 documentation & audit readiness",
					"consulting_amount": 95000,
					"other_charges": 5000,
					"govt_paid_to": "Us",
					"certification_timeline": "12 weeks",
				}
			],
		},
		{
			"quote_type": "Renewal",
			"subject": "BIS License Renewal FY26",
			"customer": helios,
			"currency": "INR",
			"items": [
				{
					"item_type": "Renewal",
					"service": "BIS-RENEW",
					"description": "Renewal consulting",
					"consulting_amount": 35000,
					"government_fees": 18000,
					"govt_paid_to": "Government Portal",
					"certification_timeline": "4 weeks",
				}
			],
		},
		{
			"quote_type": "Service",
			"subject": "FCC ID — Wi-Fi Module X200",
			"customer": bright,
			"currency": "USD",
			"items": [
				{
					"item_type": "Service",
					"service": "FCC-ID",
					"description": "FCC consulting",
					"consulting_amount": 1800,
					"testing_charges": 680,
					"govt_paid_to": "Lab Directly",
					"applicable_standard": "FCC Part 15",
					"certification_timeline": "6 weeks",
				}
			],
		},
		{
			"quote_type": "Multiple Product",
			"subject": "CE + RoHS Multi-SKU Bundle",
			"customer": bright,
			"currency": "USD",
			"items": [
				{
					"item_type": "Service",
					"service": "CE-MARK",
					"description": "CE marking — SKU family",
					"consulting_amount": 1450,
					"certification_timeline": "8 weeks",
				},
				{
					"item_type": "Testing",
					"service": "TEST-EMC",
					"description": "RoHS screening 3 SKUs",
					"lab_scope": "Chemical RoHS screening",
					"applicable_standard": "IEC 62321",
					"no_of_samples": 3,
					"testing_charges": 1560,
					"consulting_amount": 200,
					"govt_paid_to": "Us",
					"testing_timeline": "7 days",
				},
			],
		},
	]
	created = []
	for spec in specs:
		if frappe.db.exists("IC Quotation", {"subject": spec["subject"]}):
			created.append(frappe.db.get_value("IC Quotation", {"subject": spec["subject"]}, "name"))
			continue
		doc = frappe.get_doc(
			{
				"doctype": "IC Quotation",
				"force_majeure": FORCE_MAJEURE,
				"terms_and_conditions": TERMS,
				**{k: v for k, v in spec.items() if k != "items"},
				"items": spec["items"],
			}
		)
		doc.insert(ignore_permissions=True)
		created.append(doc.name)
	return created


def _seed_projects(customers, quotes):
	nova, bright, green, helios = customers[:4]
	rows = [
		{
			"project_name": "Nova — BIS CRS Smart Plug",
			"customer": nova,
			"quotation": quotes[0] if quotes else None,
			"priority": "High",
			"status": "In Progress",
			"progress_percent": 45,
			"card_color": "Blue",
			"expected_end": add_days(date.today(), 40),
			"progress_log": [
				{"remark": "Application dossier drafted", "percent": 20},
				{"remark": "Lab slot booked for safety", "percent": 45},
			],
		},
		{
			"project_name": "GreenGrid — EMC Charger",
			"customer": green,
			"quotation": quotes[1] if len(quotes) > 1 else None,
			"priority": "Critical",
			"status": "Waiting on Lab",
			"progress_percent": 60,
			"card_color": "Orange",
			"expected_end": add_days(date.today(), 18),
			"progress_log": [{"remark": "Samples dispatched to Apex Lab", "percent": 60}],
		},
		{
			"project_name": "Helios — ISO 9001",
			"customer": helios,
			"quotation": quotes[2] if len(quotes) > 2 else None,
			"priority": "Medium",
			"status": "Pending",
			"progress_percent": 10,
			"card_color": "Teal",
			"expected_end": add_days(date.today(), 90),
		},
		{
			"project_name": "Helios — BIS Renewal",
			"customer": helios,
			"quotation": quotes[3] if len(quotes) > 3 else None,
			"priority": "High",
			"status": "In Progress",
			"progress_percent": 30,
			"card_color": "Blue",
			"expected_end": add_days(date.today(), 25),
		},
		{
			"project_name": "BrightWave — FCC Module",
			"customer": bright,
			"quotation": quotes[4] if len(quotes) > 4 else None,
			"priority": "High",
			"status": "In Progress",
			"progress_percent": 55,
			"card_color": "Orange",
			"currency": "USD",
			"expected_end": add_days(date.today(), 35),
		},
		{
			"project_name": "BrightWave — CE Multi-SKU",
			"customer": bright,
			"quotation": quotes[5] if len(quotes) > 5 else None,
			"priority": "Medium",
			"status": "Waiting on Client",
			"progress_percent": 25,
			"card_color": "Slate",
			"currency": "USD",
			"expected_end": add_days(date.today(), 70),
		},
		{
			"project_name": "Nova — Label Artwork Revision",
			"customer": nova,
			"priority": "Low",
			"status": "On Hold",
			"progress_percent": 5,
			"card_color": "Slate",
			"expected_end": add_days(date.today(), 120),
		},
		{
			"project_name": "GreenGrid — Retest Contingency",
			"customer": green,
			"priority": "Medium",
			"status": "Pending",
			"progress_percent": 0,
			"card_color": "Teal",
			"expected_end": add_days(date.today(), 60),
		},
	]
	names = []
	for row in rows:
		if frappe.db.exists("IC Project", {"project_name": row["project_name"]}):
			names.append(frappe.db.get_value("IC Project", {"project_name": row["project_name"]}, "name"))
			continue
		doc = frappe.get_doc({"doctype": "IC Project", **row})
		doc.insert(ignore_permissions=True)
		names.append(doc.name)
	return names


def _seed_test_requests(customers, projects, quotes):
	green = customers[2]
	lab = frappe.db.get_value("IC Lab", {"lab_name": "NABL Apex Test House — Pune"}, "name")
	if frappe.db.exists("IC Test Request", {"title": "Charger PCB EMC — GreenGrid"}):
		return
	frappe.get_doc(
		{
			"doctype": "IC Test Request",
			"title": "Charger PCB EMC — GreenGrid",
			"customer": green,
			"project": projects[1] if len(projects) > 1 else None,
			"quotation": quotes[1] if len(quotes) > 1 else None,
			"lab": lab,
			"applicable_standard": "CISPR 32",
			"no_of_samples": 2,
			"testing_charges": 28000,
			"currency": "INR",
			"sample_status": "Dispatched to Lab",
			"checklist": [
				{"checklist_item": "Test Request Form", "uploaded_by_customer": 1},
				{"checklist_item": "Sample photos", "uploaded_by_customer": 1},
				{"checklist_item": "User manual", "uploaded_by_customer": 0},
			],
			"status_history": [
				{"status": "Sample Received", "remark": "Courier AWB 998877"},
				{"status": "Dispatched to Lab", "remark": "Handed to Apex Pune"},
			],
		}
	).insert(ignore_permissions=True)


def _seed_assets():
	assets = [
		{"asset_name": 'Dell Latitude 5540', "asset_value": 78000, "location": "Mumbai HQ", "status": "In Use"},
		{"asset_name": "Sample Storage Cabinet", "asset_value": 24000, "location": "Pune Ops", "status": "In Use"},
		{"asset_name": "Canon Scanner DR-C240", "asset_value": 42000, "location": "Delhi Desk", "status": "In Store"},
	]
	for a in assets:
		if frappe.db.exists("IC Asset Register", {"asset_name": a["asset_name"]}):
			continue
		frappe.get_doc(
			{
				"doctype": "IC Asset Register",
				**a,
				"acquired_on": add_days(date.today(), -90),
			}
		).insert(ignore_permissions=True)


def _seed_planner():
	user = frappe.session.user if frappe.session.user not in ("Guest", "Administrator") else "Administrator"
	if frappe.db.exists("IC Planner Entry", {"title": "Client call — Nova BIS"}):
		return
	frappe.get_doc(
		{
			"doctype": "IC Planner Entry",
			"title": "Client call — Nova BIS",
			"for_user": user,
			"plan_date": date.today(),
			"start_slot": "10:00",
			"end_slot": "10:30",
			"color": "Blue",
			"description": "Review dossier gaps",
		}
	).insert(ignore_permissions=True)
	frappe.get_doc(
		{
			"doctype": "IC Planner Entry",
			"title": "Lab follow-up — Apex",
			"for_user": user,
			"plan_date": date.today(),
			"start_slot": "15:00",
			"end_slot": "16:00",
			"color": "Orange",
		}
	).insert(ignore_permissions=True)
