# 13F Filing Comparator

A clean, production-ready web application for comparing hedge fund 13F filings.

## 🚀 Live Demo

**Try it now:** [https://13f-six.vercel.app/](https://13f-six.vercel.app/)

## Features

- **Enter any CIK** → Automatically fetches latest 2 filings from SEC
- **Instant comparison** → Shows stock-by-stock changes
- **Beautiful UI** → Mobile-responsive, professional design
- **Sortable & Filterable** → Click columns to sort, filter by status
- **Summary stats** → NEW, EXITED, INCREASED, DECREASED counts
- **API endpoint** → JSON API for programmatic access

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the App

```bash
python app.py
```

### 3. Open in Browser

```
http://localhost:5000
```

## Usage

1. **Enter a CIK** (Central Index Key) for any 13F filer
2. Click "Compare Latest Filings"
3. View the comparison results

### Example CIKs

- **RA Capital Management**: `0001346824`
- Find more at [SEC Company Search](https://www.sec.gov/edgar/searchedgar/companysearch)

## Architecture

This project follows **software engineering best practices**:

### MVC Pattern

```
13F_APP/
├── app.py                 # Controller (Flask routes)
├── services/              # Model (Business logic)
│   ├── sec_client.py     # SEC API client
│   ├── xml_parser.py     # XML parsing
│   └── comparator.py     # Comparison logic
├── templates/             # View (HTML)
└── static/css/           # Styling
```

### Best Practices Applied

✅ **Separation of Concerns** - Each module has one responsibility
✅ **Type Hints** - Clear function signatures
✅ **Error Handling** - Graceful failures with user-friendly messages
✅ **Configuration Management** - All settings in `config.py`
✅ **Rate Limiting** - Respects SEC's 10 requests/second limit
✅ **Documentation** - Docstrings and comments
✅ **Clean Code** - PEP 8 compliant, meaningful names

## API Endpoint

### GET `/api/compare/<cik>`

Returns JSON comparison data.

**Example:**
```bash
# Live API
curl https://13f-six.vercel.app/api/compare/0001346824

# Local development
curl http://localhost:5000/api/compare/0001346824
```

**Response:**
```json
{
  "cik": "0001346824",
  "metadata": {
    "current_date": "2025-11-14",
    "prior_date": "2025-08-14",
    ...
  },
  "summary": {
    "total_positions": 100,
    "new_positions": 10,
    ...
  },
  "comparison": [
    {
      "cusip": "...",
      "issuer": "...",
      "status": "INCREASED",
      ...
    }
  ]
}
```

## Configuration

Edit `config.py` to customize:

- **SEC_USER_AGENT** - Your identification for SEC API
- **HOST** / **PORT** - Server settings
- **DEBUG** - Set to False for production

## How It Works

1. **User enters CIK** → Flask receives POST request
2. **SEC Client fetches** → Downloads latest 2 13F InfoTable XML files
3. **XML Parser extracts** → Parses holdings from both files
4. **Comparator calculates** → Computes changes (NEW, EXITED, etc.)
5. **Template renders** → Displays beautiful results table

## Deployment

### ✅ Production (Currently Hosted)

**Live on Vercel:** [https://13f-six.vercel.app/](https://13f-six.vercel.app/)

This app is deployed and running on Vercel with automatic deployments from GitHub.

### Local Development

**Standard Mode (Password Protected):**
```bash
python app.py
# Visit http://localhost:5000
```

**Fast Dev Mode (No Password):**
```bash
DEV=1 python app.py
# Visit http://localhost:5000 (Bypasses login)
```

### Deploy Your Own

**Vercel:**
1. Fork this repo
2. Connect to Vercel
3. Auto-deploys on push

**Heroku:**
```bash
git init
heroku create
git push heroku main
```

**Railway:**
- Connect your GitHub repo
- Auto-deploys on push

## Development

### Project Structure

- `app.py` - Main Flask application (Controller)
- `config.py` - Configuration settings
- `services/` - Business logic layer (Model)
  - `sec_client.py` - SEC EDGAR API client
  - `xml_parser.py` - 13F XML parser
  - `comparator.py` - Filing comparison engine
- `templates/` - HTML templates (View)
- `static/` - CSS, JS, assets

### Adding Features

**Want to add caching?**
Edit `services/sec_client.py` to cache XML responses.

**Want to track more filings?**
Modify `get_fund_filings()` to fetch more than 2 filings.

**Want to add charts?**
Add Chart.js to `templates/results.html`.

## Troubleshooting

### Port already in use
```bash
lsof -ti:5000 | xargs kill -9
```

### SEC returns 403
- Check `SEC_USER_AGENT` in `config.py`
- Must be in format: "CompanyName email@example.com"

### CIK not found
- Verify CIK at [SEC Company Search](https://www.sec.gov/edgar/searchedgar/companysearch)
- Ensure they file 13F-HR reports

## Tech Stack

- **Backend**: Flask 3.0
- **HTTP Client**: Requests 2.31
- **XML Parser**: lxml 4.9
- **Frontend**: HTML5 + Vanilla JavaScript
- **Styling**: Modern CSS (no frameworks)
- **External API**: SEC EDGAR data.sec.gov

## Credits

**Built by Marco Qin** with industry guidance from **Stephen**.

Data sourced from [SEC EDGAR](https://www.sec.gov).

## License

MIT - Use freely for personal or commercial projects.

