import flet as ft

fileWidths = [100, 170, 130, 70, 120, 450, 70]
folderWidths = [120, 120, 590, 150, 70]
workerWidths = [130, 110, 70]
vettingWidths = [170, 130, 100, 150, 450, 80, 80, 80, 80]


def to_listview(table: ft.DataTable, widths=fileWidths):
    list_view = ft.ListView(
        expand=False,
        spacing=0,
        width=sum(widths) + 150,
        divider_thickness=10,
    )
    headerRow = ft.Row()
    for i in range(len(table.columns)):
        headerRow.controls.append(
            ft.Container(
                content=ft.Text(
                    str(table.columns[i].label.value),
                    weight=ft.FontWeight.BOLD,
                ),
                width=widths[i],
                padding=ft.Padding(5, 5, 5, 15),
            )
        )
    list_view.controls.append(headerRow)
    for data_row in table.rows:
        rowRow = ft.Row()
        for i in range(len(data_row.cells)):
            rowRow.controls.append(
                ft.Container(
                    content=data_row.cells[i].content,
                    width=widths[i],
                    padding=ft.Padding(5, 5, 5, 5),
                )
            )
        list_view.controls.append(rowRow)
    return list_view


def to_datatable(list_view: ft.ListView):
    data_table = ft.DataTable(
        columns=[],
        rows=[],
    )
    headerRow = list_view.controls[0]
    for i in range(len(headerRow.controls)):
        data_table.columns.append(
            ft.DataColumn(
                ft.Text(
                    str(headerRow.controls[i].content.value),
                    weight=ft.FontWeight.BOLD,
                )
            )
        )
    for row_control in list_view.controls[1:]:
        data_row = ft.DataRow(
            cells=[
                ft.DataCell(
                    content=cell_control.content,
                )
                for _, cell_control in enumerate(row_control.controls)
            ]
        )
        data_table.rows.append(data_row)
    return data_table
