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


maybe remove default from paydf_template
maybe change sgli rate to sgli coverage


1. Minimize DataFrame Row-wise Operations
Current Issue: Many functions (e.g., expand_paydf, update_*) iterate row-by-row and column-by-column, which is slow in pandas.
Best Practice: Use vectorized operations and avoid .iterrows() where possible. Prepare data in lists or dictionaries and create/assign DataFrames in bulk.

2. Avoid In-Place DataFrame Growth
Current Issue: Appending rows one at a time (paydf.loc[len(paydf)] = ...) is slow for large DataFrames.
Best Practice: Collect rows in a list of dicts, then create the DataFrame once. For column expansion, prepare all new columns in a dict and assign them at once.

3. Reduce Redundant Computation
Current Issue: Functions like update_variables, update_entitlements, etc., are called for every month and every row, even if values do not change.
Best Practice: Only recompute values that actually change (e.g., when an option or input changes). Use memoization or cache results for static rows.

4. Use Caching for Expensive Operations
Current Issue: Functions like calculate_bah, calculate_federal_taxes, etc., may repeat expensive lookups.
Best Practice: Use Flask-Caching for route-level or function-level caching. For pure functions, use functools.lru_cache or a custom cache.

5. Optimize Data Types
Current Issue: All values are cast to Decimal or object, which is slow and memory-inefficient.
Best Practice: Use native pandas numeric types (float64, int64) where possible. Only use Decimal for final calculations if needed for precision.

6. Profile and Parallelize
Current Issue: No profiling or parallelization.
Best Practice: Use Python's cProfile or line_profiler to find bottlenecks. For independent month calculations, consider parallelizing with concurrent.futures or similar.

7. Reduce DataFrame Copies
Current Issue: Each function returns a new DataFrame, which may cause unnecessary copying.
Best Practice: Modify DataFrames in place where safe, or use .loc/.iloc for assignment.

8. Optimize Flask Session Usage
Current Issue: Serializing large DataFrames to JSON in the session can be slow.
Best Practice: Store only minimal state in the session; keep large objects in server-side cache or temporary storage.

9. Optimize Template Rendering
Current Issue: Large tables rendered in Jinja2 can be slow.
Best Practice: Paginate or lazy-load large tables, or render only visible months/rows.

10. Static File Optimization
Current Issue: Static files may not be minified or cached.
Best Practice: Minify JS/CSS, use cache-busting, and set long cache headers.


Next Steps
Profile your code with cProfile to find the slowest functions.
Refactor DataFrame creation and expansion to use batch operations.
Add caching for expensive or repeated calculations.
Minify and cache static files.
Consider paginating or virtualizing large tables in the UI.
If you want concrete code examples for any of these optimizations, let me know which area you'd like to focus on first!



Pros of Your Current Approach
Separation of Concerns: Building a base DataFrame and then expanding it keeps logic modular.
Template-Driven: Using a template CSV makes it easy to update the structure without code changes.
Session Storage: Storing the base DataFrame in the session allows for easy re-expansion and updates.

Cons / Bottlenecks
Row-by-Row Operations: Iterating and appending rows/columns in Python is slow with pandas. Vectorized operations are much faster.
Multiple DataFrame Copies: Each expansion step may create new DataFrames, increasing memory usage and processing time.
Session Overhead: Storing large DataFrames in session variables can be inefficient, especially if the session backend is not optimized for large objects.

Recommendations for Improvement

1. Vectorize DataFrame Operations
Avoid Python for-loops for adding rows/columns. Instead, use pandas vectorized operations (e.g., assign, concat, merge, or direct column assignment).
If you need to add many rows, build a list of dicts or a 2D array, then create a DataFrame in one go and concatenate.

2. Precompute Expansion
If the expansion logic is deterministic (e.g., for each month, add a set of rows), precompute the full structure as much as possible, then fill in values.
Consider building the full expanded DataFrame in one step, using pd.MultiIndex if you have repeated row types per month.

3. Minimize DataFrame Copies
Chain operations or use in-place modifications where possible to reduce memory overhead.

4. Rethink Session Storage
If the DataFrame is large, consider storing only the minimal state needed to reconstruct it, rather than the full DataFrame.
Alternatively, serialize the DataFrame efficiently (e.g., with to_msgpack or to_parquet) if you must store it.

5. Profile and Benchmark
Use cProfile or pandas' built-in timing tools to identify the slowest parts of your code.
Test with realistic data sizes to ensure improvements are meaningful.

6. Consider Alternative Data Structures
If your data is highly sparse or repetitive, consider using sparse DataFrames or even numpy arrays for the core computation, converting to pandas only for the final output.


-->
