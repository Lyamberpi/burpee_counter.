from datetime import date

import xlsxwriter


class XlsCreator:

    def unload_user_data(self, data_list=None):
        workbook = xlsxwriter.Workbook('users_data.xlsx')
        worksheet = workbook.add_worksheet(str(date.today()))
        worksheet.set_column(0, 7, width=20)
        to_center_format = workbook.add_format()
        to_center_format.set_center_across()
        worksheet.write_row(0, 0, ["User_id", "Имя", "Фамилия", "Город", "Пол", "Возраст", "Дата_регестрации"],
                            to_center_format)
        if data_list:
            for row_number, line in enumerate(data_list, start=1):
                line_list = list(line)
                if line_list[4] == 1:
                    line_list[4] = "М"
                elif line_list[4] == 2:
                    line_list[4] = "Ж"
                else:
                    line_list[4] = None
                worksheet.write_row(row_number, 0, line_list)
        workbook.close()
