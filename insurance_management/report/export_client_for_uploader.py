# -*- coding:utf-8 -*-
from odoo import api, models, fields
from datetime import datetime
import os
from xlsxwriter.utility import xl_rowcol_to_cell
import pdb


dirname = os.path.dirname(__file__)


class ClientExportUploaderXlsx(models.AbstractModel):
    _name = 'report.report_client_export_uploader'
    _description = 'Client export for uploader Xlsx Reports'
    _inherit = 'report.report_xlsx.abstract'

    @api.model
    def generate_xlsx_report(self, workbook, data, wizard_data):
        client_branch = wizard_data
        if client_branch.insurance_type_id.ins_type_select == 'is_medical':
            # Basic Info
            date_from = fields.date.today()
            date_to = fields.date.today()

            worksheet = workbook.add_worksheet('Client Lines Sheet')

            worksheet.set_column('A:M', 16)
            worksheet.set_row(1, 30)

            header_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                "font_size": '9',
                'align': 'center',
                'valign': 'vcenter',
                'font_color': '#FFFFFF',
                "bg_color": "#000080",
            })
            header_format_green = workbook.add_format({
                'bold': 1,
                'border': 1,
                "font_size": '9',
                'align': 'center',
                'valign': 'vcenter',
                'font_color': '#FFFFFF',
                "bg_color": "#3cb371"

            })
            data_string_left = workbook.add_format({
                "align": 'left',
                "valign": 'vcenter',
                'font_size': '11',
            })
            data_string_center = workbook.add_format({
                "align": 'center',
                "valign": 'vcenter',
                'font_size': '11',
            })
            data_amount = workbook.add_format({
                "align": 'right',
                "valign": 'vcenter',
                'font_size': '11',
            })
            rows = 0
            worksheet.write(rows, 0, 'Member ID', header_format)
            worksheet.write(rows, 1, 'Dependent ID', header_format)
            worksheet.write(rows, 2, 'Member Name (English)', header_format)
            worksheet.write(rows, 3, 'Member Name (Arabic)', header_format)
            worksheet.write(rows, 4, 'Gregorian Birth Date', header_format)
            worksheet.write(rows, 5, 'Age', header_format)
            worksheet.write(rows, 6, 'Hajrah Birth Date', header_format)
            worksheet.write(rows, 7, 'Member type', header_format)
            worksheet.write(rows, 8, 'Gender', header_format)
            worksheet.write(rows, 9, 'Class no', header_format)
            worksheet.write(rows, 10, 'Risk No.', header_format)
            worksheet.write(rows, 11, 'Nationality', header_format)
            worksheet.write(rows, 12, 'Staff No.', header_format)
            worksheet.write(rows, 13, 'Member Category', header_format)
            worksheet.write(rows, 14, 'Mobile No. (1)', header_format)
            worksheet.write(rows, 15, 'Mobile No. (2)', header_format)
            worksheet.write(rows, 16, 'Dep Code', header_format)
            worksheet.write(rows, 17, 'Sponser ID', header_format)
            worksheet.write(rows, 18, 'Occupation', header_format)
            worksheet.write(rows, 19, 'Relation', header_format)
            worksheet.write(rows, 20, 'ELM Relation', header_format)
            rows += 1
        elif client_branch.insurance_type_id.ins_type_select == 'is_vehicle':
            # Basic Info
            date_from = fields.date.today()
            date_to = fields.date.today()

            worksheet = workbook.add_worksheet('Client Vehicle Info Sheet')

            worksheet.set_column('A:M', 16)
            worksheet.set_row(1, 30)

            header_format = workbook.add_format({
                'bold': 1,
                'border': 1,
                "font_size": '9',
                'align': 'center',
                'valign': 'vcenter',
                'font_color': '#FFFFFF',
                "bg_color": "#000080",
            })
            header_format_green = workbook.add_format({
                'bold': 1,
                'border': 1,
                "font_size": '9',
                'align': 'center',
                'valign': 'vcenter',
                'font_color': '#FFFFFF',
                "bg_color": "#3cb371"

            })
            data_string_left = workbook.add_format({
                "align": 'left',
                "valign": 'vcenter',
                'font_size': '11',
            })
            data_string_center = workbook.add_format({
                "align": 'center',
                "valign": 'vcenter',
                'font_size': '11',
            })
            data_amount = workbook.add_format({
                "align": 'right',
                "valign": 'vcenter',
                'font_size': '11',
            })
            rows = 0
            worksheet.write(rows, 0, 'Vehicle Type ?????? ??????????????', header_format)
            worksheet.write(rows, 1, 'Plate No.?????? ????????????', header_format)
            worksheet.write(rows, 2, 'Model  ?????? ??????????', header_format)
            worksheet.write(rows, 3, 'Chassis?????? ???????????? ', header_format)
            worksheet.write(rows, 4, 'Capacity ?????????? ??????????????????', header_format)
            worksheet.write(rows, 5, 'Driver Insurance ?????????? ????????????', header_format)
            worksheet.write(rows, 6, 'Repair ?????? ??????????????', header_format)
            worksheet.write(rows, 7, 'Value ???????????? ??????????????', header_format)
            worksheet.write(rows, 8, 'Owner Name ?????? ????????????', header_format)
            worksheet.write(rows, 9, 'Owner ID No. ?????? ???????? ????????????', header_format)
            worksheet.write(rows, 10, 'Custom ID ?????? ?????????????? ????????????????', header_format)
            worksheet.write(rows, 11, 'Sequence No. ?????????? ????????????????', header_format)
            worksheet.write(rows, 12, 'User ID No. ?????? ???????? ????????????????', header_format)
            worksheet.write(rows, 13, 'User Name ?????? ????????????????', header_format)
            worksheet.write(rows, 14, 'Building No.  ?????? ????????????', header_format)
            worksheet.write(rows, 15, 'Additional No. ?????????? ??????????????', header_format)
            worksheet.write(rows, 16, ' Street ?????? ????????????', header_format)
            worksheet.write(rows, 17, ' City ??????????????', header_format)
            worksheet.write(rows, 18, 'Unit No. ?????? ??????????', header_format)
            worksheet.write(rows, 19, 'PO. BOX ?????????? ????????????', header_format)
            worksheet.write(rows, 20, 'Zip Code ?????????? ??????????????', header_format)
            worksheet.write(rows, 21, 'Neighborhead ?????? ????????', header_format)
            worksheet.write(rows, 22, 'Mobile number ?????? ????????????', header_format)
            worksheet.write(rows, 23, 'Expiry Date of Istemara (Hijry) ?????????? ???????????? ??????????????????', header_format)
            worksheet.write(rows, 24, 'Vehicle COLOR ?????? ??????????????', header_format)
            worksheet.write(rows, 25, 'GCC Covering ?????????????? ??????????????????', header_format)
            worksheet.write(rows, 26, 'NATURAL PERIL Cover ?????????? ?????????????? ????????????????', header_format)
            worksheet.write(rows, 27, 'DOB for owner (AD) ?????????? ?????????? ????????????', header_format)
            worksheet.write(rows, 28, 'NATIONALITY ??????????????', header_format)
            rows += 1
