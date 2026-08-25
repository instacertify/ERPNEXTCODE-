# InstaCertify Consulting ERP — ERPNext 16.32.3 only

Custom Frappe app for **InstaCertify** built **only on ERPNext `v16.32.3`**.

No Flask, no Next.js, no HRMS, no other product stack — **ERPNext 16.32.3 + this `instacertify` app**.

Brand colours: `#065175` · `#ec6820`. Primary currency **INR**, multi-currency (USD) supported.

## Stack

| Layer | Version |
|-------|---------|
| Frappe | `version-16` (required by ERPNext 16) |
| ERPNext | **`v16.32.3`** |
| Custom app | `instacertify` (this repo) |

## Modules (custom DocTypes on ERPNext)

CRM / Leads · Customers · Quotations + templates · Lab library · Test / sample QR · Projects · Planner · Assets · Roles (IC Admin / Ops Manager / Sales / Operations) · `/app/ic-home` dashboard · customer quote portal · A4 print with UniQuote QR

## One-click deploy (instacertify.in)

On a Docker host:

```bash
cd deploy
cp .env.example .env   # set passwords
chmod +x one-click.sh
./one-click.sh
```

Installs **ERPNext 16.32.3** + **instacertify** only. Desk: `/app/ic-home`.

```bash
bench --site instacertify.in seed-instacertify
```

## License

MIT © InstaCertify
