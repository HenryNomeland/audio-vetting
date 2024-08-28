import flet as ft
from simpledt import SQLDataTable
from db_updates import *


def create_worker_dropdown():
    worker_names = generate_dropdown_options()
    return ft.Dropdown(
        label="Select Worker",
        options=[ft.dropdown.Option(name) for name in worker_names],
    )


def add_check_column(data_table):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Select")))
    updated_rows = []
    for row in new_rows:
        checkbox = ft.Checkbox(value=False, active_color="blue")
        updated_row = row.cells + [ft.DataCell(checkbox)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table


def add_delete_column(data_table, delete_function):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Delete")))
    updated_rows = []
    for row in new_rows:
        delete_button = ft.IconButton(
            icon=ft.icons.DELETE,
            icon_color="red",
            on_click=lambda e, name=row.cells[0].content.value: delete_function(name),
        )
        updated_row = row.cells + [ft.DataCell(delete_button)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table
