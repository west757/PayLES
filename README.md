<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main

todo:
create levdf (leave calculator)
instructions page
update pay active and drill pay in config
add more resources
add drill pay
account for specific pays
add security, no sql injection, other security attributes
update readme


possible:
create unit tests
implement CSRF using Flask-WTF, restructure forms first


end of project:
minify style.css and script.js when pushed into a production environment
normalize css: https://necolas.github.io/normalize.css/
use python cProfile or line_profiler to find bottlenecks
check mobile use
instructions for self-host





1. Template Security

Flask/Jinja2 templates auto-escape variables by default, preventing cross-site scripting (XSS).
Never use |safe or Markup() on user input unless you are certain it’s safe.
Always pass user input through Flask’s template rendering (e.g., render_template) and avoid manually building HTML with user data.
Why it matters:
Prevents attackers from injecting malicious scripts into your pages.

2. Rate Limiting

Restricts how often a user/IP can make requests to your app in a given time period.
Prevents abuse, brute-force attacks, and denial-of-service (DoS).
In Flask, you can use the Flask-Limiter extension to easily add rate limits to routes (e.g., “10 requests per minute per IP”).
Why it matters:
Protects your app from being overwhelmed or exploited by repeated requests.

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
