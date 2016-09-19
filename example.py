from patch_reader.betterload import betterload

wb = betterload("leap.xlsx")

ws = wb.get_sheet_by_name("Questions")
#for cell in ws['D']:
#    print cell.value
