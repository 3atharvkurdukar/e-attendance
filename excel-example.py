import xlrd

wb = xlrd.open_workbook("sample.xlsx")
sheet = wb.sheet_by_index(0)

for i in range(sheet.nrows):
    for j in range(sheet.ncols):
        print "\t" + str(sheet.cell_value(i, j)),
    print ""
