<!--
PayLES readme

Steps to run Flask application:
1. Open command prompt
2. Navigate to: c:\Users\blue\Documents\GitHub\PayLES\app
3. Run: venv\Scripts\activate
4. run python main.py
5. Open on browser: http://127.0.0.1:8080/

flask basics: https://realpython.com/python-web-applications/
file upload: https://stackabuse.com/step-by-step-guide-to-file-upload-with-flask/
flask templates: https://www.geeksforgeeks.org/flask-templates/
serving static flask files: https://stackabuse.com/serving-static-files-with-flask/
get/post with flask: https://stackabuse.com/how-to-get-and-parse-http-post-body-in-flask-json-and-form-data/
pdfplumber: https://pypi.org/project/pdfplumber/
dynamic AJAX with flask: https://www.geeksforgeeks.org/dynamic-forms-handling-with-htmx-and-python-flask/
css modal: https://codepen.io/anon/embed/DdeoeW?height=600&theme-id=0&slug-hash=DdeoeW&default-tab=result&animations=run&editable=&name=cp_embed_4#html-box
table: https://stackoverflow.com/questions/4932181/rounded-table-corners-css-only
pull data from excel: https://stackoverflow.com/questions/22542442/extract-excel-columns-into-python-array
flask config file: https://flask.palletsprojects.com/en/stable/config/
flask sessions: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/
searching through dataframes: https://rowannicholls.github.io/python/advanced/data_frames_searching.html
python dataframe add column: https://www.geeksforgeeks.org/dealing-with-rows-and-columns-in-pandas-dataframe/


military les: https://www.dfas.mil/Portals/98/Documents/Military%20Members/Payentitlements/aboutpay/Army_reading_your_LES.pdf?ver=2020-04-22-134400-497
SGLI website: https://www.va.gov/life-insurance/options-eligibility/sgli/
military pay table: https://www.dfas.mil/militarymembers/payentitlements/Pay-Tables/
MHA zipcodes: https://veteran.com/bah-rates-state/
bah table: https://www.travel.dod.mil/Allowances/Basic-Allowance-for-Housing/BAH-Rate-Lookup/


todo:
- display LES at bottom of table as image
- overlay of selectable things on les display
- have first input be a placeholder for inputs, then actual value (if-then)
- css styling
- building out modals
- building out pages
- additional rows to be added
-->


    <div class="table-div" id="matrix-id">
        {% block content %}
        {{session['matrix_html'] | safe}}
        {% endblock %}
    </div>
<!--
old table:
-->
<!--
    <div class="table-div" id="matrix-id">
        <table class="matrix-table">
            <tbody>
                <tr class="matrix-header">
                    <td class="matrix-header"></td>
                    <td class="matrix-header">{{session.months[0]}}</td>
                    <td class="matrix-header">{{session.months[1]}}</td>
                    <td class="matrix-header">{{session.months[2]}}</td>
                    <td class="matrix-header">{{session.months[3]}}</td>
                    <td class="matrix-header">{{session.months[4]}}</td>
                    <td class="matrix-header">{{session.months[5]}}</td>
                    <td class="matrix-header">{{session.months[6]}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-basepay">Base Pay</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.basepay[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-bas">BAS</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bas[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-bah">BAH</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.bah[6])}}</td>
                </tr>

                {% if session.ueainitial[0] != 0 %}
                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-ueainitial">UEA Initial</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ueainitial[6])}}</td>
                </tr>
                {% endif %}

                {% if session.advancedebt[0] != 0 %}
                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-advancedebt">Advance Debt</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.advancedebt[6])}}</td>
                </tr>
                {% endif %}

                {% if session.pcsmember[0] != 0 %}
                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-pcsmember">PCS Member</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmember[6])}}</td>
                </tr>
                {% endif %}


                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-federaltaxes">Federal Taxes</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.federaltaxes[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-ficasocsecurity">FICA - Social Security</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficasocsecurity[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-ficamedicare">FICA - Medicare</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.ficamedicare[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-sgli">SGLI</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.sgli[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-statetaxes">State Taxes</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.statetaxes[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-rothtsp">Roth TSP</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.rothtsp[6])}}</td>
                </tr>


                {% if session.partialpay[0] != 0 %}
                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-partialpay">Partial Pay</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.partialpay[6])}}</td>
                </tr>
                {% endif %}

                {% if session.pcsmembers[0] != 0 %}
                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-pcsmembers">PCS Members</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.pcsmembers[6])}}</td>
                </tr>
                {% endif %}

                {% if session.debt[0] != 0 %}
                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-debt">Debt</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.debt[6])}}</td>
                </tr>
                {% endif %}


                <tr class="matrix">
                    <td class="matrix" colspan="8" style="background-color: #CFD8DC; height: 8px; padding: 0px;"></td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-taxablepay">Taxable Pay</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.taxablepay[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-nontaxablepay">Non-Taxable Pay</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.nontaxablepay[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-totaltaxes">Total Taxes</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.totaltaxes[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-grosspay">Gross Pay</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.grosspay[6])}}</td>
                </tr>

                <tr class="matrix">
                    <td class="matrix">
                        <label class="modalbutton" for="modal-netpay">Net Pay</label>
                    </td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[0])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[1])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[2])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[3])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[4])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[5])}}</td>
                    <td class="matrix">{{'${:,.2f}'.format(session.netpay[6])}}</td>
                </tr>
            </tbody>
        </table>
    </div>
    -->