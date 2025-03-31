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



<!--
To implement the update_bah function that updates the BAH row in the matrix DataFrame based on the user inputs and various conditions, you can add the following code under the #update bah comment in the updatematrix function of main.py. Here's how the logic could be incorporated:

#update bah
def update_bah():
    # Read the necessary dataframes into the session
    bah_with_dependents = pd.read_csv('/mnt/data/bah_with_dependents_2025.csv')
    bah_without_dependents = pd.read_csv('/mnt/data/bah_without_dependents_2025.csv')
    mha_zipcodes = pd.read_csv('/mnt/data/mha_zipcodes.csv')

    # Lookup MHA based on the current or future zipcode
    if session['zipcode_future'] != 0:
        mha_search = mha_zipcodes[mha_zipcodes['Zipcode'] == session['zipcode_future']]
    else:
        mha_search = mha_zipcodes[mha_zipcodes['Zipcode'] == session['zipcode_current']]

    if not mha_search.empty:
        session['mha_future'] = mha_search.iloc[0]['MHA']
        session['mha_future_name'] = mha_search.iloc[0]['MHA_NAME']
    else:
        session['mha_future'] = session['mha_current']
        session['mha_future_name'] = session['mha_current_name']

    # Choose the appropriate BAH dataframe based on the number of dependents
    if session['dependents_future'] > 0:
        bah_df = bah_with_dependents
    else:
        bah_df = bah_without_dependents

    # Find the BAH value based on MHA and rank
    bah_value = bah_df.loc[bah_df['MHA'] == session['mha_future'], session['rank_future']]

    if not bah_value.empty:
        bah_value = bah_value.iloc[0]
    else:
        bah_value = 0  # Default if no BAH value is found

    # Now, we need to update the BAH row in the matrix.
    bah_row_index = session['row_headers'].index("BAH")

    # Iterate through each month and apply the BAH changes
    for i in range(1, len(session['col_headers'])):
        # If the current month is greater than or equal to the future month of the zipcode or dependents
        if i >= session['col_headers'].index(session['zipcode_future_month']) or \
           i >= session['col_headers'].index(session['dependents_future_month']):
            session['matrix'].at[bah_row_index, session['col_headers'][i]] = bah_value
        else:
            # Otherwise, retain the previous value
            session['matrix'].at[bah_row_index, session['col_headers'][i]] = session['matrix'].at[bah_row_index, session['col_headers'][1]]

    # Optionally, ensure the columns update in the dataframe after modification
    return session['matrix']

# Call the update_bah function to apply the changes
session['matrix'] = update_bah()

Explanation:

    MHA Lookup: The MHA (Military Housing Area) for the current or future zipcode is determined by searching the mha_zipcodes.csv file.

    BAH Dataframe Selection: The BAH dataframe (bah_with_dependents or bah_without_dependents) is selected based on whether the user has dependents.

    BAH Value Extraction: The BAH value for the selected MHA and rank is extracted from the selected BAH dataframe.

    BAH Row Update: The BAH row in the matrix dataframe is updated according to the user's inputs. The update will take effect based on the specified future months for the zipcode and dependents.

    Return Updated Matrix: The function returns the updated matrix with the changes applied to the BAH row.

This function is designed to be added to the updatematrix function. You should call the update_bah() function inside updatematrix() to apply the BAH updates whenever the user submits their changes.

-->