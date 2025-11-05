<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main


short-term:
- drill pay calculation (divide monthly total by 30)
- oconus cola and oha calculations
- conus cola
- refactor resources
- tag for resources which require a CAC
- when going to a new resource page, go to top
- number of resources when filtering

mid-term:
- get combat zone from les
- determine if user is active duty or national guard
- guide modals
- add pro-rated calculations for rows grade and zip code
- set initial value for template rows (submarine, dive, jump, etc)
- joint spouse with two LES

long-term:
- leave calculator
- resolve rounding errors (tsp off by 1 cent, or tolerance in discrepancy calculation)
- update readme
- add comments to code
- add loading screen after submitting LES
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

potential:
- rows displayed setting
- show custom rows setting
- import/export for custom rows


3. Security Headers
Content-Security-Policy: restricts sources for scripts, styles, etc.
X-Frame-Options: prevents clickjacking by disallowing your site in iframes.
X-Content-Type-Options: nosniff: prevents MIME type sniffing.
Strict-Transport-Security: enforces HTTPS.
You can set these headers in Flask using an after_request handler.

-->
