<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- add accounts (tsp, bank, debt, savings, emergency fund)
- update max tsp percentage recommendation
- update other recommendations
- rework how recommendations are calculated
- remove old LES's from GitHub
- styling of budget scroll bars
- tsp calculator for reaching certain tsp amount and providing rates
- keep table in area where change occurs and not update scroll to top of page
- add in recommendation for type of bank

mid-term:
- get combat zone from les
- check what all is saved if in combat zone (are state taxes paid?)
- add drill pay
- update readme
- add comments to code
- alphabetize resources and add stars for top ones
- different browser checks
- instructions modal
- branch of service variable?
- make months in service editable?
- drills variable?

long-term:
- create leave calculator
- add pro-rated calculations for cells
- set initial value for template rows
- import/export for custom rows
- account for specific pays (submarine, dive, jump, etc)
- update modal content
- rework resources, maybe include tags and search
- pdf export option
- add charity to custom row
- joint spouse with two LES's
- simplify capturing sgli rate and remarks
- see about simplifying recommendations to being inline and using flask g or session variable
- create unit tests 
- check mobile use
- minify style.css and script.js when pushed into a production environment
- normalize css: https://necolas.github.io/normalize.css/
- use python cProfile or line_profiler to find bottlenecks
- instructions for self-host
- definitions/terms/abbreviations table
- searchable definitions
- reddit account
- XML export
- JSON export
- charts and reports
- export entire budget (all metadata)
- merch (patch)


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
