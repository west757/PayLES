import os
import xlrd

STATIC_FOLDER = 'C:/Users/blue/Documents/GitHub/PayLES/app/static'
BAH_FILE = "bah_2025.xls"

def bah_from_excel():
 
    bah_2025 = xlrd.open_workbook(os.path.join(STATIC_FOLDER, BAH_FILE))
    dependents_with_sheet = bah_2025.sheet_by_name('With')
    dependents_without_sheet = bah_2025.sheet_by_name('Without')
    bah_with_dependents = [[dependents_with_sheet.cell_value(r, c) for c in range(dependents_with_sheet.ncols)] for r in range(dependents_with_sheet.nrows)]
    bah_without_dependents = [[dependents_without_sheet.cell_value(r, c) for c in range(dependents_without_sheet.ncols)] for r in range(dependents_without_sheet.nrows)]
    
    #print(bah_with_dependents)
    #print(bah_without_dependents)

    return()
 
 
# main function
if __name__ == "__main__":
    
    bah_from_excel()
    