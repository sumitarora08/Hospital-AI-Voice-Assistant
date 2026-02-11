from openpyxl import Workbook

wb = Workbook()
ws = wb.active

ws.append(["Name", "Disease", "Time"])

wb.save("appointments_main.xlsx")

print("Excel Created Successfully")
