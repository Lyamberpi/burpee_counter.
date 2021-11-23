from datetime import date

import xlsxwriter


class XlsCreator:

    def unload_user_data(self, data_list=None):
        workbook = xlsxwriter.Workbook('users_data.xlsx')
        worksheet = workbook.add_worksheet(str(date.today()))
        worksheet.set_column(0, 0, width=15)
        worksheet.set_column(1, 3, width=20)
        worksheet.set_column(4, 4, width=5)
        worksheet.set_column(5, 5, width=10)
        worksheet.set_column(6, 7, width=20)
        header_format = workbook.add_format()
        header_format.set_center_across()
        header_format.set_bold()
        header_format.set_border()
        worksheet.freeze_panes(1, 0)
        worksheet.write_row(0, 0, ["User_id", "Имя", "Фамилия", "Город", "Пол", "Возраст", "Дата_регистрации"],
                            header_format)
        if data_list:
            lines_format = workbook.add_format()
            lines_format.set_border()
            lines_format.set_align("left")
            for row_number, line in enumerate(data_list, start=1):
                line_list = list(line)
                worksheet.write_row(row_number, 0, line_list, lines_format)
                center_format = workbook.add_format()
                center_format.set_border()
                center_format.set_center_across()
                if line_list[4]:
                    worksheet.write(row_number, 4, line_list[4], center_format)
                if line_list[5]:
                    worksheet.write(row_number, 5, line_list[5], center_format)
                if line_list[6]:
                    num_format = workbook.add_format()
                    num_format.set_border()
                    num_format.set_center_across()
                    num_format.set_num_format("yyyy-mm-dd")
                    worksheet.write(row_number, 6, line_list[6], num_format)
        workbook.close()
