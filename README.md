# InstaCertify Consulting ERP (ERPNext 16.32.3)

Custom Frappe app for **InstaCertify** — certification & testing consulting — built **purely on ERPNext v16.32.3** + **Frappe HR (HRMS)**. No parallel SaaS stack.

Brand colours: `#065175` (primary) · `#ec6820` (accent). Primary currency **INR**, with **USD** (and other) multi-currency on every quote/customer.

## What you get

| Area | Capabilities |
|------|----------------|
| **CRM / Leads** | Person, company, service vs testing request, company size, India state dropdown, GST, lead source (Google, Direct Call, IndiaMART, referral, consultant library…), timeline, remarks |
| **Customers** | Firm profile, GST, factory + billing address, multiple POCs, onboarded date, deliverable uploads (PDF/image), credentials/commitments/incidents, past quotes & invoices links |
| **Quotations** | Wizard by type: Service / Testing / Certificate / Renewal / Multiple Product / Other · templates (anyone creates, **Admin deletes**) · consulting + lab revenue vs govt fees · force majeure + T&Cs · UniQuote barcode + **QR bottom-right** · A4 print · share link · customer accept / change remarks · notify sharer + Admin · start project when accepted |
| **Lab library** | Horizontal chips + page 1/2/3 · scope, selling price (purchase price **Admin only**) · accreditation PDF downloads · anyone can register lab / add scope |
| **Testing** | Sample lifecycle (received → lab → in process → report → share link) · sample QR label when received · customer checklist uploads |
| **Projects** | Tile/card dashboard, priority, progress remarks, working hours |
| **Planner** | 24h calendar in **30-minute** blocks; schedule self or teammates |
| **Assets** | Anyone registers; auto **asset code**; custodian + value |
| **HRMS** | Salary slips, holiday calendar, attendance, joining letter (via Frappe HR) — profile actions on colourful home desk |
| **Roles** | **IC Admin** (full + Excel export) · **IC Ops Manager** · **IC Sales Person** (own/assigned quotes & customers) · **IC Operations Manager** (projects, hours, customer records) |

Demo seed loads **6 quotation types**, 4 customers, 5 leads, 3 labs, 8 projects, assets, planner blocks.

## Quick start (one-click on the server)

On a host with Docker Engine **23+** and DNS for `instacertify.in`:

```bash
git clone https://github.com/instacertify/ERPNEXTCODE-.git
cd ERPNEXTCODE-/deploy
cp .env.example .env   # set DB_PASSWORD, ADMIN_PASSWORD
chmod +x one-click.sh
./one-click.sh
```

This builds a **frappe_docker** layered image with:

- Frappe `version-16`
- ERPNext **`v16.32.3`**
- HRMS `version-16`
- this `instacertify` app

Then opens the site (default publish port `8080`). Desk home: **`/app/ic-home`**.

Customer quote portal: `/ic-quote?token=…` · Sample tracking: `/ic-sample?token=…` · Report share: `/ic-report?token=…`.

Re-seed demo data:

```bash
bench --site instacertify.in seed-instacertify
# or with force:
bench --site instacertify.in seed-instacertify --force
```

## App layout

```
instacertify/          # Frappe app
  hooks.py             # theme, permissions, events
  setup/seed.py        # colourful demo dataset
  api/dashboard.py     # greeting + project cards + lab pager
  www/                 # public quote / sample / report pages
  public/css|js        # Zoho-like rounded blue/orange UI
deploy/
  one-click.sh         # production-oriented installer
  apps.json            # ERPNext 16.32.3 + HRMS + this repo
  preview-*.html       # static UI previews
```

## Roles cheat-sheet

1. **IC Admin** — everything, template delete, purchase prices, full Excel-style exports (`export` permission + `export_quotations_excel`).
2. **IC Ops Manager** — view/authorise operations across quotes & projects.
3. **IC Sales Person** — create/edit quotes (from templates), see assigned/own quotes & customers, progress on closed projects.
4. **IC Operations Manager** — project oversight, working hours, customer delivery records.

## Screenshots / previews

Open locally:

- `deploy/preview-dashboard.html`
- `deploy/preview-quotation.html`

## License

MIT © InstaCertify
