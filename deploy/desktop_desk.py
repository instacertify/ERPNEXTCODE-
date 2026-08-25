#!/usr/bin/env python3
"""InstaCertify interactive desk — tryable UI with seeded demo data (desktop)."""
from __future__ import annotations

import json
import secrets
from datetime import date, datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "instacertify-desktop-demo"

USERS = {
	"admin@instacertify.com": {"name": "Nikhil Tiwari", "role": "IC Admin", "password": "admin"},
	"sales@instacertify.com": {"name": "Asha Sales", "role": "IC Sales Person", "password": "sales"},
	"ops@instacertify.com": {"name": "Rohan Ops", "role": "IC Operations Manager", "password": "ops"},
}

FORCE = """Neither party shall be liable for failure or delay from circumstances beyond reasonable control including acts of God, war, pandemic, strikes, or shortages."""
TERMS = """1. Validity 30 days. 2. Consulting + lab charges = InstaCertify revenue. 3. Government fees may be paid on portal/lab. 4. Taxes extra. 5. 50% advance to start."""

DB = {
	"leads": [
		{"id": "LEAD-2026-00001", "person": "Karan Shah", "company": "PixelForge Technologies", "type": "Service Request", "size": "Small", "country": "India", "state": "Gujarat", "phone": "+91 97277 88990", "email": "karan@pixelforge.example", "source": "IndiaMART", "status": "Qualified", "currency": "INR"},
		{"id": "LEAD-2026-00002", "person": "Mia Johansson", "company": "Nordic IoT AB", "type": "Testing Request", "size": "Medium", "country": "Other", "state": "", "phone": "+46 70 123 4567", "email": "mia@nordiciot.example", "source": "Google", "status": "New", "currency": "USD"},
		{"id": "LEAD-2026-00003", "person": "Vikram Iyer", "company": "Helios Appliance Co", "type": "Service Request", "size": "Micro", "country": "India", "state": "Karnataka", "phone": "+91 99000 11224", "email": "vikram@helios.example", "source": "Referral by Existing Customer", "status": "Quotation Sent", "currency": "INR"},
		{"id": "LEAD-2026-00004", "person": "Chen Wei", "company": "Shenzhen Orbital Ltd", "type": "Mixed / Multiple", "size": "Large", "country": "Other", "state": "", "phone": "+86 138 0000 1122", "email": "chen.wei@orbital.example", "source": "Consultant", "status": "Contacted", "currency": "USD"},
		{"id": "LEAD-2026-00005", "person": "Neha Gupta", "company": "UrbanCharge Solutions", "type": "Testing Request", "size": "Medium", "country": "India", "state": "Haryana", "phone": "+91 98100 44556", "email": "neha@urbancharge.example", "source": "Direct Call", "status": "New", "currency": "INR"},
	],
	"customers": [
		{"id": "CUST-001", "name": "Nova Electronics Pvt Ltd", "size": "Medium", "gstin": "27AABCN1234A1Z5", "country": "India", "state": "Maharashtra", "address": "Plot 12, MIDC Andheri, Mumbai", "factory": "Unit 4, Chakan, Pune", "currency": "INR", "contacts": [{"name": "Rahul Deshmukh", "email": "rahul@novaelec.example", "phone": "+91 98765 43210", "role": "QA Head"}]},
		{"id": "CUST-002", "name": "BrightWave Devices Inc", "size": "Large", "gstin": "", "country": "United States", "state": "", "address": "500 Market St, San Francisco", "factory": "Shenzhen OEM Line A", "currency": "USD", "contacts": [{"name": "Emily Carter", "email": "emily@brightwave.example", "phone": "+1 628 555 0144", "role": "Compliance"}]},
		{"id": "CUST-003", "name": "GreenGrid Energy LLP", "size": "Small", "gstin": "07AAGCG9988B1Z2", "country": "India", "state": "Delhi", "address": "Okhla Phase II, New Delhi", "factory": "", "currency": "INR", "contacts": [{"name": "Imran Qureshi", "email": "imran@greengrid.example", "phone": "+91 98111 22334", "role": "Founder"}]},
		{"id": "CUST-004", "name": "Helios Appliance Co", "size": "Micro", "gstin": "29AABCH5566C1Z9", "country": "India", "state": "Karnataka", "address": "Peenya, Bengaluru", "factory": "", "currency": "INR", "contacts": [{"name": "Ananya Rao", "email": "ananya@helios.example", "phone": "+91 99000 11223", "role": "Director"}]},
	],
	"labs": [
		{"id": "LAB-0001", "name": "NABL Apex Test House — Pune", "location": "Pune, India", "accreditation": "NABL ISO/IEC 17025", "scopes": [{"test": "EMC Radiated Emission", "std": "CISPR 32", "days": 10, "sell": 28000, "buy": 18000, "cur": "INR"}, {"test": "Safety — IT Equipment", "std": "IEC 62368-1", "days": 14, "sell": 35000, "buy": 22000, "cur": "INR"}]},
		{"id": "LAB-0002", "name": "GlobalCert Labs — Dubai", "location": "Dubai, UAE", "accreditation": "ILAC MRA", "scopes": [{"test": "RF Conducted Power", "std": "EN 300 328", "days": 12, "sell": 680, "buy": 420, "cur": "USD"}]},
		{"id": "LAB-0003", "name": "Pacific Safety Lab — Singapore", "location": "Singapore", "accreditation": "SAC-SINGLAS", "scopes": [{"test": "Chemical RoHS screening", "std": "IEC 62321", "days": 7, "sell": 520, "buy": 300, "cur": "USD"}]},
	],
	"quotes": [
		{"id": "QT-2026-00001", "type": "Service", "subject": "BIS CRS — Smart Plug Series A", "customer": "CUST-001", "currency": "INR", "status": "Shared", "barcode": "ICQ-A1B2C3D4E5", "timeline": "10 weeks", "token": "demo-bis", "items": [{"type": "Service", "desc": "BIS CRS consulting", "consulting": 85000, "testing": 0, "govt": 42000, "other": 0, "paid_to": "Government Portal"}], "force": FORCE, "terms": TERMS},
		{"id": "QT-2026-00002", "type": "Testing", "subject": "EMC + Safety — Charger PCB", "customer": "CUST-003", "currency": "INR", "status": "Accepted", "barcode": "ICQ-EMC99881", "timeline": "3 weeks", "token": "demo-emc", "items": [{"type": "Testing", "desc": "EMC radiated emission", "consulting": 15000, "testing": 28000, "govt": 0, "other": 0, "paid_to": "Us", "samples": 2, "std": "CISPR 32"}, {"type": "Testing", "desc": "Safety IEC 62368-1", "consulting": 10000, "testing": 35000, "govt": 0, "other": 0, "paid_to": "Us", "samples": 1, "std": "IEC 62368-1"}], "force": FORCE, "terms": TERMS},
		{"id": "QT-2026-00003", "type": "Certificate", "subject": "ISO 9001 Certificate Support", "customer": "CUST-004", "currency": "INR", "status": "Draft", "barcode": "ICQ-ISO9001", "timeline": "12 weeks", "token": "demo-iso", "items": [{"type": "Certificate", "desc": "ISO 9001 documentation", "consulting": 95000, "testing": 0, "govt": 0, "other": 5000, "paid_to": "Us"}], "force": FORCE, "terms": TERMS},
		{"id": "QT-2026-00004", "type": "Renewal", "subject": "BIS License Renewal FY26", "customer": "CUST-004", "currency": "INR", "status": "Shared", "barcode": "ICQ-RENEW26", "timeline": "4 weeks", "token": "demo-renew", "items": [{"type": "Renewal", "desc": "Renewal consulting", "consulting": 35000, "testing": 0, "govt": 18000, "other": 0, "paid_to": "Government Portal"}], "force": FORCE, "terms": TERMS},
		{"id": "QT-2026-00005", "type": "Service", "subject": "FCC ID — Wi-Fi Module X200", "customer": "CUST-002", "currency": "USD", "status": "Draft", "barcode": "ICQ-FCCX200", "timeline": "6 weeks", "token": "demo-fcc", "items": [{"type": "Service", "desc": "FCC consulting", "consulting": 1800, "testing": 680, "govt": 0, "other": 0, "paid_to": "Lab Directly"}], "force": FORCE, "terms": TERMS},
		{"id": "QT-2026-00006", "type": "Multiple Product", "subject": "CE + RoHS Multi-SKU Bundle", "customer": "CUST-002", "currency": "USD", "status": "Changes Requested", "barcode": "ICQ-CEBUNDLE", "timeline": "8 weeks", "token": "demo-ce", "customer_remarks": "Please split RoHS per SKU and confirm Singapore lab slot.", "items": [{"type": "Service", "desc": "CE marking — SKU family", "consulting": 1450, "testing": 0, "govt": 0, "other": 0, "paid_to": "Us"}, {"type": "Testing", "desc": "RoHS screening 3 SKUs", "consulting": 200, "testing": 1560, "govt": 0, "other": 0, "paid_to": "Us", "samples": 3, "std": "IEC 62321"}], "force": FORCE, "terms": TERMS},
	],
	"projects": [
		{"id": "PRJ-001", "name": "Nova — BIS CRS Smart Plug", "customer": "CUST-001", "priority": "High", "status": "In Progress", "progress": 45, "color": "Blue"},
		{"id": "PRJ-002", "name": "GreenGrid — EMC Charger", "customer": "CUST-003", "priority": "Critical", "status": "Waiting on Lab", "progress": 60, "color": "Orange"},
		{"id": "PRJ-003", "name": "Helios — ISO 9001", "customer": "CUST-004", "priority": "Medium", "status": "Pending", "progress": 10, "color": "Teal"},
		{"id": "PRJ-004", "name": "Helios — BIS Renewal", "customer": "CUST-004", "priority": "High", "status": "In Progress", "progress": 30, "color": "Blue"},
		{"id": "PRJ-005", "name": "BrightWave — FCC Module", "customer": "CUST-002", "priority": "High", "status": "In Progress", "progress": 55, "color": "Orange"},
		{"id": "PRJ-006", "name": "BrightWave — CE Multi-SKU", "customer": "CUST-002", "priority": "Medium", "status": "Waiting on Client", "progress": 25, "color": "Slate"},
		{"id": "PRJ-007", "name": "Nova — Label Artwork Revision", "customer": "CUST-001", "priority": "Low", "status": "On Hold", "progress": 5, "color": "Slate"},
		{"id": "PRJ-008", "name": "GreenGrid — Retest Contingency", "customer": "CUST-003", "priority": "Medium", "status": "Pending", "progress": 0, "color": "Teal"},
	],
	"tests": [
		{"id": "TR-001", "title": "Charger PCB EMC — GreenGrid", "customer": "CUST-003", "lab": "LAB-0001", "status": "Dispatched to Lab", "samples": 2, "std": "CISPR 32", "qr": "ICSAMPLE-TR-001-AB12", "token": "sample-green"},
	],
	"assets": [
		{"id": "AST-001", "code": "IC-AST-2026-00001", "name": "Dell Latitude 5540", "value": 78000, "who": "Nikhil Tiwari", "loc": "Mumbai HQ"},
		{"id": "AST-002", "code": "IC-AST-2026-00002", "name": "Sample Storage Cabinet", "value": 24000, "who": "Rohan Ops", "loc": "Pune Ops"},
		{"id": "AST-003", "code": "IC-AST-2026-00003", "name": "Canon Scanner DR-C240", "value": 42000, "who": "Store", "loc": "Delhi Desk"},
	],
	"planner": [
		{"title": "Client call — Nova BIS", "start": "10:00", "end": "10:30", "color": "Blue"},
		{"title": "Lab follow-up — Apex", "start": "15:00", "end": "16:00", "color": "Orange"},
	],
	"templates": [
		{"name": "BIS CRS Standard (INR)", "type": "Service"},
		{"name": "EMC Testing Bundle", "type": "Testing"},
		{"name": "FCC ID Overseas (USD)", "type": "Service"},
	],
}


