# FarmSmart MVP

AI-powered Panchayat-level weather and crop decision support system for farmers and agriculture officers.

## What is included

- Frontend single-page app in `index.html`
- Firebase Phone OTP integration with visible Firebase error codes
- Free demo OTP fallback when Firebase SMS is blocked by billing/internal SMS errors
- Farmer and agriculture officer sign in / sign up flow
- Role-restricted dashboards
- Telugu and English advisory text
- Telugu-compatible browser voice alerts
- Live Open-Meteo weather loading by Panchayat coordinates
- FastAPI backend skeleton under `backend/`
- Official location-data import helper for LGD/Census-derived CSV files

## Run Frontend

```bash
node server.js
```

Then open:

```text
http://localhost:5173/
```

## Free OTP Testing

Firebase real SMS requires billing. For free testing, either add a Firebase test phone number or use the app's fallback OTP shown on screen when Firebase returns `auth/billing-not-enabled` or `auth/internal-error`.

Firebase test phone numbers:

```text
Firebase Console -> Authentication -> Sign-in method -> Phone -> Phone numbers for testing
```

Example:

```text
Phone: +919876543210
OTP: 123456
```

Then enter `9876543210` in the app if the number maps to `+919876543210`.

## Firebase Console Settings

Enable these:

- Authentication -> Sign-in method -> Phone
- Authentication -> Settings -> Authorized domains -> `localhost`
- SMS region policy should allow India if using Indian numbers
- Blaze billing is required only for real SMS delivery

## Run Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

## Real District / Mandal / Village Data

Do not manually invent full administrative data. Import official LGD or Census-derived data using:

```bash
cd backend
python app/import_locations_csv.py data/official_locations.csv data/locations.json
```

CSV columns:

```text
id,state,district,mandal,name,latitude,longitude,soil_type,major_crops
```

Use `|` between crops in `major_crops`.

## Notes

Firebase web config is safe to keep in frontend files. Never put Firebase admin SDK private keys, service account JSON, SMS provider secrets, or API secrets in frontend code.
