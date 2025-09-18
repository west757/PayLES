<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- remove old LES's from GitHub
- styling of budget scroll bars
- tsp calculator for reaching certain tsp amount and providing rates
- add agency matching to ytd tsp
- incorporate oconus zip code tracking
- add pro-rated calculations for cells
- drill pay calculation (divide monthly total by 30)
- remove charity
- add charity to custom row
- conditionally render drills row
- tsp account add tsp matching

mid-term:
- get combat zone from les
- instructions modal
- rework resources 
-   tags for category (general, financial, moving, education, mental health), branch, featured
-   alphabetize, stars for featured ones
-   search bar

long-term:
- create leave calculator
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
