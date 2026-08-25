# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

app_name = "instacertify"
app_title = "InstaCertify"
app_publisher = "InstaCertify"
app_description = "Consulting ERP for certification and testing — CRM, quotations, labs, projects, HRMS overlays"
app_email = "nikhil@instacertify.com"
app_license = "MIT"
app_version = "1.0.0"

# Apps required
required_apps = ["erpnext", "hrms"]

# Includes in <head>
app_include_css = [
	"/assets/instacertify/css/instacertify_theme.css",
]
app_include_js = [
	"/assets/instacertify/js/instacertify.js",
]

web_include_css = [
	"/assets/instacertify/css/instacertify_theme.css",
	"/assets/instacertify/css/portal.css",
]

# Home Pages
# website_user_home_page = "ic-home"

# Generators
website_generators = []

# Jinja
jinja = {
	"methods": [
		"instacertify.utils.qr.qr_data_uri",
		"instacertify.utils.qr.qr_base64_png",
	],
}

# Installation
after_install = "instacertify.setup.after_install"
after_migrate = "instacertify.setup.after_migrate"

# Desk Notifications
# notification_config = "instacertify.notifications.get_notification_config"

# Permissions
permission_query_conditions = {
	"IC Quotation": "instacertify.permissions.quotation_query",
	"IC Lead": "instacertify.permissions.lead_query",
	"IC Project": "instacertify.permissions.project_query",
	"IC Customer Profile": "instacertify.permissions.customer_query",
}

has_permission = {
	"IC Quotation": "instacertify.permissions.quotation_has_permission",
	"IC Lab": "instacertify.permissions.lab_has_permission",
}

# Document Events
doc_events = {
	"IC Quotation": {
		"on_update": "instacertify.instacertify.doctype.ic_quotation.ic_quotation.on_update",
	},
	"IC Test Request": {
		"on_update": "instacertify.instacertify.doctype.ic_test_request.ic_test_request.on_update",
	},
	"IC Asset Register": {
		"before_insert": "instacertify.instacertify.doctype.ic_asset_register.ic_asset_register.before_insert",
	},
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"instacertify.tasks.daily_reminders",
	],
}

# Fixtures
fixtures = [
	{
		"dt": "Role",
		"filters": [["name", "in", [
			"IC Admin",
			"IC Ops Manager",
			"IC Sales Person",
			"IC Operations Manager",
		]]],
	},
]

# Bench commands
commands = ["instacertify.commands.commands"]

# Boot session
boot_session = "instacertify.boot.boot_session"

# Branding — keep soft; theme CSS drives colour
# app_logo_url = "/assets/instacertify/images/instacertify-mark.svg"

default_mail_footer = """
	<span>Powered by InstaCertify Consulting ERP on ERPNext</span>
"""
