/* InstaCertify desk helpers */
frappe.provide("instacertify");

instacertify.colors = {
	primary: "#065175",
	accent: "#ec6820",
	teal: "#0d8a8a",
	slate: "#3d4f5f",
};

instacertify.apply_form_polish = function (frm) {
	if (!frm || !frm.$wrapper) return;
	frm.$wrapper.addClass("ic-rounded-form");
};

instacertify.greeting = function () {
	const hour = moment().hour();
	let hello = "Hello";
	if (hour < 12) hello = "Good morning";
	else if (hour < 17) hello = "Good afternoon";
	else hello = "Good evening";
	const name = frappe.boot.user.first_name || frappe.boot.user.name;
	return `${hello}, ${name}`;
};

instacertify.can_see_purchase_price = function () {
	const roles = frappe.boot.user.roles || [];
	return roles.includes("IC Admin") || roles.includes("System Manager") || roles.includes("Administrator");
};

frappe.ui.form.on("IC Quotation", {
	refresh(frm) {
		instacertify.apply_form_polish(frm);
		frm.set_df_property("status", "read_only", 1);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Print A4 Quote"), () => {
				frappe.set_route("print", "IC Quotation", frm.doc.name);
			}, __("Share"));

			frm.add_custom_button(__("Share with Customer"), () => {
				frappe.call({
					method: "instacertify.instacertify.doctype.ic_quotation.ic_quotation.create_share_link",
					args: { quotation: frm.doc.name },
					freeze: true,
					callback(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.msgprint({
								title: __("Share Link"),
								indicator: "green",
								message: `<p>Link ready:</p><p><a href="${r.message.share_link}" target="_blank">${r.message.share_link}</a></p>
								<p><button class="btn btn-primary btn-sm" onclick="frappe.utils.copy_to_clipboard('${r.message.share_link}')">Copy</button></p>`,
							});
						}
					},
				});
			}, __("Share"));

			frm.add_custom_button(__("Save as Template"), () => {
				frappe.prompt(
					[{ fieldname: "template_name", fieldtype: "Data", label: "Template Name", reqd: 1 }],
					(values) => {
						frappe.call({
							method: "instacertify.instacertify.doctype.ic_quotation.ic_quotation.save_as_template",
							args: { quotation: frm.doc.name, template_name: values.template_name },
							callback(r) {
								frappe.show_alert({ message: __("Template saved: {0}", [r.message]), indicator: "green" });
							},
						});
					},
					__("Create Quotation Template"),
					__("Save")
				);
			}, __("Template"));

			if (frm.doc.status === "Accepted" && !frm.doc.project) {
				frm.add_custom_button(__("Start Project"), () => {
					frappe.prompt(
						[{ fieldname: "project_name", fieldtype: "Data", label: "Project Name", default: frm.doc.subject }],
						(values) => {
							frappe.call({
								method: "instacertify.instacertify.doctype.ic_quotation.ic_quotation.start_project",
								args: { quotation: frm.doc.name, project_name: values.project_name },
								callback(r) {
									frappe.set_route("Form", "IC Project", r.message);
								},
							});
						},
						__("Start Project from Quote"),
						__("Create")
					);
				}).addClass("btn-primary");
			}
		}

		// Quote-type driven section hints
		instacertify.toggle_quote_sections(frm);
	},

	quote_type(frm) {
		instacertify.toggle_quote_sections(frm);
	},

	template(frm) {
		if (!frm.doc.template) return;
		frappe.confirm(
			__("Load items and terms from template? This replaces current line items."),
			() => {
				frappe.call({
					method: "instacertify.instacertify.doctype.ic_quotation.ic_quotation.apply_template",
					args: { quotation: frm.doc.name || "", template: frm.doc.template },
					callback() {
						if (frm.doc.name) frm.reload_doc();
						else {
							frappe.model.with_doc("IC Quotation Template", frm.doc.template, () => {
								const tpl = frappe.get_doc("IC Quotation Template", frm.doc.template);
								frm.set_value("force_majeure", tpl.force_majeure);
								frm.set_value("terms_and_conditions", tpl.terms_and_conditions);
								frm.set_value("currency", tpl.currency);
							});
						}
					},
				});
			}
		);
	},

	customer(frm) {
		if (!frm.doc.customer) return;
		frappe.db.get_value("IC Customer Profile", frm.doc.customer, ["default_currency", "company_name"], (r) => {
			if (r && r.default_currency) frm.set_value("currency", r.default_currency);
		});
	},
});

instacertify.toggle_quote_sections = function (frm) {
	const t = frm.doc.quote_type;
	frm.dashboard.clear_headline();
	const map = {
		Service: "Service quote — consulting + government fees + certification timeline",
		Testing: "Testing quote — samples, lab accreditation, standards, testing charges",
		Certificate: "Certificate-only quote — editable for renewals and certificates",
		Renewal: "Renewal quote — lighter consulting with statutory fees",
		"Multiple Product": "Multi-type / multi-product — add mixed Service + Testing lines",
		Other: "Custom quote — free-form line items",
	};
	if (map[t]) {
		frm.dashboard.set_headline_alert(map[t], "blue");
	}
};

