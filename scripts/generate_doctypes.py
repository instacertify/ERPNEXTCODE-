#!/usr/bin/env python3
"""Generate InstaCertify DocType JSON definitions for ERPNext/Frappe."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DT_ROOT = ROOT / "instacertify" / "instacertify" / "doctype"


def field(fieldname, fieldtype, label=None, **kw):
    f = {
        "fieldname": fieldname,
        "fieldtype": fieldtype,
        "label": label or fieldname.replace("_", " ").title(),
    }
    f.update(kw)
    return f


def section(label, **kw):
    return field(label.lower().replace(" ", "_") + "_section", "Section Break", label, **kw)


def col(**kw):
    return field("column_break_" + str(kw.pop("n", os.urandom(2).hex())), "Column Break", "", **kw)


def write_doctype(name: str, meta: dict, children: list | None = None):
    slug = name.lower().replace(" ", "_")
    folder = DT_ROOT / slug
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "__init__.py").write_text("")
    doc = {
        "doctype": "DocType",
        "name": name,
        "module": "InstaCertify",
        "engine": "InnoDB",
        "is_tree": 0,
        "issingle": 0,
        "is_submittable": meta.get("is_submittable", 0),
        "istable": meta.get("istable", 0),
        "editable_grid": meta.get("editable_grid", 1),
        "track_changes": 1,
        "track_seen": 1,
        "track_views": 1,
        "custom": 0,
        "naming_rule": meta.get("naming_rule", "Expression"),
        "autoname": meta.get("autoname", f"format:IC-{slug.upper()[:3]}-.YYYY.-.#####"),
        "title_field": meta.get("title_field"),
        "search_fields": meta.get("search_fields"),
        "sort_field": "modified",
        "sort_order": "DESC",
        "permissions": meta.get("permissions", default_perms(meta.get("istable", 0))),
        "fields": meta["fields"],
        "links": meta.get("links", []),
        "actions": [],
        "allow_rename": meta.get("allow_rename", 1),
        "has_web_view": meta.get("has_web_view", 0),
        "index_web_pages_for_search": 0,
        "show_name_in_global_search": 1,
        "image_field": meta.get("image_field"),
        "quick_entry": meta.get("quick_entry", 0),
        "beta": 0,
    }
    # clean None
    doc = {k: v for k, v in doc.items() if v is not None}
    (folder / f"{slug}.json").write_text(json.dumps(doc, indent=1) + "\n")

    # controller stub
    class_name = "".join(p.title() for p in slug.split("_"))
    controller = f'''# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import frappe
from frappe.model.document import Document


class {class_name}(Document):
	pass
'''
    # keep existing richer controllers if present later
    py = folder / f"{slug}.py"
    if not py.exists():
        py.write_text(controller)

    js = folder / f"{slug}.js"
    if not js.exists() and not meta.get("istable"):
        js.write_text(
            f"""// Copyright (c) 2026, InstaCertify
