import flet as ft
from simpledt import SQLDataTable
from db_updates import *
from sys import platform
import subprocess


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


def add_edit_column(data_table, edit_function):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Edit")))
    updated_rows = []
    for row in new_rows:
        edit_button = ft.IconButton(
            icon=ft.icons.EDIT,
            icon_color="blue",
            on_click=lambda e, filename=row.cells[0].content.value: edit_function(
                filename
            ),
        )
        updated_row = row.cells + [ft.DataCell(edit_button)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table


def audacity_function(file_name):
    filepath = get_filepath(file_name)
    subprocess.run(["audacity", filepath])


def add_audacity_column(data_table):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Audacity")))
    updated_rows = []
    for row in new_rows:
        audacity_button = ft.IconButton(
            icon=ft.icons.HEARING_ROUNDED,
            icon_color="pink",
            on_click=lambda e, filename=row.cells[0].content.value: audacity_function(
                filename
            ),
        )
        updated_row = row.cells + [ft.DataCell(audacity_button)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table


def add_image_column(data_table, image_function):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Plot")))
    updated_rows = []
    for row in new_rows:
        image_button = ft.IconButton(
            icon=ft.icons.IMAGE_OUTLINED,
            icon_color="green",
            on_click=lambda e, filename=row.cells[0].content.value: image_function(
                filename
            ),
        )
        updated_row = row.cells + [ft.DataCell(image_button)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table


def add_play_column(data_table, play_function):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Play")))
    updated_rows = []
    for row in new_rows:
        play_button = ft.IconButton(
            icon=ft.icons.PLAY_ARROW,
            icon_color="black",
            on_click=lambda e, filename=row.cells[0].content.value: play_function(
                filename
            ),
        )
        updated_row = row.cells + [ft.DataCell(play_button)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table
