import flet as ft
from simpledt import SQLDataTable
from dt_updates import create_worker_dropdown, add_edit_column
from db_updates import update_comments


def create_vetting_tab(page: ft.Page, update_files_and_folders):
    vettingQuery = """
                    SELECT Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments
                    FROM Files
                    LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                    """
    worker_dropdown_vetting = create_worker_dropdown()
    worker_dropdown_vetting.options.insert(0, ft.dropdown.Option("All"))

    def on_worker_dropdown_change(e):
        worker = worker_dropdown_vetting.value
        if worker != "All":
            vettingSQLWorker = SQLDataTable(
                "sqlite",
                "audio.db",
                statement=vettingQuery + f"WHERE Workers.WorkerName = '{worker}'",
            )
        else:
            vettingSQLWorker = SQLDataTable(
                "sqlite",
                "audio.db",
                statement=vettingQuery,
            )
        vetting_table.controls[0] = add_edit_column(
            vettingSQLWorker.datatable, edit_comments
        )
        page.update()

    worker_dropdown_vetting.on_change = on_worker_dropdown_change

    def edit_comments(file_name):
        def close_dlg(e):
            page.close(edit_comments_dlg)

        new_comments = ft.TextField(label="Comments", max_length=50)

        def execute_edit(e):
            update_comments(file_name, new_comments.value)
            if worker_dropdown_vetting.value != "All":
                vettingSQLWorker = SQLDataTable(
                    "sqlite",
                    "audio.db",
                    statement=vettingQuery
                    + f"WHERE Workers.WorkerName = '{worker_dropdown_vetting.value}'",
                )
            else:
                vettingSQLWorker = SQLDataTable(
                    "sqlite",
                    "audio.db",
                    statement=vettingQuery,
                )
            vetting_table.controls[0] = add_edit_column(
                vettingSQLWorker.datatable, edit_comments
            )
            page.update()
            update_files_and_folders()
            close_dlg(e)

        edit_comments_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editing Comments for {file_name}"),
            content=ft.Column([new_comments], tight=True),
            actions=[
                ft.TextButton("Submit Edit", on_click=execute_edit),
                ft.TextButton("Cancel", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(edit_comments_dlg)

    vettingSQLNULL = SQLDataTable(
        "sqlite", "audio.db", statement=vettingQuery + "WHERE Files.FileName = ''"
    )
    vetting_row = ft.Row(
        controls=[
            ft.Container(ft.Text("Select Worker:"), padding=10),
            ft.Container(worker_dropdown_vetting, padding=10),
        ],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_table = ft.Row(
        [add_edit_column(vettingSQLNULL.datatable, edit_comments)],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_controls = ft.Column(
        [vetting_row, vetting_table],
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
    )
    vetting_output = ft.Column(
        [ft.Text("Some sort of image output will be over here")],
        scroll="auto",
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    vetting_tab = ft.Row(
        controls=[vetting_controls, vetting_output],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )
    return vetting_tab, worker_dropdown_vetting
