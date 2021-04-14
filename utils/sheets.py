import os
import csv
import xlrd
import xlsxwriter
from time import time
from utils.files import data_filename as fn

import config
from utils.files import data_filename


def csvs2xlsx(**kwargs):
    basename = f'combined_csvs.{time()}.xlsx'
    filename = data_filename(basename)
    if os.path.exists(filename):
        os.remove(filename)

    workbook = xlsxwriter.Workbook(filename)

    for sheet, file in kwargs.items():
        worksheet = workbook.add_worksheet(sheet)
        with open(data_filename(file)) as f:
            rows = csv.reader(f, quotechar=config.CSV_QUOTECHAR, delimiter=config.CSV_DELIMITER,
                              quoting=csv.QUOTE_MINIMAL)
            for i, row in enumerate(rows):
                for j, field in enumerate(row):
                    worksheet.write(i, j, field)

    workbook.close()
    return basename


def xlsx2csvs(filename):
    wb = xlrd.open_workbook(filename)
    sheet_names = wb.sheet_names()
    csv_filenames = dict()
    for name in sheet_names:
        csv_basename = f'{name}.{time()}.csv'
        csv_filename = fn(csv_basename)
        csv_filenames[name] = csv_filename
        sh = wb.sheet_by_name(name)
        with open(csv_filename, 'w') as f:
            wr = csv.writer(f, delimiter=config.CSV_DELIMITER, quotechar=config.CSV_QUOTECHAR,
                            quoting=csv.QUOTE_MINIMAL)
            for row_num in range(sh.nrows):
                wr.writerow(sh.row_values(row_num))

    return csv_filenames


def check_xlsx(filename):
    wb = xlrd.open_workbook(filename)
    sheet_names = wb.sheet_names()
    if 'Disciplinas' not in sheet_names:
        return 'Uma das planilhas do arquivo.xlsx deve se chamar "Disciplinas" (sem as aspas).'
    if 'Turmas' not in sheet_names:
        return 'Uma das planilhas do arquivo.xlsx deve se chamar "Turmas" (sem as aspas).'


def check_csv(filename):
    """add some sort of validation. The code here is not working properly. This sniffer package is not working."""
    return
    with open(filename, 'r') as f:
        try:
            dialect = csv.Sniffer().sniff(f.read(4096))
        except csv.Error:
            return 'Not a CSV file.'

    if dialect.delimiter != config.CSV_DELIMITER:
        return f'O delimitador de campos do CSV deve ser o caractere ({config.CSV_DELIMITER}).'
    if dialect.quotechar != config.CSV_QUOTECHAR:
        return f'O caracter usado como aspas no CSV deve ser ({config.CSV_DELIMITER}).'
