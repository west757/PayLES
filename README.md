<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- total tsp deduction per year and contribution limits, max tsp percentage
- get combat zone from les
- start without uploading les
- add charity to custom row
- deduct tsp before calculating taxes
- tsp rate maxes change depending on other rows

mid-term:
- instructions page and overlay on example les
- add drill pay
- update readme
- check what all is saved if in combat zone (are state taxes paid?)
- add more modals
- add comments to code
- alphabetize resources and add stars for top ones
- cell button tooltips on hover (tsp rate rows disabled, mha full name, etc)
- different browser checks
- add accounts (tsp, bank debt)
- add pro-rated calculations for cells
- interest feature for accounts
- import/export for custom rows
- custom scroll bars

long-term:
- create leave calculator
- minimize/maximize month columns
- set initial value for template rows
- account for specific pays
- rework resources, maybe include tags and search
- pdf export option
- joint spouse with two LES's
- simplify capturing sgli rate and remarks
- create unit tests
- check mobile use
- minify style.css and script.js when pushed into a production environment
- normalize css: https://necolas.github.io/normalize.css/
- use python cProfile or line_profiler to find bottlenecks
- instructions for self-host
- definitions/terms/abbreviations table



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
