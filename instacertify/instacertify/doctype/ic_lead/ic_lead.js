// Copyright (c) 2026, InstaCertify
frappe.ui.form.on('IC Lead', {
	refresh(frm) {
		instacertify.apply_form_polish(frm);
	}
});
