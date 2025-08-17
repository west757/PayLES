<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main

todo:
implement CSRF using Flask-WTF, restructure forms first
add in rows from paydf_template

set dependents to int input
set non-special row options to decimal input
create levdf (leave calculator)
instructions page and overlay on example les
update pay active and drill pay in config
add more resources
add drill pay
account for specific pays
update readme
refactor javascript
check what all is saved if in combat zone (are state taxes paid?)
total tsp deduction per year and contribution limits, max tsp percentage
add modals
joint spouse with two LES's

possible:
create unit tests


end of project:
minify style.css and script.js when pushed into a production environment
normalize css: https://necolas.github.io/normalize.css/
use python cProfile or line_profiler to find bottlenecks
check mobile use
instructions for self-host



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
