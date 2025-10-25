<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- drill pay calculation (divide monthly total by 30)
- oconus cola and oha calculations
- conus cola
- info column for each pay
- disallow drills and tsp when not allowed
- rework tsp recommendations
- tsp zeroing

mid-term:
- get combat zone from les
- guide modals
- rework resources 
-   tags for category (general, financial, moving, education, mental health), branch, featured
-   alphabetize, stars for featured ones
-   search bar
- add pro-rated calculations for rows grade and zip code
- add loading screen after submitting LES
- get component from LES, maybe use TPC or PACIDN
- add official calculators to resources list
- recommendation for mid-month pay
- show custom rows checkbox

long-term:
- leave calculator
- set initial value for template rows
- update readme
- add comments to code
- import/export for custom rows
- account for specific pays (submarine, dive, jump, etc)
- update modal content
- pdf export option (borb)
- confirm carrying over debt to/from months on les (amount forward, carry forward)
- joint spouse with two LES's
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
- error checking and validation for les variables
- change main.py from debug when moving to prod


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


