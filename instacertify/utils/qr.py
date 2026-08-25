# Copyright (c) 2026, InstaCertify and contributors
# License: MIT

from __future__ import annotations

import base64
import io

import frappe


def qr_base64_png(payload: str, scale: int = 4) -> str:
	"""Return base64 PNG for embedding in print formats."""
	try:
		import pyqrcode
	except Exception:
		return ""
	code = pyqrcode.create(str(payload or ""), error="M")
	buffer = io.BytesIO()
	code.png(buffer, scale=scale, module_color=(6, 81, 117), background=(255, 255, 255))
	return base64.b64encode(buffer.getvalue()).decode()


def qr_data_uri(payload: str, scale: int = 4) -> str:
	b64 = qr_base64_png(payload, scale=scale)
	if not b64:
		return ""
	return f"data:image/png;base64,{b64}"


@frappe.whitelist()
def make_qr(payload: str):
	return qr_data_uri(payload)
