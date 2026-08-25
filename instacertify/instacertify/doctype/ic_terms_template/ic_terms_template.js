// Copyright (c) 2026, InstaCertify
frappe.ui.form.on('IC Terms Template', {
	refresh(frm) {
		instacertify.apply_form_polish(frm);
	}
});
