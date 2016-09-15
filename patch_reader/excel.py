from zipfile import ZipFile
from io import BytesIO

from openpyxl.xml.constants import (
    ARC_CORE,
    ARC_WORKBOOK,
    ARC_STYLE,
    ARC_THEME,
    SHARED_STRINGS,
    EXTERNAL_LINK,
)

from openpyxl.workbook import DocumentProperties
from openpyxl.workbook.names.external import detect_external_links
from openpyxl.workbook.names.named_range import read_named_ranges
from openpyxl.reader.strings import read_string_table
from openpyxl.reader.style import read_style_table
from openpyxl.reader.workbook import (
    read_content_types,
    read_properties_core,
    read_excel_base_date,
    detect_worksheets,
    read_rels,
    read_workbook_code_name,
)
from openpyxl.reader.worksheet import read_worksheet
from openpyxl.reader.comments import read_comments, get_comments_file

from patch_reader.drawings import read_drawings, get_drawings_file


def _load_workbook(wb, archive, filename, read_only, keep_vba):
    valid_files = archive.namelist()

    # If are going to preserve the vba then attach a copy of the archive to the
    # workbook so that is available for the save.
    if keep_vba:
        try:
            f = open(filename, 'rb')
            s = f.read()
            f.close()
        except:
            pos = filename.tell()
            filename.seek(0)
            s = filename.read()
            filename.seek(pos)
        wb.vba_archive = ZipFile(BytesIO(s), 'r')

    if read_only:
        wb._archive = ZipFile(filename)

    # get workbook-level information
    try:
        wb.properties = read_properties_core(archive.read(ARC_CORE))
    except KeyError:
        wb.properties = DocumentProperties()
    wb._read_workbook_settings(archive.read(ARC_WORKBOOK))

    # what content types do we have?
    cts = dict(read_content_types(archive))
    rels = dict

    strings_path = cts.get(SHARED_STRINGS)
    if strings_path is not None:
        if strings_path.startswith("/"):
            strings_path = strings_path[1:]
        shared_strings = read_string_table(archive.read(strings_path))
    else:
        shared_strings = []

    try:
        wb.loaded_theme = archive.read(ARC_THEME)  # some writers don't output a theme, live with it (fixes #160)
    except KeyError:
        assert wb.loaded_theme == None, "even though the theme information is missing there is a theme object ?"

    style_table, color_index, cond_styles = read_style_table(archive.read(ARC_STYLE))
    wb.shared_styles = style_table
    wb.style_properties = {'dxf_list':cond_styles}
    wb.cond_styles = cond_styles

    wb.properties.excel_base_date = read_excel_base_date(xml_source=archive.read(ARC_WORKBOOK))

    # get worksheets
    wb.worksheets = []  # remove preset worksheet
    for sheet in detect_worksheets(archive):
        sheet_name = sheet['title']
        worksheet_path = sheet['path']
        if not worksheet_path in valid_files:
            continue

        if not read_only:
            new_ws = read_worksheet(archive.read(worksheet_path), wb,
                                    sheet_name, shared_strings, style_table,
                                    color_index=color_index,
                                    keep_vba=keep_vba)
        else:
            new_ws = read_worksheet(None, wb, sheet_name, shared_strings,
                                    style_table,
                                    color_index=color_index,
                                    worksheet_path=worksheet_path)

        new_ws.sheet_state = sheet.get('state') or 'visible'
        wb._add_sheet(new_ws)

        if not read_only:
        # load comments into the worksheet cells
            comments_file = get_comments_file(worksheet_path, archive, valid_files)
            if comments_file is not None:
                read_comments(new_ws, archive.read(comments_file))

            drawings_file = get_drawings_file(worksheet_path, archive, valid_files)
            if drawings_file is not None:
                read_drawings(new_ws, drawings_file, archive, valid_files)

    wb._named_ranges = list(read_named_ranges(archive.read(ARC_WORKBOOK), wb))

    wb.code_name = read_workbook_code_name(archive.read(ARC_WORKBOOK))

    if EXTERNAL_LINK in cts:
        rels = read_rels(archive)
        wb._external_links = list(detect_external_links(rels, archive))
