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
- restrict search input

mid-term:
- get combat zone from les
- determine if user is active duty or national guard
- guide modals
- add pro-rated calculations for rows grade and zip code
- set initial value for template rows (submarine, dive, jump, etc)
- joint spouse with two LES
- config for icons
- minimize formatting (when shrinking window)

long-term:
- leave calculator
- resolve rounding errors (tsp off by 1 cent, or tolerance in discrepancy calculation)
- update readme
- add comments to code
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
- add loading screen after submitting LES


3. Security Headers
Content-Security-Policy: restricts sources for scripts, styles, etc.
X-Frame-Options: prevents clickjacking by disallowing your site in iframes.
X-Content-Type-Options: nosniff: prevents MIME type sniffing.
Strict-Transport-Security: enforces HTTPS.
You can set these headers in Flask using an after_request handler.




Sort Order
- different colors for tag content
Setting: Sort resources by Name, Category, Branch, or CAC Required.
UI: Dropdown or radio buttons.
Why: Lets users quickly find resources in their preferred order.
2. Display Style
Setting: Toggle between List View and Grid View.
UI: Button or switch.
Why: Some users prefer compact lists, others like visual grids.
3. Show/Hide Details
Setting: Toggle to show/hide resource descriptions or tags.
UI: Checkbox.
Why: Useful for users who want a minimal view or more info.
4. Favorites
Setting: Mark resources as favorites and show only favorites.
UI: Star icon or "Show Favorites Only" checkbox.
Why: Users can quickly access their most-used resources.
5. Export Format
Setting: Choose export format (CSV, Excel, JSON).
UI: Dropdown next to export button.
Why: Flexibility for different user needs.
6. Accessibility Options
Setting: High contrast mode, larger text, etc.
UI: Toggle or dropdown.
Why: Improves usability for all users.
7. Resource Type Filter
Setting: Filter by resource type (e.g., website, document, tool).
UI: Additional filter dropdown.
Why: Helps users narrow down by format.
8. Reset Filters/Settings
Setting: Button to reset all filters and settings to default.
UI: Button.
Why: Quick way to clear selections.
9. Show/Hide CAC Required
Setting: Toggle to show/hide the CAC Required badge.
UI: Checkbox.
Why: For users who don’t care about CAC status.
10. Results Per Page
Setting: Choose how many resources to show per page (10, 20, 50).
UI: Dropdown.
Why: Customizes pagination for user preference.
-->