frappe.ui.form.on("IC Quotation Item", {
	consulting_amount(frm, cdt, cdn) {
		instacertify.recalc_line(frm, cdt, cdn);
	},
	testing_charges(frm, cdt, cdn) {
		instacertify.recalc_line(frm, cdt, cdn);
	},
	government_fees(frm, cdt, cdn) {
		instacertify.recalc_line(frm, cdt, cdn);
	},
	other_charges(frm, cdt, cdn) {
		instacertify.recalc_line(frm, cdt, cdn);
	},
	lab(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.lab) return;
		frappe.db.get_doc("IC Lab", row.lab).then((lab) => {
			frappe.model.set_value(cdt, cdn, "accreditation", lab.accreditation);
		});
	},
	service(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.service) return;
		frappe.db.get_doc("IC Service Catalog", row.service).then((svc) => {
			frappe.model.set_value(cdt, cdn, "item_type", svc.category === "Testing" ? "Testing" : svc.category);
			frappe.model.set_value(cdt, cdn, "description", svc.service_name);
			frappe.model.set_value(cdt, cdn, "certification_timeline", svc.typical_timeline);
			const amount =
				frm.doc.currency === "USD" ? svc.default_consulting_usd : svc.default_consulting_inr;
			if (amount) frappe.model.set_value(cdt, cdn, "consulting_amount", amount);
		});
	},
});

instacertify.recalc_line = function (frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const total =
		flt(row.consulting_amount) +
		flt(row.testing_charges) +
		flt(row.government_fees) +
		flt(row.other_charges);
	frappe.model.set_value(cdt, cdn, "line_total", total);
};

frappe.ui.form.on("IC Lab", {
	refresh(frm) {
		instacertify.apply_form_polish(frm);
		if (!instacertify.can_see_purchase_price()) {
			frm.fields_dict.scopes.grid.update_docfield_property("purchase_price", "hidden", 1);
			frm.fields_dict.scopes.grid.update_docfield_property("purchase_price", "in_list_view", 0);
		}
	},
});

frappe.ui.form.on("IC Lab Scope", {
	form_render(frm, cdt, cdn) {
		if (!instacertify.can_see_purchase_price()) {
			frappe.meta.get_docfield("IC Lab Scope", "purchase_price", frm.doc.name).hidden = 1;
		}
	},
});

frappe.ui.form.on("IC Test Request", {
	refresh(frm) {
		instacertify.apply_form_polish(frm);
		if (!frm.is_new()) {
			if (frm.doc.sample_status === "Sample Received" || frm.doc.sample_qr_code) {
				frm.add_custom_button(__("Sample QR / Label"), () => {
					frappe.set_route("print", "IC Test Request", frm.doc.name);
				});
			}
			if (frm.doc.report_file) {
				frm.add_custom_button(__("Share Report Link"), () => {
					frappe.call({
						method: "instacertify.instacertify.doctype.ic_test_request.ic_test_request.share_report",
						args: { test_request: frm.doc.name },
						callback(r) {
							frappe.msgprint(`Report link: <a href="${r.message.report_share_link}" target="_blank">${r.message.report_share_link}</a>`);
							frm.reload_doc();
						},
					});
				});
			}
			frm.add_custom_button(__("Generate Sample QR"), () => {
				frappe.call({
					method: "instacertify.instacertify.doctype.ic_test_request.ic_test_request.generate_sample_qr",
					args: { test_request: frm.doc.name },
					callback() {
						frm.reload_doc();
					},
				});
			});
		}
	},
});

frappe.ui.form.on("IC Customer Profile", {
	refresh(frm) {
		instacertify.apply_form_polish(frm);
		if (frm.doc.name) {
			frm.add_custom_button(__("Open Quotes"), () => {
				frappe.set_route("List", "IC Quotation", { customer: frm.doc.name });
			});
			frm.add_custom_button(__("Open Projects"), () => {
				frappe.set_route("List", "IC Project", { customer: frm.doc.name });
			});
		}
	},
});

frappe.ui.form.on("IC Quotation Template", {
	refresh(frm) {
		if (!frm.is_new() && !(frappe.user.has_role("IC Admin") || frappe.user.has_role("System Manager"))) {
			frm.page.clear_menu();
			// non-admins cannot delete — enforced by permissions; hide delete button
			frm.page.btn_secondary && frm.page.btn_secondary.hide();
		}
	},
});

// Route helpers for new quote wizard feel
$(document).on("form-load", function () {
	$(".ic-rounded-form .form-section").css("border-radius", "14px");
});
