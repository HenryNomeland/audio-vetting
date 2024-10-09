import flet as ft
from simpledt import SQLDataTable
from db_updates import *
import subprocess
import platform


def create_worker_dropdown():
    worker_names = generate_dropdown_options()
    return ft.Dropdown(
        label="Select Worker",
        options=[ft.dropdown.Option(name) for name in worker_names],
    )


def create_visit_dropdown():
    visit_names = generate_visitdropdown_options("All")
    return ft.Dropdown(
        label="Select Visit",
        options=[ft.dropdown.Option(name) for name in visit_names],
    )


def create_foldergroup_dropdown():
    group_names = generate_foldergroupdropdown_options()
    return ft.Dropdown(
        label="Select Visit Group",
        options=[ft.dropdown.Option(name) for name in group_names],
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


def audioedit_function(file_name):
    filepath = get_filepath(file_name)
    os = platform.system()
    # the following is just trying to find the path to audition and if it can't find it it tries to find the path to audacity
    if os == "Windows":
        try:
            subprocess.run(
                [
                    r"C:\Program Files (x86)\Adobe\Adobe Audition 2024\Adobe Audition.exe",
                    filepath,
                ]
            )
        except:
            try:
                subprocess.run(
                    [
                        r"C:\Program Files\Adobe\Adobe Audition 2024\Adobe Audition.exe",
                        filepath,
                    ]
                )
            except:
                try:
                    subprocess.run([r"C:\Program Files\Audacity\Audacity.exe"])
                except:
                    subprocess.run([r"C:\Program Files (x86)\Audacity\Audacity.exe"])


def add_audioedit_column(data_table):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Audio")))
    updated_rows = []
    for row in new_rows:
        audioedit_button = ft.IconButton(
            icon=ft.icons.HEARING_ROUNDED,
            icon_color="pink",
            on_click=lambda e, filename=row.cells[0].content.value: audioedit_function(
                filename
            ),
        )
        updated_row = row.cells + [ft.DataCell(audioedit_button)]
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


def add_pause_column(data_table, pause_function):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    new_columns.append(ft.DataColumn(ft.Text("Stop")))
    updated_rows = []
    for row in new_rows:
        pause_button = ft.IconButton(
            icon=ft.icons.SQUARE,
            icon_color="black",
            icon_size=18,
            on_click=lambda e: pause_function(),
        )
        updated_row = row.cells + [ft.DataCell(pause_button)]
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table


def add_status_dropdown(data_table, status_function):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    updated_rows = []
    for row in new_rows:
        status_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("Incomplete"),
                ft.dropdown.Option("Complete"),
                ft.dropdown.Option("Flagged"),
            ],
            on_change=lambda e, filename=row.cells[0].content.value: status_function(
                e, filename
            ),
            text_style=ft.TextStyle(size=13, color=ft.colors.BLACK),
            content_padding=ft.Padding(6, 0, 2, 5),
            border=ft.InputBorder.NONE,
        )
        status_dropdown.value = get_file_status(row.cells[0].content.value)
        updated_row = row.cells
        if status_dropdown.value == "Incomplete":
            updated_cell = ft.Container(
                content=status_dropdown, padding=ft.Padding(2, 5, 3, 4), width=130
            )
        if status_dropdown.value == "Flagged":
            updated_cell = ft.Container(
                content=status_dropdown,
                padding=ft.Padding(2, 5, 3, 4),
                width=130,
                bgcolor=ft.colors.RED_ACCENT_100,
            )
        if status_dropdown.value == "Complete":
            updated_cell = ft.Container(
                content=status_dropdown,
                padding=ft.Padding(2, 5, 3, 4),
                width=130,
                bgcolor=ft.colors.GREEN_ACCENT_100,
            )
        updated_row[3] = ft.DataCell(updated_cell)
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table


def color_status_col(data_table):
    new_columns = data_table.columns.copy()
    new_rows = data_table.rows.copy()
    updated_rows = []
    for row in new_rows:
        updated_row = row.cells
        row_status = updated_row[4].content.value
        if row_status == "Incomplete":
            updated_cell = ft.Text(
                value=updated_row[4].content.value,
            )
        if row_status == "Flagged":
            updated_cell = ft.Text(
                value=updated_row[4].content.value,
                weight=ft.FontWeight.W_800,
                color=ft.colors.RED_800,
            )
        if row_status == "Complete":
            updated_cell = ft.Text(
                value=updated_row[4].content.value,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.GREEN_800,
            )
        updated_row[4] = ft.DataCell(updated_cell)
        updated_rows.append(ft.DataRow(cells=updated_row))
    new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
    return new_data_table
