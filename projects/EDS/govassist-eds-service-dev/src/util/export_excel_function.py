import copy


def copy_row_styles(sheet, source_row, target_row):
    """Copy styles from source_row to target_row"""
    for col in range(1, sheet.max_column + 1):
        source_cell = sheet.cell(row=source_row, column=col)
        target_cell = sheet.cell(row=target_row, column=col)

        # Copy styles
        if source_cell.has_style:
            target_cell.font = copy.copy(source_cell.font)
            target_cell.border = copy.copy(source_cell.border)
            target_cell.fill = copy.copy(source_cell.fill)
            target_cell.number_format = source_cell.number_format
            target_cell.protection = copy.copy(source_cell.protection)
            target_cell.alignment = copy.copy(source_cell.alignment)
