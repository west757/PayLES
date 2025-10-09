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
- tsp input zeroing
- rename settings.html and budget.html
- compare LES with recommendations
- rename initials to manuals
- make year a metadata row
- oconus calculations
- only add required rows when needed
- display either conus or oconus variables, or both
- set dependents limit to 5
- remove editable from pay_template, use trigger instead

mid-term:
- get combat zone from les
- instructions modal
- rework resources 
-   tags for category (general, financial, moving, education, mental health), branch, featured
-   alphabetize, stars for featured ones
-   search bar
- add pro-rated calculations for rows grade and zip code
- add loading screen after submitting LES
- shorten remarks and add in blocks for ytd entitle and ytd deduct
- get component from LES, maybe use TPC or PACIDN
- add calculator lookups for certain things (zip code to mha, etc)

long-term:
- leave calculator
- set initial value for template rows
- update readme
- add comments to code
- add in ranks for each branch tooltip
- add in branch row
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



<!-- tsp table-->
<div id="tsp-container">
    <table id="tsp-table" class="styled-table">
        <thead>
            <tr>
                <th>TSP Calculator</th>
                {% for month in months %}
                <th>{{ month }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody>
            {% for row in tsp %}
                {% set row_meta = headers | selectattr('header', 'equalto', row.header) | list | first %}
                {% set next_row = budget[loop.index] if not loop.last else None %}

                {% set section_break = false %}
                {% if row.header in ['Roth TSP Bonus Rate', 'TSP Contribution Total', 'YTD TSP Contribution Total'] %}
                    {% set section_break = true %}
                {% endif %}

                {% set row_class = "" %}
                {% if row.type == 'r' %}
                    {% set row_class = "row-tsp-rate" %}
                {% endif %}

                <tr class="{{ row_class }}{% if section_break %} section-break {% endif %}">
                    {% if row.type %}
                        <td class="cell row-header-cell">
                            <button
                                class="styled-table-button modal-button tooltip{% if row.modal != 'none' %} clickable{% endif %}"
                                data-modal="{{ row.modal }}"
                                data-tooltip="{{ row_meta.tooltip if row_meta.tooltip != 'none' }}">
                                {{ row.header }}
                            </button>
                        </td>
                    {% else %}
                        <td>
                            {{ row.header }}
                        </td>
                    {% endif %}
                    
                    {% for month in months %}
                        {% if row.editable and not loop.first %}
                            <td class="cell">
                                <button class="styled-table-button cell-button tooltip" data-row="{{ row.header }}" data-month="{{ month }}" data-field="{{ row.field }}" data-value="{{ row[month] }}">
                                    {{ format_cell(row, month) }}
                                </button>
                            </td>
                        {% else %}
                            <td class="tooltip" data-row="{{ row.header }}" data-month="{{ month }}" data-value="{{ row[month] }}">
                                {{ format_cell(row, month) }}
                            </td>
                        {% endif %}
                    {% endfor %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>