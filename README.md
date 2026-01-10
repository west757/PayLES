# PayLES

**PayLES** is a web application designed to help military personnel calculate and manage their Leave and Earnings Statement (LES), including budgeting, allowances, and other financial planning tools.

## Features

- LES calculations for CONUS and OCONUS locations
- Budgeting tools and calculators
- Support for various allowances (COLA, OHA, etc.)
- Pro-rated calculations for grade and zip code
- User-friendly interface with dropdowns and tooltips
- Security headers for improved safety
- **Planned features:** combat zone detection, joint spouse support, reports, graphs, and more

## Getting Started

### Prerequisites

- Python 3.8+
- Flask and required dependencies (see `requirements.txt`)

### Installation

```sh
git clone https://github.com/west757/PayLES.git
cd PayLES
pip install -r requirements.txt
```

### Running the Application

```sh
python -m app.main
```

The application will start a local Flask server.

## Project Structure

```
app/                # Main application code
  main.py           # Entry point
  routes.py         # Flask routes
  forms.py, budgets.py, calculations.py, etc. # Core modules
  static/           # Static files (CSS, JS)
  templates/        # HTML templates
requirements.txt    # Python dependencies
README.md           # Project documentation
```

## Roadmap

See the README for short-term, mid-term, and long-term goals, including new features, improvements, and potential ideas.

## Contributing

Contributions are welcome! Please submit issues or pull requests via GitHub.

## License

This project is licensed under the MIT License.


<!--
to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- oconus cola and oha calculations
- conus cola
- default for OCONUS locations in dropdown
- add pro-rated calculations for rows grade and zip code
- change session_type or remove it in config

mid-term:
- determine if user is in combat zone
- determine if user is active duty or national guard
- joint spouse with two LES
- reports and graphs and pie chart
- resources list filtering for resources
- move branch into component
- hide drills row

long-term:
- leave calculator
- update readme
- add comments to code
- update modal content
- pdf export option (borb)
- confirm carrying over debt to/from months on les (amount forward, carry forward)
- create unit tests 
- check mobile use
- minify style.css and script.js when pushed into a production environment
- normalize css: https://necolas.github.io/normalize.css/
- use python cProfile or line_profiler to find bottlenecks
- instructions for self-host
- reddit account
- merch (patch, coin)
- add in recommendation for type of bank
- uncomment prompt when leaving budget page
- better css for border table scroll bar
- uncomment les age limit check
- change main.py from debug when moving to prod
- save LES to accounts for historical records
- emergency fund goal calculator

potential:
- rows displayed setting
- show custom rows setting
- import/export for custom rows
- add loading screen after submitting LES
- color code rows


3. Security Headers
Content-Security-Policy: restricts sources for scripts, styles, etc.
X-Frame-Options: prevents clickjacking by disallowing your site in iframes.
X-Content-Type-Options: nosniff: prevents MIME type sniffing.
Strict-Transport-Security: enforces HTTPS.
You can set these headers in Flask using an after_request handler.


- different colors for tag content
- sort alphabetically or by filter
- export format (CSV, excel, JSON, bookmark upload)
- reset filters
- results per page
- size of resources
- show/hide tags

- toggle between list view and grid view
- favorites (if accounts)



Stationed Duty Location:

Country:
choose country

US:
enter zip code
if zip code alaska/hawaii, bring up locality dropdown
- displays zip code, tooltip is mha name

Non-US:
choose Locality
- displays locality code, tooltip is country - locality
enter rent
enter roommates

-->
