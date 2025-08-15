<!--
PayLES readme

to run:
navigate to: \Documents\Github\Payles
run: python -m app.main

todo:
instructions for self-host
create levdf (leave calculator)

add more resources
add drill pay
add security, no sql injection, other security attributes
check mobile use
add unit tests and edge case tests for core logic, or flask's test client for route testing
update readme

implement CSRF using Flask-WTF, restructure forms first

minify style.css and script.js when pushed into a production environment


Use browser caching for static files.
Cache expensive computations if possible (e.g., with Flask-Caching).
Avoid unnecessary recomputation of dataframes or images.

normalize css: https://necolas.github.io/normalize.css/
re-look into caching at the end of the project
use python cProfile or line_profiler to find bottlenecks




Recommendations for Improvement

1. Vectorize DataFrame Operations
Avoid Python for-loops for adding rows/columns. Instead, use pandas vectorized operations (e.g., assign, concat, merge, or direct column assignment).
If you need to add many rows, build a list of dicts or a 2D array, then create a DataFrame in one go and concatenate.



-->
