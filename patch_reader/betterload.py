from openpyxl.reader.excel import load_workbook
from openpyxl.reader.excel import _validate_archive
from openpyxl.packaging.workbook import WorkbookParser
from openpyxl.packaging.relationship import get_dependents, get_rels_path
from .drawings import read_drawings, get_drawings_file

def betterload(filename, read_only=False, use_iterators=False, keep_vba=False, guess_types=False, data_only=False):
    wb = load_workbook(filename, read_only, use_iterators, keep_vba, guess_types, data_only)
    archive = _validate_archive(filename)
    valid_files = archive.namelist()
    wb_sheet_names = wb.get_sheet_names()
    parser = WorkbookParser(archive)
    parser.parse()
    for sheet, rel in parser.find_sheets():
        sheet_name = sheet.name
        ws = wb.get_sheet_by_name(sheet_name)
        print "***"
        print ws._images
        worksheet_path = rel.target
        if not worksheet_path in valid_files:
            continue
        if not sheet_name in wb_sheet_names:
            continue
        drawings_file = get_drawings_file(worksheet_path, archive, valid_files)
        if drawings_file is not None:
            ws = wb.get_sheet_by_name(sheet_name)
            read_drawings(ws, drawings_file, archive, valid_files)
    return wb;
