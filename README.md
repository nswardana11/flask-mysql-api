# Flask MySQL API

API sederhana untuk ambil data dari MySQL dan digunakan oleh Google Apps Script.

## Endpoint

- `/report-mutations?key=your-secret-key` → ambil data mutasi transaksi

## Environment Variables

- `DB_HOST`
- `DB_USER`
- `DB_PASS`
- `DB_NAME`
- `API_KEY`

## Deploy ke Render

1. Push repo ke GitHub
2. Buat Web Service baru
3. Isi Environment Variables
4. Start command: `python app.py`
