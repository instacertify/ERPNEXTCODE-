# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

import click
import frappe
from frappe.commands import pass_context


@click.command("seed-instacertify")
@click.option("--force", is_flag=True, default=False)
@pass_context
def seed_instacertify(context, force=False):
	"""Load InstaCertify demo data (quotes, labs, projects)."""
	for site in context.sites:
		frappe.init(site=site)
		frappe.connect()
		from instacertify.setup.seed import seed_demo_data
		from instacertify.setup.workspace import ensure_workspace_and_prints
		from instacertify.setup import ensure_roles, ensure_currencies

		ensure_roles()
		ensure_currencies()
		ensure_workspace_and_prints()
		seed_demo_data(force=force)
		frappe.db.commit()
		click.echo(f"Seeded InstaCertify on {site}")
		frappe.destroy()


commands = [seed_instacertify]