frappe.ui.form.on('{name}', {{
	refresh(frm) {{
		instacertify.apply_form_polish(frm);
	}}
}});
"""
        )

    if children:
        for child_name, child_meta in children:
            child_meta["istable"] = 1
            child_meta["editable_grid"] = 1
            child_meta["naming_rule"] = "Random"
            child_meta["autoname"] = "hash"
            child_meta["permissions"] = []
            write_doctype(child_name, child_meta)


def default_perms(istable=0):
    if istable:
        return []
    roles = [
        ("IC Admin", 1, 1, 1, 1, 1, 1, 1),
        ("IC Ops Manager", 1, 1, 1, 1, 1, 1, 0),
        ("IC Operations Manager", 1, 1, 1, 1, 0, 1, 0),
        ("IC Sales Person", 1, 1, 1, 0, 0, 1, 0),
        ("System Manager", 1, 1, 1, 1, 1, 1, 1),
    ]
    out = []
    for role, read, write, create, delete, submit, export, import_ in roles:
        out.append(
            {
                "role": role,
                "read": read,
                "write": write,
                "create": create,
                "delete": delete,
                "submit": submit,
                "cancel": submit,
                "amend": submit,
                "report": 1,
                "export": export,
                "import": import_,
                "share": 1,
                "print": 1,
                "email": 1,
            }
        )
    return out


def indian_states():
    return "\\n".join(
        [
            "Andhra Pradesh",
            "Arunachal Pradesh",
            "Assam",
            "Bihar",
            "Chhattisgarh",
            "Goa",
            "Gujarat",
            "Haryana",
            "Himachal Pradesh",
            "Jharkhand",
            "Karnataka",
            "Kerala",
            "Madhya Pradesh",
            "Maharashtra",
            "Manipur",
            "Meghalaya",
            "Mizoram",
            "Nagaland",
            "Odisha",
            "Punjab",
            "Rajasthan",
            "Sikkim",
            "Tamil Nadu",
            "Telangana",
            "Tripura",
            "Uttar Pradesh",
            "Uttarakhand",
            "West Bengal",
            "Andaman and Nicobar Islands",
            "Chandigarh",
            "Dadra and Nagar Haveli and Daman and Diu",
            "Delhi",
            "Jammu and Kashmir",
            "Ladakh",
            "Lakshadweep",
            "Puducherry",
        ]
    )


def build():
    DT_ROOT.mkdir(parents=True, exist_ok=True)

    # --- IC Consultant ---
    write_doctype(
        "IC Consultant",
        {
            "autoname": "field:consultant_name",
            "naming_rule": "By fieldname",
            "title_field": "consultant_name",
            "search_fields": "email,phone,specialization",
            "fields": [
                field("consultant_name", "Data", "Consultant Name", reqd=1, unique=1),
                field("email", "Data", "Email", options="Email"),
                field("phone", "Data", "Phone"),
                field("specialization", "Data", "Specialization"),
                field("active", "Check", "Active", default=1),
                field("notes", "Small Text", "Notes"),
            ],
        },
    )

    # --- IC Lead ---
    write_doctype(
        "IC Lead",
        {
            "autoname": "format:LEAD-.YYYY.-.#####",
            "title_field": "person_name",
            "search_fields": "company_name,email,phone,lead_source",
            "fields": [
                section("Lead Details"),
                field("person_name", "Data", "Person Name", reqd=1, in_list_view=1),
                field("company_name", "Data", "Company Name", reqd=1, in_list_view=1),
                field(
                    "request_type",
                    "Select",
                    "Request Type",
                    options="\\nService Request\\nTesting Request\\nMixed / Multiple\\nOther",
                    reqd=1,
                    in_list_view=1,
                ),
                field(
                    "company_size",
                    "Select",
                    "Company Size",
                    options="\\nMicro\\nSmall\\nMedium\\nLarge",
                    in_list_view=1,
                ),
                col(n=1),
                field(
                    "country",
                    "Select",
                    "Country",
                    options="India\\nUnited States\\nUnited Kingdom\\nUAE\\nSingapore\\nGermany\\nOther",
                    default="India",
                    reqd=1,
                ),
                field(
                    "state",
                    "Select",
                    "State (India)",
                    options=indian_states(),
                    depends_on="eval:doc.country=='India'",
                ),
                field("phone", "Data", "Contact Number", reqd=1),
                field("email", "Data", "Email Address", options="Email", reqd=1),
                section("Source & Timeline"),
                field(
                    "lead_source",
                    "Select",
                    "Lead Source",
                    options="\\nGoogle\\nDirect Call\\nLead Generated\\nReferral by Existing Customer\\nIndiaMART\\nConsultant\\nWebsite\\nLinkedIn\\nOther",
                    reqd=1,
                    in_list_view=1,
                ),
                field(
                    "consultant",
                    "Link",
                    "Consultant",
                    options="IC Consultant",
                    depends_on="eval:doc.lead_source=='Consultant'",
                ),
                field("expected_timeline", "Data", "Expected Timeline"),
                col(n=2),
                field(
                    "status",
                    "Select",
                    "Status",
                    options="New\\nContacted\\nQualified\\nQuotation Sent\\nWon\\nLost\\nNurture",
                    default="New",
                    in_list_view=1,
                ),
                field("assigned_to", "Link", "Assigned To", options="User"),
                field("currency", "Link", "Preferred Currency", options="Currency", default="INR"),
                section("Optional Details"),
                field("address", "Small Text", "Company Address"),
                field("gstin", "Data", "GST Details / GSTIN"),
                field("remarks", "Text Editor", "Remarks"),
                field("converted_customer", "Link", "Converted Customer", options="IC Customer Profile", read_only=1),
            ],
        },
    )

    # --- IC Customer Profile ---
    write_doctype(
        "IC Customer Profile",
        {
            "autoname": "format:CUST-.YYYY.-.#####",
            "title_field": "company_name",
            "search_fields": "gstin,primary_email,country",
            "image_field": "image",
            "fields": [
                section("Company"),
                field("image", "Attach Image", "Logo"),
                field("company_name", "Data", "Company / Firm Name", reqd=1, in_list_view=1),
                field(
                    "company_size",
                    "Select",
                    "Company Size",
                    options="\\nMicro\\nSmall\\nMedium\\nLarge",
                ),
                field("gstin", "Data", "GST Number"),
                field("country", "Select", "Country", options="India\\nUnited States\\nUnited Kingdom\\nUAE\\nSingapore\\nGermany\\nOther", default="India"),
                field("state", "Select", "State", options=indian_states()),
                col(n=3),
                field("billing_address", "Small Text", "Registered / Billing Address"),
                field("factory_address", "Small Text", "Factory Address"),
                field("onboarded_on", "Date", "Date Onboarded", in_list_view=1),
                field("assigned_sales", "Link", "Assigned Sales Person", options="User", in_list_view=1),
                field("default_currency", "Link", "Default Currency", options="Currency", default="INR"),
                field("erpnext_customer", "Link", "ERPNext Customer", options="Customer"),
                section("Points of Contact"),
                field("contacts", "Table", "Contacts", options="IC Customer Contact"),
                section("Commercial"),
                field("past_quotes_html", "HTML", "Past Quotes"),
                field("invoices_html", "HTML", "Invoices"),
                section("Secure Notes"),
                field("login_credentials", "Password", "Login Credentials / Portal Access"),
                field("commitments", "Text Editor", "Commitments"),
                field("incidents", "Text Editor", "Incidents"),
                section("Deliverables & Files"),
                field("documents", "Table", "Project Documents", options="IC Customer Document"),
            ],
        },
        children=[
            (
                "IC Customer Contact",
                {
                    "fields": [
                        field("person_name", "Data", "Person Name", reqd=1, in_list_view=1),
                        field("designation", "Data", "Designation", in_list_view=1),
                        field("email", "Data", "Email", options="Email", in_list_view=1),
                        field("phone", "Data", "Phone", in_list_view=1),
                        field("is_primary", "Check", "Primary", in_list_view=1),
                        field("factory_location", "Data", "Factory / Site"),
                    ]
                },
            ),
            (
                "IC Customer Document",
                {
                    "fields": [
                        field("title", "Data", "Title", reqd=1, in_list_view=1),
                        field("document_type", "Select", "Type", options="PDF\\nImage\\nOther\\nDeliverable\\nCertificate", in_list_view=1),
                        field("file", "Attach", "File", reqd=1, in_list_view=1),
                        field("related_project", "Link", "Project", options="IC Project"),
                        field("remarks", "Small Text", "Remarks"),
                        field("uploaded_on", "Datetime", "Uploaded On", in_list_view=1),
                    ]
                },
            ),
        ],
    )

    # --- IC Service Catalog ---
    write_doctype(
        "IC Service Catalog",
        {
            "autoname": "field:service_code",
            "naming_rule": "By fieldname",
            "title_field": "service_name",
            "search_fields": "category,service_code",
            "fields": [
                field("service_code", "Data", "Service Code", reqd=1, unique=1),
                field("service_name", "Data", "Service Name", reqd=1, in_list_view=1),
                field(
                    "category",
                    "Select",
                    "Category",
                    options="Service\\nTesting\\nCertificate\\nRenewal\\nOther",
                    reqd=1,
                    in_list_view=1,
                ),
                field("typical_timeline", "Data", "Typical Certification Timeline"),
                field("description", "Text Editor", "Description"),
                field("default_consulting_inr", "Currency", "Default Consulting (INR)", options="INR"),
                field("default_consulting_usd", "Currency", "Default Consulting (USD)", options="USD"),
                field("document_checklist", "Table", "Document Checklist", options="IC Service Checklist Item"),
                field("active", "Check", "Active", default=1),
            ],
        },
        children=[
            (
                "IC Service Checklist Item",
                {
                    "fields": [
                        field("item", "Data", "Checklist Item", reqd=1, in_list_view=1),
                        field("mandatory", "Check", "Mandatory", default=1, in_list_view=1),
                        field("file_types", "Data", "Accepted File Types", default="PDF, Image", in_list_view=1),
                    ]
                },
            )
        ],
    )

    # --- IC Lab ---
    write_doctype(
        "IC Lab",
        {
            "autoname": "format:LAB-.####",
            "title_field": "lab_name",
            "search_fields": "location,accreditation",
            "fields": [
                section("Lab Identity"),
                field("lab_name", "Data", "Lab Name", reqd=1, in_list_view=1),
                field("location", "Data", "Location", in_list_view=1),
                field("accreditation", "Data", "Accreditation", in_list_view=1),
                field("contact_email", "Data", "Contact Email", options="Email"),
                field("contact_phone", "Data", "Contact Phone"),
                col(n=4),
                field("lab_scope_pdf", "Attach", "Lab Scope Sheet (PDF)"),
                field("accreditation_certificate", "Attach", "Accreditation Certificate"),
                field("active", "Check", "Active", default=1),
                field("notes", "Small Text", "Notes"),
                section("Testing Scope & Pricing"),
                field("scopes", "Table", "Testing Scopes", options="IC Lab Scope"),
            ],
            "permissions": [
                {
                    "role": "IC Admin",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "report": 1, "export": 1, "import": 1, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "IC Ops Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 0,
                    "report": 1, "export": 1, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "IC Operations Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 0,
                    "report": 1, "export": 0, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "IC Sales Person",
                    "read": 1, "write": 1, "create": 1, "delete": 0,
                    "report": 1, "export": 0, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "report": 1, "export": 1, "import": 1, "share": 1, "print": 1, "email": 1,
                },
            ],
        },
        children=[
            (
                "IC Lab Scope",
                {
                    "fields": [
                        field("test_name", "Data", "Name of Test", reqd=1, in_list_view=1),
                        field("applicable_standard", "Data", "Applicable Standard", in_list_view=1),
                        field("accreditation_scope", "Data", "Accreditation Scope"),
                        field("typical_timeline_days", "Int", "Timeline (Days)", in_list_view=1),
                        field("purchase_price", "Currency", "Purchase Price", in_list_view=0),
                        field("selling_price", "Currency", "Selling Price", in_list_view=1),
                        field("currency", "Link", "Currency", options="Currency", default="INR"),
                        field("scope_pdf", "Attach", "Scope PDF"),
                    ]
                },
            )
        ],
    )

    # --- IC Quotation Template ---
    write_doctype(
        "IC Quotation Template",
        {
            "autoname": "field:template_name",
            "naming_rule": "By fieldname",
            "title_field": "template_name",
            "search_fields": "quote_type,service",
            "fields": [
                field("template_name", "Data", "Template Name", reqd=1, unique=1, in_list_view=1),
                field(
                    "quote_type",
                    "Select",
                    "Quote Type",
                    options="Service\\nTesting\\nCertificate\\nRenewal\\nMultiple Product\\nOther",
                    reqd=1,
                    in_list_view=1,
                ),
                field("service", "Link", "Primary Service", options="IC Service Catalog"),
                field("currency", "Link", "Currency", options="Currency", default="INR"),
                field("force_majeure", "Text Editor", "Force Majeure"),
                field("terms_and_conditions", "Text Editor", "Terms and Conditions"),
                field("items_json", "Long Text", "Serialized Items JSON", hidden=1),
                field("created_by_user", "Link", "Created By", options="User", default="__user"),
                field("is_active", "Check", "Active", default=1),
                field("notes", "Small Text", "Notes"),
            ],
            "permissions": [
                {
                    "role": "IC Admin",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "report": 1, "export": 1, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "IC Ops Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 0,
                    "report": 1, "export": 1, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "IC Sales Person",
                    "read": 1, "write": 1, "create": 1, "delete": 0,
                    "report": 1, "export": 0, "share": 1, "print": 1, "email": 1,
                },
                {
                    "role": "IC Operations Manager",
                    "read": 1, "write": 0, "create": 0, "delete": 0,
                    "report": 1, "export": 0, "share": 0, "print": 1, "email": 0,
                },
                {
                    "role": "System Manager",
                    "read": 1, "write": 1, "create": 1, "delete": 1,
                    "report": 1, "export": 1, "share": 1, "print": 1, "email": 1,
                },
            ],
        },
    )

    # --- IC Quotation ---
    write_doctype(
        "IC Quotation",
        {
            "autoname": "format:QT-.YYYY.-.#####",
            "title_field": "subject",
            "search_fields": "customer,quote_type,status,currency",
            "is_submittable": 1,
            "fields": [
                section("Create Quote For"),
                field(
                    "quote_type",
                    "Select",
                    "Quote For",
                    options="Service\\nTesting\\nCertificate\\nRenewal\\nMultiple Product\\nOther",
                    reqd=1,
                    in_list_view=1,
                ),
                field("template", "Link", "Load From Template", options="IC Quotation Template"),
                field("subject", "Data", "Subject", reqd=1, in_list_view=1),
                field("unique_barcode", "Data", "UniQuote Barcode", read_only=1),
                col(n=5),
                field("customer", "Link", "Customer", options="IC Customer Profile", reqd=1, in_list_view=1),
                field("lead", "Link", "Source Lead", options="IC Lead"),
                field("currency", "Link", "Currency", options="Currency", default="INR", reqd=1),
                field(
                    "status",
                    "Select",
                    "Status",
                    options="Draft\\nShared\\nAccepted\\nChanges Requested\\nRejected\\nConverted to Project",
                    default="Draft",
                    in_list_view=1,
                    read_only=1,
                ),
                section("Ownership"),
                field("sales_person", "Link", "Sales Person", options="User", default="__user"),
                field("shared_by", "Link", "Shared By", options="User", read_only=1),
                field("share_token", "Data", "Share Token", read_only=1, hidden=1),
                field("share_link", "Data", "Customer Share Link", read_only=1),
                field("customer_remarks", "Text Editor", "Customer Change Remarks", read_only=1),
                field("accepted_on", "Datetime", "Accepted On", read_only=1),
                section("Line Items"),
                field("items", "Table", "Items", options="IC Quotation Item"),
                section("Cost Summary"),
                field("consulting_total", "Currency", "Consulting (Revenue)", options="currency", read_only=1),
                field("testing_lab_total", "Currency", "Lab / Testing (Revenue)", options="currency", read_only=1),
                field("government_fees_total", "Currency", "Government Fees", options="currency", read_only=1),
                field("other_charges_total", "Currency", "Other Charges", options="currency", read_only=1),
                col(n=6),
                field("our_revenue_total", "Currency", "Our Revenue (Consulting + Lab)", options="currency", read_only=1),
                field("grand_total", "Currency", "Grand Total", options="currency", read_only=1, in_list_view=1),
                field("payment_notes", "Small Text", "Payment Notes (portal / lab / us)"),
                section("Certification & Testing Context"),
                field("certification_timeline", "Data", "Certification Timeline"),
                field("force_majeure", "Text Editor", "Force Majeure"),
                field("terms_and_conditions", "Text Editor", "Terms and Conditions"),
                field("internal_notes", "Small Text", "Internal Notes"),
                section("Linked Project"),
                field("project", "Link", "Project", options="IC Project", read_only=1),
            ],
        },
        children=[
            (
                "IC Quotation Item",
                {
                    "fields": [
                        field(
                            "item_type",
                            "Select",
                            "Type",
                            options="Service\\nTesting\\nCertificate\\nRenewal\\nOther",
                            reqd=1,
                            in_list_view=1,
                        ),
                        field("service", "Link", "Service", options="IC Service Catalog", in_list_view=1),
                        field("description", "Small Text", "Description", in_list_view=1),
                        field("lab", "Link", "Lab", options="IC Lab"),
                        field("lab_scope", "Data", "Test / Scope Name"),
                        field("applicable_standard", "Data", "Applicable Standard"),
                        field("accreditation", "Data", "Lab Accreditation"),
                        field("no_of_samples", "Int", "No. of Samples", default=1),
                        field("testing_timeline", "Data", "Testing Timeline"),
                        field("certification_timeline", "Data", "Certification Timeline"),
                        field("consulting_amount", "Currency", "Consulting Fee", in_list_view=1),
                        field("testing_charges", "Currency", "Testing / Lab Charges", in_list_view=1),
                        field("government_fees", "Currency", "Government Fees"),
                        field(
                            "govt_paid_to",
                            "Select",
                            "Govt / Lab Paid To",
                            options="Us\\nGovernment Portal\\nLab Directly\\nSplit",
                        ),
                        field("other_charges", "Currency", "Other Charges"),
                        field("line_total", "Currency", "Line Total", read_only=1, in_list_view=1),
                    ]
                },
            )
        ],
    )

    # --- IC Project ---
    write_doctype(
        "IC Project",
        {
            "autoname": "format:PRJ-.YYYY.-.#####",
            "title_field": "project_name",
            "search_fields": "customer,priority,status",
            "fields": [
                section("Project"),
                field("project_name", "Data", "Project Name", reqd=1, in_list_view=1),
                field("customer", "Link", "Client", options="IC Customer Profile", reqd=1, in_list_view=1),
                field("quotation", "Link", "Source Quotation", options="IC Quotation"),
                field(
                    "priority",
                    "Select",
                    "Priority",
                    options="Low\\nMedium\\nHigh\\nCritical",
                    default="Medium",
                    in_list_view=1,
                ),
                col(n=7),
                field(
                    "status",
                    "Select",
                    "Status",
                    options="Pending\\nIn Progress\\nWaiting on Client\\nWaiting on Lab\\nCompleted\\nOn Hold",
                    default="Pending",
                    in_list_view=1,
                ),
                field("sales_person", "Link", "Sales Person", options="User"),
                field("operations_owner", "Link", "Operations Owner", options="User"),
                field("currency", "Link", "Currency", options="Currency", default="INR"),
                field("expected_end", "Date", "Expected End"),
                field("progress_percent", "Percent", "% Complete", in_list_view=1),
                section("Progress & Hours"),
                field("progress_log", "Table", "Progress Remarks", options="IC Project Progress"),
                field("working_hours", "Table", "Working Hours", options="IC Project Hours"),
                section("Colour Card"),
                field("card_color", "Select", "Card Colour", options="Blue\\nOrange\\nTeal\\nSlate", default="Blue"),
            ],
        },
        children=[
            (
                "IC Project Progress",
                {
                    "fields": [
                        field("date", "Datetime", "Date", in_list_view=1, default="Now"),
                        field("remark", "Small Text", "Remark", reqd=1, in_list_view=1),
                        field("percent", "Percent", "Progress %", in_list_view=1),
                        field("user", "Link", "By", options="User", default="__user"),
                    ]
                },
            ),
            (
                "IC Project Hours",
                {
                    "fields": [
                        field("date", "Date", "Date", reqd=1, in_list_view=1),
                        field("employee", "Link", "Employee", options="User", reqd=1, in_list_view=1),
                        field("hours", "Float", "Hours", reqd=1, in_list_view=1),
                        field("activity", "Data", "Activity", in_list_view=1),
                    ]
                },
            ),
        ],
    )

    # --- IC Test Request ---
    write_doctype(
        "IC Test Request",
        {
            "autoname": "format:TR-.YYYY.-.#####",
            "title_field": "title",
            "search_fields": "customer,lab,sample_status",
            "fields": [
                section("Request"),
                field("title", "Data", "Title", reqd=1, in_list_view=1),
                field("customer", "Link", "Customer", options="IC Customer Profile", reqd=1),
                field("project", "Link", "Project", options="IC Project"),
                field("quotation", "Link", "Quotation", options="IC Quotation"),
                field("lab", "Link", "Lab", options="IC Lab", in_list_view=1),
                col(n=8),
                field("applicable_standard", "Data", "Applicable Standard"),
                field("no_of_samples", "Int", "No. of Samples", default=1),
                field("testing_charges", "Currency", "Testing Charges"),
                field("currency", "Link", "Currency", options="Currency", default="INR"),
                field(
                    "sample_status",
                    "Select",
                    "Sample Status",
                    options="Awaiting Sample\\nSample Received\\nDispatched to Lab\\nTesting in Process\\nReport Available\\nReport Uploaded\\nShared with Customer",
                    default="Awaiting Sample",
                    in_list_view=1,
                ),
                section("QR & Sharing"),
                field("sample_qr_code", "Data", "Sample QR Payload", read_only=1),
                field("sample_qr_link", "Data", "Sample Tracking Link", read_only=1),
                field("report_file", "Attach", "Test Report"),
                field("report_share_link", "Data", "Report Share Link", read_only=1),
                field("share_token", "Data", "Share Token", hidden=1, read_only=1),
                section("Customer Checklist Uploads"),
                field("checklist", "Table", "Checklist Files", options="IC Test Checklist File"),
                field("status_history", "Table", "Status History", options="IC Sample Status Log"),
                field("notes", "Text Editor", "Notes"),
            ],
        },
        children=[
            (
                "IC Test Checklist File",
                {
                    "fields": [
                        field("checklist_item", "Data", "Checklist Item", reqd=1, in_list_view=1),
                        field("file", "Attach", "Uploaded File", in_list_view=1),
                        field("uploaded_by_customer", "Check", "By Customer", in_list_view=1),
                        field("uploaded_on", "Datetime", "Uploaded On"),
                        field("reviewed", "Check", "Reviewed"),
                    ]
                },
            ),
            (
                "IC Sample Status Log",
                {
                    "fields": [
                        field("status", "Data", "Status", in_list_view=1),
                        field("at", "Datetime", "At", in_list_view=1, default="Now"),
                        field("by_user", "Link", "By", options="User"),
                        field("remark", "Small Text", "Remark"),
                    ]
                },
            ),
        ],
    )

    # --- IC Asset Register ---
    write_doctype(
        "IC Asset Register",
        {
            "autoname": "format:AST-.YYYY.-.#####",
            "title_field": "asset_name",
            "search_fields": "asset_code,custodian",
            "fields": [
                field("asset_name", "Data", "Asset Name", reqd=1, in_list_view=1),
                field("asset_code", "Data", "Asset Code", read_only=1, in_list_view=1),
                field("acquired_on", "Date", "Acquired On", reqd=1),
                field("asset_value", "Currency", "Value", options="INR", in_list_view=1),
                field("custodian", "Link", "Who Has the Asset", options="User", in_list_view=1),
                field("location", "Data", "Location"),
                field("status", "Select", "Status", options="In Use\\nIn Store\\nUnder Repair\\nDisposed", default="In Use"),
                field("photo", "Attach Image", "Photo"),
                field("notes", "Small Text", "Notes"),
                field("registered_by", "Link", "Registered By", options="User", default="__user"),
            ],
        },
    )

    # --- IC Planner Entry (30-min calendar) ---
    write_doctype(
        "IC Planner Entry",
        {
            "autoname": "format:PLN-.YYYY.-.#####",
            "title_field": "title",
            "search_fields": "owner_user,for_user",
            "fields": [
                field("title", "Data", "Task / Title", reqd=1, in_list_view=1),
                field("owner_user", "Link", "Created By", options="User", default="__user"),
                field("for_user", "Link", "Team Member", options="User", reqd=1, in_list_view=1),
                field("plan_date", "Date", "Date", reqd=1, in_list_view=1),
                field(
                    "start_slot",
                    "Select",
                    "Start (30-min)",
                    options=slot_options(),
                    reqd=1,
                    in_list_view=1,
                ),
                field(
                    "end_slot",
                    "Select",
                    "End (30-min)",
                    options=slot_options(),
                    reqd=1,
                ),
                field("all_day", "Check", "All Day"),
                field("project", "Link", "Related Project", options="IC Project"),
                field("description", "Small Text", "Description"),
                field("color", "Select", "Colour", options="Blue\\nOrange\\nTeal\\nSlate", default="Orange"),
            ],
        },
    )

    # --- IC Terms Template ---
    write_doctype(
        "IC Terms Template",
        {
            "autoname": "field:title",
            "naming_rule": "By fieldname",
            "title_field": "title",
            "fields": [
                field("title", "Data", "Title", reqd=1, unique=1),
                field("force_majeure", "Text Editor", "Force Majeure"),
                field("terms_and_conditions", "Text Editor", "Terms and Conditions"),
                field("is_default", "Check", "Default"),
            ],
        },
    )

    print(f"DocTypes written under {DT_ROOT}")


def slot_options():
    slots = []
    for h in range(0, 24):
        for m in (0, 30):
            slots.append(f"{h:02d}:{m:02d}")
    return "\\n".join(slots)


if __name__ == "__main__":
    build()
