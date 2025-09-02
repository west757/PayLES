<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- align checkboxes in settings table
- instructions page and overlay on example les
- refactor html
- refactor css
- refactor javascript
- refactor python
- cell button tooltips on hover for mha full name
- cell button tooltips on hover for tsp rate row disabled
- add accounts (tsp, bank debt)
- interest feature for accounts
- update max tsp percentage recommendation
- definitions/terms/abbreviations table
- searchable definitions
- bug with adding rows makes first row added have minus -$20?

mid-term:
- get combat zone from les
- check what all is saved if in combat zone (are state taxes paid?)
- add drill pay
- update readme
- add comments to code
- alphabetize resources and add stars for top ones
- different browser checks
- custom scroll bars
- ability to make any entitlement/deduction/allotment row a YTD

long-term:
- create leave calculator
- add pro-rated calculations for cells
- minimize/maximize month columns
- set initial value for template rows
- import/export for custom rows
- account for specific pays
- update modal content
- rework resources, maybe include tags and search
- pdf export option
- add charity to custom row
- joint spouse with two LES's
- simplify capturing sgli rate and remarks
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
