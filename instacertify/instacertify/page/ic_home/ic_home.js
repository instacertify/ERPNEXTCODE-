frappe.pages["ic-home"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("InstaCertify"),
		single_column: true,
	});

	$(wrapper).find(".layout-main-section").html(`
		<div class="ic-home-root" style="padding:8px 4px 24px;">
			<div class="ic-greeting" id="ic-greeting">
				<h2>Loading…</h2>
			</div>
			<div style="margin-top:22px;">
				<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
					<h3 style="margin:0;color:#065175;">Ongoing Projects</h3>
					<a href="/app/ic-project" style="color:#ec6820;font-weight:600;">View all</a>
				</div>
				<div class="ic-project-rail" id="ic-projects"></div>
			</div>
			<div style="display:grid;grid-template-columns:1.2fr 1fr;gap:16px;margin-top:8px;">
				<div class="frappe-card" style="padding:16px;border-radius:14px;">
					<h3 style="margin-top:0;color:#065175;">Pending Quotes</h3>
					<div id="ic-pending"></div>
				</div>
				<div class="frappe-card" style="padding:16px;border-radius:14px;">
					<h3 style="margin-top:0;color:#065175;">Today's Planner</h3>
					<div id="ic-planner"></div>
					<div style="margin-top:12px;">
						<button class="btn btn-primary btn-sm" id="ic-new-plan">Add 30-min block</button>
					</div>
				</div>
			</div>
			<div class="frappe-card" style="padding:16px;border-radius:14px;margin-top:16px;">
				<div style="display:flex;justify-content:space-between;align-items:center;">
					<h3 style="margin:0;color:#065175;">Lab Library</h3>
					<div class="ic-pagination" id="ic-lab-pager"></div>
				</div>
				<div class="ic-lab-stack" id="ic-labs" style="margin-top:12px;"></div>
			</div>
			<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;">
				<a class="btn btn-primary ic-cta-pulse" href="/app/ic-quotation/new">Create Quotation</a>
				<a class="btn btn-default" href="/app/ic-lead/new">New Lead</a>
				<a class="btn btn-default" href="/app/ic-customer-profile">Customers</a>
				<a class="btn btn-default" href="/app/ic-test-request">Test Requests</a>
				<a class="btn btn-default" href="/app/ic-asset-register">Assets</a>
				<a class="btn btn-default" href="/app/hr">HR / Salary Slips</a>
			</div>
		</div>
	`);

	let labPage = 1;
	const load = () => {
		frappe.call({
			method: "instacertify.api.dashboard.home_dashboard",
			callback(r) {
				const d = r.message || {};
				$("#ic-greeting").html(`
					<h2>${frappe.utils.escape_html(d.greeting || "")}</h2>
					<div class="sub">${frappe.utils.escape_html(d.date_label || "")} · ${frappe.utils.escape_html(d.time_label || "")}</div>
					<div class="ic-stats">
						<div class="ic-stat"><div class="n">${d.stats?.leads || 0}</div><div class="l">Leads</div></div>
						<div class="ic-stat"><div class="n">${d.stats?.quotes || 0}</div><div class="l">Quotes</div></div>
						<div class="ic-stat"><div class="n">${d.stats?.open_projects || 0}</div><div class="l">Open Projects</div></div>
						<div class="ic-stat"><div class="n">${d.stats?.test_requests || 0}</div><div class="l">Test Requests</div></div>
						<div class="ic-stat"><div class="n">${d.stats?.labs || 0}</div><div class="l">Labs</div></div>
					</div>
				`);

				const projects = d.projects || [];
				$("#ic-projects").html(
					projects
						.map(
							(p) => `
					<a class="ic-project-card color-${frappe.utils.escape_html(p.card_color || "Blue")}" href="/app/ic-project/${encodeURIComponent(p.name)}" style="text-decoration:none;color:inherit;">
						<h4>${frappe.utils.escape_html(p.project_name)}</h4>
						<div class="meta"><span>${frappe.utils.escape_html(p.customer_name || p.customer || "")}</span>
						<span class="ic-pill priority-${frappe.utils.escape_html(p.priority || "")}">${frappe.utils.escape_html(p.priority || "")}</span></div>
						<div class="meta" style="margin-top:8px;"><span>${frappe.utils.escape_html(p.status || "")}</span><span>${Math.round(p.progress_percent || 0)}%</span></div>
					</a>`
						)
						.join("") || "<p>No projects yet.</p>"
				);

				$("#ic-pending").html(
					(d.pending_quotes || [])
						.map(
							(q) => `
					<div style="padding:10px 0;border-bottom:1px solid #e6eef3;">
						<a href="/app/ic-quotation/${encodeURIComponent(q.name)}" style="color:#065175;font-weight:600;">${frappe.utils.escape_html(q.subject)}</a>
						<div style="font-size:12px;color:#5b6b78;">${frappe.utils.escape_html(q.status)} · ${frappe.utils.escape_html(q.currency)} ${frappe.format(q.grand_total || 0, { fieldtype: "Currency" })}</div>
					</div>`
						)
						.join("") || "<p>No pending quotes.</p>"
				);

				$("#ic-planner").html(
					(d.planner || [])
						.map(
							(e) => `
					<div class="ic-planner-slot busy">${frappe.utils.escape_html(e.start_slot)}–${frappe.utils.escape_html(e.end_slot)} · ${frappe.utils.escape_html(e.title)}</div>`
						)
						.join("") || "<p>No blocks scheduled today. Use the planner for 30-minute slots.</p>"
				);
			},
		});
		loadLabs(labPage);
	};

	const loadLabs = (page) => {
		frappe.call({
			method: "instacertify.api.dashboard.labs_paginated",
			args: { page, page_size: 6 },
			callback(r) {
				const d = r.message || {};
				labPage = d.page;
				$("#ic-labs").html(
					(d.labs || [])
						.map(
							(l) => `
					<div class="ic-lab-chip" data-lab="${frappe.utils.escape_html(l.name)}">
						<strong>${frappe.utils.escape_html(l.lab_name)}</strong>
						<span style="font-size:12px;color:#5b6b78;">${frappe.utils.escape_html(l.location || "")}</span>
						<span style="font-size:11px;color:#ec6820;">${frappe.utils.escape_html(l.accreditation || "")}</span>
					</div>`
						)
						.join("") || "<p>No labs registered.</p>"
				);
				const pages = d.pages || 1;
				let pager = `<button data-p="1">First</button>`;
				for (let i = 1; i <= pages; i++) {
					pager += `<button class="${i === labPage ? "active" : ""}" data-p="${i}">${i}</button>`;
				}
				pager += `<button data-p="${pages}">Last</button>`;
				$("#ic-lab-pager").html(pager);
			},
		});
	};

	$(wrapper).on("click", "#ic-lab-pager button", function () {
		loadLabs(cint($(this).data("p")));
	});

	$(wrapper).on("click", ".ic-lab-chip", function () {
		const lab = $(this).data("lab");
		frappe.call({
			method: "instacertify.api.dashboard.lab_detail",
			args: { lab },
			callback(r) {
				const d = r.message;
				let scopes = (d.scopes || [])
					.map((s) => {
						const purchase = d.show_purchase
							? `<div>Purchase: ${s.currency} ${s.purchase_price || 0}</div>`
							: "";
						const dl = s.scope_pdf
							? `<a href="${s.scope_pdf}" target="_blank">Scope PDF</a>`
							: "";
						return `<li style="margin-bottom:8px;"><strong>${frappe.utils.escape_html(s.test_name)}</strong>
						<div>${frappe.utils.escape_html(s.applicable_standard || "")} · ${s.typical_timeline_days || "—"} days</div>
						<div>Selling: ${frappe.utils.escape_html(s.currency || "")} ${s.selling_price || 0}</div>
						${purchase}${dl}</li>`;
					})
					.join("");
				const cert = d.accreditation_certificate
					? `<p><a href="${d.accreditation_certificate}" target="_blank">Download Accreditation Certificate</a></p>`
					: "";
				const scopeSheet = d.lab_scope_pdf
					? `<p><a href="${d.lab_scope_pdf}" target="_blank">Download Lab Scope Sheet</a></p>`
					: "";
				frappe.msgprint({
					title: d.lab_name,
					indicator: "blue",
					message: `<p>${frappe.utils.escape_html(d.location || "")} · ${frappe.utils.escape_html(d.accreditation || "")}</p>
						${scopeSheet}${cert}<ol>${scopes}</ol>
						<p><a href="/app/ic-lab/${encodeURIComponent(d.name)}">Open lab record</a></p>`,
				});
			},
		});
	});

	$(wrapper).on("click", "#ic-new-plan", () => {
		frappe.new_doc("IC Planner Entry");
	});

	if (frappe.user.has_role("IC Admin") || frappe.user.has_role("System Manager")) {
		$(wrapper)
			.find(".ic-home-root")
			.append(
				`<div style="margin-top:12px;"><button class="btn btn-default btn-sm" id="ic-export-quotes">Admin: Download Quotes CSV</button></div>`
			);
		$(wrapper).on("click", "#ic-export-quotes", () => {
			window.open(
				"/api/method/instacertify.api.export.download_doctype_csv?doctype=" +
					encodeURIComponent("IC Quotation"),
				"_blank"
			);
		});
	}

	load();
};