def cust_name(cid):
	for c in DB["customers"]:
		if c["id"] == cid:
			return c["name"]
	return cid


def quote_totals(q):
	c = t = g = o = 0
	for i in q["items"]:
		c += i.get("consulting", 0)
		t += i.get("testing", 0)
		g += i.get("govt", 0)
		o += i.get("other", 0)
	return {"consulting": c, "testing": t, "govt": g, "other": o, "revenue": c + t, "grand": c + t + g + o}


def login_required(fn):
	@wraps(fn)
	def wrap(*a, **k):
		if not session.get("user"):
			return redirect(url_for("login"))
		return fn(*a, **k)
	return wrap


SHELL = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>InstaCertify ERP Desk</title>
<style>
:root{--p:#065175;--a:#ec6820;--bg:#f3f7fa;--card:#fff;--r:14px}
*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI",system-ui,sans-serif;background:radial-gradient(1200px 500px at 10% -10%,rgba(6,81,117,.10),transparent 60%),radial-gradient(900px 400px at 100% 0%,rgba(236,104,32,.10),transparent 55%),var(--bg);color:#1c2b36}
.top{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;background:#fff;border-bottom:2px solid rgba(6,81,117,.12);position:sticky;top:0;z-index:10}
.brand{font-weight:800;color:var(--p);font-size:18px}.brand span{color:var(--a);font-size:11px;display:block;letter-spacing:1px;text-transform:uppercase}
.nav{display:flex;gap:8px;flex-wrap:wrap}.nav a{text-decoration:none;color:var(--p);padding:8px 14px;border-radius:999px;border:1px solid rgba(6,81,117,.15);font-weight:600;font-size:13px;background:#fff}
.nav a.active,.nav a:hover{background:var(--p);color:#fff}
.wrap{max-width:1180px;margin:0 auto;padding:20px}
.greet{background:linear-gradient(120deg,var(--p),#0a7aad 55%,var(--a));color:#fff;border-radius:18px;padding:22px 26px;box-shadow:0 8px 24px rgba(6,81,117,.12)}
.greet h1{margin:0 0 4px;font-size:24px}.greet .sub{opacity:.92;font-size:13px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-top:14px}
.stat{background:rgba(255,255,255,.16);border-radius:12px;padding:12px}.stat .n{font-size:22px;font-weight:700}.stat .l{font-size:11px;text-transform:uppercase;opacity:.9}
.rail{display:flex;gap:14px;overflow-x:auto;padding:8px 2px 16px}
.card{min-width:240px;background:var(--card);border-radius:var(--r);padding:16px;box-shadow:0 8px 24px rgba(6,81,117,.08);border-top:4px solid var(--p);text-decoration:none;color:inherit}
.card.Orange{border-top-color:var(--a)}.card.Teal{border-top-color:#0d8a8a}.card.Slate{border-top-color:#3d4f5f}
.card h3{margin:0 0 6px;font-size:15px;color:var(--p)}.meta{font-size:12px;color:#5b6b78;display:flex;justify-content:space-between;gap:8px}
.pill{display:inline-flex;padding:2px 10px;border-radius:999px;font-size:11px;font-weight:600;background:rgba(6,81,117,.1);color:var(--p)}
.pill.hot{background:rgba(236,104,32,.15);color:var(--a)}
.panel{background:#fff;border-radius:var(--r);padding:16px;box-shadow:0 8px 24px rgba(6,81,117,.08);margin-top:14px}
.panel h2{margin:0 0 12px;color:var(--p);font-size:18px}
.grid2{display:grid;grid-template-columns:1.2fr 1fr;gap:16px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:10px 8px;border-bottom:1px solid #e6eef3;text-align:left}th{color:var(--p);font-size:12px}
.btn{display:inline-block;border:0;border-radius:999px;padding:10px 16px;font-weight:700;cursor:pointer;text-decoration:none;font-size:13px}
.btn-p{background:linear-gradient(135deg,var(--p),#0a6e9c);color:#fff}.btn-a{background:var(--a);color:#fff}.btn-g{background:#e8eef2;color:var(--p)}
.chips{display:flex;flex-wrap:wrap;gap:10px}.chip{border-radius:12px;padding:12px 16px;background:#fff;border:1px solid rgba(6,81,117,.12);cursor:pointer;min-width:180px}
.chip strong{display:block;color:var(--p)}
.login{max-width:420px;margin:10vh auto;background:#fff;padding:28px;border-radius:18px;box-shadow:0 10px 30px rgba(6,81,117,.12)}
.login input,.login select,textarea{width:100%;padding:10px 12px;border-radius:10px;border:1px solid #c9d7e1;margin:6px 0 12px}
.hint{font-size:12px;color:#5b6b78;background:#f3f7fa;padding:10px;border-radius:10px}
.slot{background:linear-gradient(90deg,rgba(6,81,117,.15),rgba(236,104,32,.18));padding:8px;border-radius:8px;margin:6px 0;font-size:13px;font-weight:600;color:var(--p)}
.badge{font-size:11px;padding:3px 8px;border-radius:999px;background:#e8eef2;color:var(--p);font-weight:700}
.badge.ok{background:#d8f3e2;color:#0b6b3a}.badge.warn{background:#ffe6d4;color:#a84500}
@media(max-width:800px){.grid2{grid-template-columns:1fr}}
</style>
</head>
<body>
{% if user %}
<div class="top">
  <div class="brand">InstaCertify<span>Consulting ERP · ERPNext 16.32.3 app preview</span></div>
  <div class="nav">
    <a href="/" class="{{'active' if tab=='home' else ''}}">Home</a>
    <a href="/crm" class="{{'active' if tab=='crm' else ''}}">CRM</a>
    <a href="/customers" class="{{'active' if tab=='customers' else ''}}">Customers</a>
    <a href="/quotes" class="{{'active' if tab=='quotes' else ''}}">Quotations</a>
    <a href="/projects" class="{{'active' if tab=='projects' else ''}}">Projects</a>
    <a href="/labs" class="{{'active' if tab=='labs' else ''}}">Labs</a>
    <a href="/calendar" class="{{'active' if tab=='calendar' else ''}}">Calendar</a>
    <a href="/profile" class="{{'active' if tab=='profile' else ''}}">My Profile</a>
  </div>
  <div style="font-size:13px">{{ user.name }} · {{ user.role }} · <a href="/logout">Logout</a></div>
</div>
{% endif %}
<div class="wrap">{{ body|safe }}</div>
</body></html>
"""


def page(tab, body, **ctx):
	user = None
	if session.get("user"):
		u = USERS[session["user"]]
		user = {"email": session["user"], "name": u["name"], "role": u["role"]}
	return render_template_string(SHELL, tab=tab, body=body, user=user, **ctx)


@app.get("/login")
def login():
	if session.get("user"):
		return redirect("/")
	body = """
	<div class="login">
	  <div class="brand" style="margin-bottom:12px">InstaCertify<span>Desktop tryout desk</span></div>
	  <form method="post">
	    <label>Email</label>
	    <select name="email">
	      <option value="admin@instacertify.com">admin@instacertify.com (IC Admin)</option>
	      <option value="sales@instacertify.com">sales@instacertify.com (Sales)</option>
	      <option value="ops@instacertify.com">ops@instacertify.com (Operations)</option>
	    </select>
	    <label>Password</label>
	    <input name="password" type="password" value="admin"/>
	    <button class="btn btn-p" style="width:100%">Enter desk</button>
	  </form>
	  <div class="hint" style="margin-top:12px">Passwords: <b>admin</b> / <b>sales</b> / <b>ops</b><br/>This mirrors the ERPNext custom-app desk with seeded demo data so you can click through CRM, quotes, labs, projects, and the customer quote portal.</div>
	</div>
	"""
	return page("login", body)


@app.post("/login")
def login_post():
	email = request.form.get("email")
	password = request.form.get("password")
	u = USERS.get(email)
	if not u or u["password"] != password:
		return redirect("/login")
	session["user"] = email
	return redirect("/")


@app.get("/logout")
def logout():
	session.clear()
	return redirect("/login")


@app.get("/")
@login_required
def home():
	now = datetime.now()
	hour = now.hour
	greet = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")
	u = USERS[session["user"]]
	proj = "".join(
		f'<a class="card {p["color"]}" href="/projects"><h3>{p["name"]}</h3><div class="meta"><span>{cust_name(p["customer"])}</span><span class="pill {"hot" if p["priority"] in ("High","Critical") else ""}">{p["priority"]}</span></div><div class="meta" style="margin-top:8px"><span>{p["status"]}</span><span>{p["progress"]}%</span></div></a>'
		for p in DB["projects"][:8]
	)
	pending = "".join(
		f'<div style="padding:10px 0;border-bottom:1px solid #e6eef3"><a href="/quotes/{q["id"]}" style="color:#065175;font-weight:700">{q["subject"]}</a><div style="font-size:12px;color:#5b6b78">{q["status"]} · {q["currency"]} {quote_totals(q)["grand"]:,}</div></div>'
		for q in DB["quotes"] if q["status"] in ("Draft", "Shared", "Changes Requested")
	)
	plan = "".join(f'<div class="slot">{e["start"]}–{e["end"]} · {e["title"]}</div>' for e in DB["planner"])
	body = f"""
	<div class="greet"><h1>{greet}, {u['name']}</h1>
	<div class="sub">{now.strftime('%A, %d %B %Y')} · {now.strftime('%I:%M %p')}</div>
	<div class="stats">
	  <div class="stat"><div class="n">{len(DB['leads'])}</div><div class="l">Leads</div></div>
	  <div class="stat"><div class="n">{len(DB['quotes'])}</div><div class="l">Quotes</div></div>
	  <div class="stat"><div class="n">{sum(1 for p in DB['projects'] if p['status'] not in ('Completed',))}</div><div class="l">Open Projects</div></div>
	  <div class="stat"><div class="n">{len(DB['tests'])}</div><div class="l">Test Requests</div></div>
	  <div class="stat"><div class="n">{len(DB['labs'])}</div><div class="l">Labs</div></div>
	</div></div>
	<div style="display:flex;justify-content:space-between;align-items:center;margin-top:18px"><h2 style="color:#065175;margin:0">Ongoing Projects</h2><a href="/projects" style="color:#ec6820;font-weight:700">View all</a></div>
	<div class="rail">{proj}</div>
	<div class="grid2">
	  <div class="panel"><h2>Pending Quotes</h2>{pending}<div style="margin-top:12px"><a class="btn btn-p" href="/quotes/new">Create Quotation</a></div></div>
	  <div class="panel"><h2>Today's Planner</h2>{plan}<a class="btn btn-g" href="/calendar" style="margin-top:8px">Open calendar</a></div>
	</div>
	"""
	return page("home", body)


@app.get("/crm")
@login_required
def crm():
	rows = "".join(
		f"<tr><td>{l['id']}</td><td>{l['person']}</td><td>{l['company']}</td><td>{l['type']}</td><td>{l['source']}</td><td><span class='badge'>{l['status']}</span></td><td>{l['currency']}</td></tr>"
		for l in DB["leads"]
	)
	body = f"""<div class="panel"><h2>CRM / Leads</h2>
	<table><thead><tr><th>ID</th><th>Person</th><th>Company</th><th>Request</th><th>Source</th><th>Status</th><th>Cur</th></tr></thead><tbody>{rows}</tbody></table></div>"""
	return page("crm", body)


@app.get("/customers")
@login_required
def customers():
	cards = "".join(
		f"""<a class="card Blue" href="/customers/{c['id']}" style="min-width:280px"><h3>{c['name']}</h3>
		<div class="meta"><span>{c['country']} · {c['size']}</span><span class="pill">{c['currency']}</span></div>
		<div class="meta" style="margin-top:8px"><span>{c['gstin'] or 'No GST'}</span><span>{c['contacts'][0]['name']}</span></div></a>"""
		for c in DB["customers"]
	)
	body = f"""<div class="panel"><h2>Customers</h2><div class="rail">{cards}</div></div>"""
	return page("customers", body)


@app.get("/customers/<cid>")
@login_required
def customer_detail(cid):
	c = next(x for x in DB["customers"] if x["id"] == cid)
	quotes = [q for q in DB["quotes"] if q["customer"] == cid]
	qrows = "".join(f"<tr><td><a href='/quotes/{q['id']}'>{q['id']}</a></td><td>{q['subject']}</td><td>{q['status']}</td><td>{q['currency']} {quote_totals(q)['grand']:,}</td></tr>" for q in quotes)
	cons = "".join(f"<li><b>{p['name']}</b> — {p['role']} · {p['email']} · {p['phone']}</li>" for p in c["contacts"])
	body = f"""<div class="panel"><h2>{c['name']}</h2>
	<p><b>GST:</b> {c['gstin'] or '—'} · <b>Size:</b> {c['size']} · <b>Currency:</b> {c['currency']}</p>
	<p><b>Billing:</b> {c['address']}<br/><b>Factory:</b> {c['factory'] or '—'}</p>
	<h3 style="color:#065175">Points of contact</h3><ul>{cons}</ul>
	<h3 style="color:#065175">Quotes & invoicing</h3>
	<table><thead><tr><th>Quote</th><th>Subject</th><th>Status</th><th>Total</th></tr></thead><tbody>{qrows}</tbody></table>
	<p style="margin-top:12px"><a class="btn btn-g" href="/customers">Back</a></p></div>"""
	return page("customers", body)


@app.get("/quotes")
@login_required
def quotes():
	rows = "".join(
		f"<tr><td><a href='/quotes/{q['id']}'>{q['id']}</a></td><td>{q['type']}</td><td>{q['subject']}</td><td>{cust_name(q['customer'])}</td><td>{q['currency']} {quote_totals(q)['grand']:,}</td><td><span class='badge {'ok' if q['status']=='Accepted' else 'warn' if q['status']=='Changes Requested' else ''}'>{q['status']}</span></td><td><a href='/portal/{q['token']}' target='_blank'>Share</a></td></tr>"
		for q in DB["quotes"]
	)
	body = f"""<div class="panel"><div style="display:flex;justify-content:space-between;align-items:center"><h2>Quotations</h2><a class="btn btn-p" href="/quotes/new">Create Quotation</a></div>
	<table><thead><tr><th>ID</th><th>Type</th><th>Subject</th><th>Customer</th><th>Total</th><th>Status</th><th>Portal</th></tr></thead><tbody>{rows}</tbody></table>
	<p class="hint">Templates available: {', '.join(t['name'] for t in DB['templates'])}</p></div>"""
	return page("quotes", body)


@app.get("/quotes/new")
@login_required
def quote_new():
	cust_opts = "".join(f"<option value='{c['id']}'>{c['name']} ({c['currency']})</option>" for c in DB["customers"])
	tpl_opts = "".join(f"<option>{t['name']}</option>" for t in DB["templates"])
	body = f"""<div class="panel"><h2>Create Quotation</h2>
	<form method="post">
	  <label>Quote for</label>
	  <select name="type"><option>Service</option><option>Testing</option><option>Certificate</option><option>Renewal</option><option>Multiple Product</option><option>Other</option></select>
	  <label>Template (optional)</label><select name="template"><option value="">—</option>{tpl_opts}</select>
	  <label>Customer</label><select name="customer">{cust_opts}</select>
	  <label>Subject</label><input name="subject" required placeholder="e.g. BIS CRS — Product X"/>
	  <label>Currency</label><select name="currency"><option>INR</option><option>USD</option></select>
	  <label>Consulting amount</label><input name="consulting" type="number" value="50000"/>
	  <label>Testing / lab charges</label><input name="testing" type="number" value="0"/>
	  <label>Government fees</label><input name="govt" type="number" value="0"/>
	  <button class="btn btn-p">Save draft quote</button>
	</form></div>"""
	return page("quotes", body)


@app.post("/quotes/new")
@login_required
def quote_new_post():
	cid = request.form["customer"]
	qid = f"QT-2026-{len(DB['quotes'])+1:05d}"
	token = secrets.token_urlsafe(6)
	DB["quotes"].append({
		"id": qid, "type": request.form["type"], "subject": request.form["subject"], "customer": cid,
		"currency": request.form["currency"], "status": "Draft", "barcode": f"ICQ-{secrets.token_hex(4).upper()}",
		"timeline": "TBD", "token": token, "force": FORCE, "terms": TERMS,
		"items": [{"type": request.form["type"], "desc": request.form["subject"], "consulting": float(request.form.get("consulting") or 0), "testing": float(request.form.get("testing") or 0), "govt": float(request.form.get("govt") or 0), "other": 0, "paid_to": "Us"}],
	})
	return redirect(f"/quotes/{qid}")


@app.get("/quotes/<qid>")
@login_required
def quote_detail(qid):
	q = next(x for x in DB["quotes"] if x["id"] == qid)
	t = quote_totals(q)
	items = "".join(
		f"<tr><td>{i['type']}</td><td>{i['desc']}<div style='font-size:11px;color:#5b6b78'>{i.get('std','')} {('· samples '+str(i['samples'])) if i.get('samples') else ''}</div></td><td>{i.get('consulting',0):,}</td><td>{i.get('testing',0):,}</td><td>{i.get('govt',0):,} <div style='font-size:11px'>{i.get('paid_to','')}</div></td><td><b>{i.get('consulting',0)+i.get('testing',0)+i.get('govt',0)+i.get('other',0):,}</b></td></tr>"
		for i in q["items"]
	)
	body = f"""<div class="panel" style="position:relative;padding-bottom:120px">
	<div style="display:flex;justify-content:space-between;border-bottom:3px solid #065175;padding-bottom:10px">
	  <div><div style="color:#ec6820;font-size:11px;letter-spacing:1px;text-transform:uppercase;font-weight:700">InstaCertify Quotation</div>
	  <h2 style="margin:4px 0">{q['subject']}</h2>
	  <div style="font-size:13px;color:#5b6b78">{q['id']} · {cust_name(q['customer'])} · {q['type']}</div></div>
	  <div style="text-align:right;font-size:13px"><span class="badge">{q['status']}</span><div>Barcode {q['barcode']}</div><div>Timeline {q['timeline']}</div></div>
	</div>
	<table><thead><tr><th>Type</th><th>Description</th><th>Consulting</th><th>Testing</th><th>Govt</th><th>Total</th></tr></thead><tbody>{items}</tbody></table>
	<div style="margin-top:12px;text-align:right">Our revenue (consulting+lab): <b>{q['currency']} {t['revenue']:,}</b><br/>Grand total: <b style="color:#065175;font-size:18px">{q['currency']} {t['grand']:,}</b></div>
	<details style="margin-top:12px"><summary><b>Terms & Force Majeure</b></summary><p>{q['terms']}</p><p>{q['force']}</p></details>
	{"<p class='hint'><b>Customer remarks:</b> "+q.get('customer_remarks','')+"</p>" if q.get('customer_remarks') else ""}
	<div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
	  <a class="btn btn-p" href="/portal/{q['token']}" target="_blank">Share with customer</a>
	  <a class="btn btn-g" href="/quotes/{q['id']}/print" target="_blank">Print A4</a>
	  {"<form method='post' action='/quotes/"+q['id']+"/start' style='display:inline'><button class='btn btn-a'>Start Project</button></form>" if q['status']=='Accepted' else ""}
	</div>
	<div style="position:absolute;right:16px;bottom:16px;text-align:center;font-size:10px;color:#5b6b78">
	  <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={q['barcode']}" width="88" height="88" alt="QR"/>
	  <div>UniQuote QR</div>
	</div>
	</div>"""
	return page("quotes", body)


@app.get("/quotes/<qid>/print")
@login_required
def quote_print(qid):
	return redirect(f"/portal/{next(x['token'] for x in DB['quotes'] if x['id']==qid)}?print=1")


@app.post("/quotes/<qid>/start")
@login_required
def quote_start(qid):
	q = next(x for x in DB["quotes"] if x["id"] == qid)
	pid = f"PRJ-{len(DB['projects'])+1:03d}"
	DB["projects"].insert(0, {"id": pid, "name": q["subject"], "customer": q["customer"], "priority": "High", "status": "Pending", "progress": 0, "color": "Blue"})
	q["status"] = "Converted to Project"
	return redirect("/projects")


@app.get("/portal/<token>")
def portal(token):
	q = next((x for x in DB["quotes"] if x["token"] == token), None)
	if not q:
		return "Invalid quote link", 404
	t = quote_totals(q)
	items = "".join(
		f"<tr><td>{i['type']}</td><td>{i['desc']}</td><td>{i.get('consulting',0):,}</td><td>{i.get('testing',0):,}</td><td>{i.get('govt',0):,}</td><td><b>{i.get('consulting',0)+i.get('testing',0)+i.get('govt',0)+i.get('other',0):,}</b></td></tr>"
		for i in q["items"]
	)
	actions = ""
	if q["status"] in ("Draft", "Shared", "Changes Requested"):
		actions = f"""<form method="post" style="display:flex;gap:8px;flex-wrap:wrap;margin-top:16px">
		<button class="btn btn-p" name="action" value="accept">Accept Quote</button>
		<button class="btn btn-a" name="action" value="changes">Request Changes</button>
		</form>
		<form method="post"><input type="hidden" name="action" value="changes"/><textarea name="remarks" placeholder="Describe required changes"></textarea><button class="btn btn-g">Submit remarks</button></form>"""
	body = f"""
	<div class="panel" style="position:relative;padding-bottom:120px">
	  <div style="color:#ec6820;font-weight:700;text-transform:uppercase;font-size:12px">Customer quote portal</div>
	  <h2 style="color:#065175">{q['subject']}</h2>
	  <p>{q['id']} · {cust_name(q['customer'])} · {q['currency']} · <span class="badge">{q['status']}</span></p>
	  <table><thead><tr><th>Type</th><th>Description</th><th>Consulting</th><th>Testing</th><th>Govt</th><th>Total</th></tr></thead><tbody>{items}</tbody></table>
	  <p style="text-align:right;font-size:18px;color:#065175"><b>Grand total: {q['currency']} {t['grand']:,}</b></p>
	  {actions}
	  <div style="position:absolute;right:16px;bottom:16px;text-align:center;font-size:10px;color:#5b6b78">
	    <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={q['barcode']}" width="88" height="88"/>
	    <div>Scan UniQuote</div>
	  </div>
	</div>
	<script>{'window.print()' if request.args.get('print') else ''}</script>
	"""
	# portal without auth chrome
	return render_template_string(SHELL.replace("{% if user %}", "{% if false %}"), tab="", body=body, user=None)


@app.post("/portal/<token>")
def portal_post(token):
	q = next(x for x in DB["quotes"] if x["token"] == token)
	action = request.form.get("action")
	if action == "accept":
		q["status"] = "Accepted"
	elif action == "changes":
		q["status"] = "Changes Requested"
		q["customer_remarks"] = request.form.get("remarks") or "Changes requested"
	return redirect(f"/portal/{token}")


@app.get("/projects")
@login_required
def projects():
	cards = "".join(
		f'<div class="card {p["color"]}"><h3>{p["name"]}</h3><div class="meta"><span>{cust_name(p["customer"])}</span><span class="pill {"hot" if p["priority"] in ("High","Critical") else ""}">{p["priority"]}</span></div><div class="meta" style="margin-top:8px"><span>{p["status"]}</span><span>{p["progress"]}%</span></div></div>'
		for p in DB["projects"]
	)
	body = f"""<div class="panel"><h2>Projects</h2><div class="rail" style="flex-wrap:wrap">{cards}</div>
	<h3 style="color:#065175;margin-top:18px">Test requests</h3>
	<table><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Samples</th><th>QR</th></tr></thead>
	<tbody>{''.join(f"<tr><td>{t['id']}</td><td>{t['title']}</td><td>{t['status']}</td><td>{t['samples']}</td><td>{t['qr']}</td></tr>" for t in DB['tests'])}</tbody></table>
	</div>"""
	return page("projects", body)


@app.get("/labs")
@login_required
def labs():
	u = USERS[session["user"]]
	show_buy = u["role"] == "IC Admin"
	chips = []
	for lab in DB["labs"]:
		scopes = "".join(
			f"<li><b>{s['test']}</b> · {s['std']} · {s['days']}d · sell {s['cur']} {s['sell']:,}"
			+ (f" · buy {s['cur']} {s['buy']:,}" if show_buy else "")
			+ "</li>"
			for s in lab["scopes"]
		)
		chips.append(f"<div class='chip'><strong>{lab['name']}</strong><span style='font-size:12px;color:#5b6b78'>{lab['location']}</span><span style='font-size:11px;color:#ec6820'>{lab['accreditation']}</span><ul style='font-size:12px;padding-left:16px'>{scopes}</ul></div>")
	body = f"""<div class="panel"><h2>Lab Library</h2>
	<p class="hint">Horizontal lab stack · purchase price visible to Admin only (you are <b>{u['role']}</b>)</p>
	<div class="chips">{''.join(chips)}</div>
	<div style="margin-top:12px" class="nav"><a class="active">1</a><a>First</a><a>Last</a></div>
	</div>"""
	return page("labs", body)


@app.get("/calendar")
@login_required
def calendar():
	slots = []
	busy = {(e["start"], e["end"]): e["title"] for e in DB["planner"]}
	for h in range(8, 20):
		for m in (0, 30):
			start = f"{h:02d}:{m:02d}"
			end_h, end_m = (h, 30) if m == 0 else (h + 1, 0)
			end = f"{end_h:02d}:{end_m:02d}"
			title = None
			for (s, e), t in busy.items():
				if s <= start < e:
					title = t
			slots.append(f"<div class='{'slot' if title else ''}' style='min-height:28px;border-bottom:1px dashed #d7e3ea;padding:4px 8px;font-size:12px'><b>{start}</b> {title or ''}</div>")
	body = f"""<div class="panel"><h2>Planner · 30-minute blocks</h2>
	{''.join(f'<div class="slot">{e["start"]}–{e["end"]} · {e["title"]}</div>' for e in DB['planner'])}
	<div style="margin-top:12px;background:#fff;border-radius:12px;overflow:hidden">{''.join(slots)}</div>
	<form method="post" style="margin-top:12px" class="grid2">
	  <div><label>Title</label><input name="title" required/><label>Start</label><input name="start" value="11:00"/><label>End</label><input name="end" value="11:30"/>
	  <button class="btn btn-p">Add block</button></div>
	</form></div>"""
	return page("calendar", body)


@app.post("/calendar")
@login_required
def calendar_post():
	DB["planner"].append({"title": request.form["title"], "start": request.form["start"], "end": request.form["end"], "color": "Blue"})
	return redirect("/calendar")


@app.get("/profile")
@login_required
def profile():
	u = USERS[session["user"]]
	assets = "".join(f"<tr><td>{a['code']}</td><td>{a['name']}</td><td>₹ {a['value']:,}</td><td>{a['who']}</td><td>{a['loc']}</td></tr>" for a in DB["assets"])
	body = f"""<div class="panel"><h2>My Profile · {u['name']}</h2>
	<p>Role: <b>{u['role']}</b> · Email: {session['user']}</p>
	<div class="grid2">
	  <div><h3 style="color:#065175">HR</h3>
	    <ul><li>Salary slips (HRMS) — downloadable after ERPNext site install</li>
	    <li>Holiday calendar</li><li>Attendance</li>
	    <li>Joining letter with QR — print format <b>IC Joining Letter</b></li></ul>
	  </div>
	  <div><h3 style="color:#065175">Assets</h3>
	    <table><thead><tr><th>Code</th><th>Name</th><th>Value</th><th>Custodian</th><th>Loc</th></tr></thead><tbody>{assets}</tbody></table>
	  </div>
	</div>
	{"<p style='margin-top:12px'><a class='btn btn-g' href='/export/quotes.csv'>Admin: Download Quotes CSV</a></p>" if u['role']=='IC Admin' else ''}
	</div>"""
	return page("profile", body)


@app.get("/export/quotes.csv")
@login_required
def export_csv():
	if USERS[session["user"]]["role"] != "IC Admin":
		return "Forbidden", 403
	from flask import Response
	lines = ["id,type,subject,customer,currency,status,grand_total"]
	for q in DB["quotes"]:
		lines.append(f"{q['id']},{q['type']},{q['subject']},{cust_name(q['customer'])},{q['currency']},{q['status']},{quote_totals(q)['grand']}")
	return Response("\n".join(lines), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=quotes.csv"})


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5055, debug=False)
