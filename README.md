<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- add in rows from budget template into budget from settings
- update pay active and drill pay in config
- account for specific pays
- total tsp deduction per year and contribution limits, max tsp percentage
- recommendations tab (like if not adding to tsp, put in money)
- sticky month header of budget
- cell button tooltips on hover (tsp rate rows disabled, mha full name, etc)
- get combat zone from les
- disable inputs when changing months
- set initial value for template rows
- add in check for max inject rows
- validate export
- tooltips over edit buttons

mid-term:
- instructions page and overlay on example les
- add drill pay
- update readme
- check what all is saved if in combat zone (are state taxes paid?)
- add more modals
- rework drag and drop functionality
- add in charity contributions as a row
- go through other les variables and see if they apply
- YTD rows (tsp, gross, entitlements, deductions)
- add comments
- alphabetize resources and add stars for top ones
- recommendations like paying state income tax, not being fully vested in tsp

long-term:
- create leave calculator
- rework resources, maybe include tags and search
- pdf export option
- joint spouse with two LES's
- create unit tests
- check mobile use
- minify style.css and script.js when pushed into a production environment
- normalize css: https://necolas.github.io/normalize.css/
- use python cProfile or line_profiler to find bottlenecks
- instructions for self-host



3. Security Headers

HTTP headers that instruct browsers to enforce security policies.
Common headers for Flask apps:
Content-Security-Policy: restricts sources for scripts, styles, etc.
X-Frame-Options: prevents clickjacking by disallowing your site in iframes.
X-Content-Type-Options: nosniff: prevents MIME type sniffing.
Strict-Transport-Security: enforces HTTPS.
You can set these headers in Flask using an after_request handler.
Why it matters:
Helps prevent XSS, clickjacking, and other browser-based attacks.


-->
