<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- drill pay calculation (divide monthly total by 30)
- make tsp account for tsp table
- change account to just be bank account
- tsp input restrictions
- rename initials to manuals
- make year a metadata row
- oconus cola and oha calculations
- line to not take up width in cell for section break
- make badge go away after user first clicks on the modal
- show custom rows checkbox
- make cell buttons visible in table
- rewrite insert row
- conus cola

mid-term:
- get combat zone from les
- guide modal
- rework resources 
-   tags for category (general, financial, moving, education, mental health), branch, featured
-   alphabetize, stars for featured ones
-   search bar
- add pro-rated calculations for rows grade and zip code
- add loading screen after submitting LES
- shorten remarks and add in blocks for ytd entitle and ytd deduct
- get component from LES, maybe use TPC or PACIDN
- add official calculators to resources list
- adjustable table size
- adjustable les size
- restrict LES upload to be within past 2 months
- animation for home tab change
- recommendation for mid-month pay

long-term:
- leave calculator
- tdy cost calculator
- set initial value for template rows
- update readme
- add comments to code
- import/export for custom rows
- account for specific pays (submarine, dive, jump, etc)
- update modal content
- pdf export option (borb)
- confirm carrying over debt to/from months on les (amount forward, carry forward)
- joint spouse with two LES's
- see about simplifying recommendations to being inline and using flask g or session variable
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
