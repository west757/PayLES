<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main

todo:
instructions for self-host
create levdf (leave calculator)
create tspdf (tsp calculator)

add more resources
add more faq
add drill pay
add security, no sql injection, other security attributes
validation checks
verify adjusted screen sizes
check mobile use
add in error alerts for different things
add more html5 validation attributes like required, type="email", etc
autofocus the first input on forms
highlight the current page in the navigation
add error handling for all file operations and user inputs
log errors to a file or monitoring service
check for edge cases
ask about type hints
add unit tests for core logic, or flask's test client for route testing
update readme

Static Assets:
Minify and bundle CSS/JS for production.
Use browser caching for static files.
Optimize images (resize, compress).

Database/Computation:
Cache expensive computations if possible (e.g., with Flask-Caching).
Avoid unnecessary recomputation of dataframes or images.

Sessions:
Set SESSION_COOKIE_SECURE = True and SESSION_COOKIE_SAMESITE = 'Lax' or 'Strict' in production.
Use CSRF protection for all forms (Flask-WTF or similar).

File Uploads:
Restrict file types and size.
Store uploaded files outside the web root if saving to disk.

-->
