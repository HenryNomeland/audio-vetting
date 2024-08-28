import flet as ft
from db_updates import make_conn, commit_conn
import threading
from db_initialization import init_db
from simpledt import SQLDataTable
from db_updates import *
from dt_updates import *


def main(page: ft.Page):
    page.add(
        ft.Container(
            ft.Text("Syncing network drives to Sqlite database...", size=20),
            alignment=ft.alignment.center,
            width=page.width,
            height=page.height,
        )
    )
    page.update()

    def update_sqliteDB():
        init_db()
        page.clean()
        application(page)

    threading.Thread(target=update_sqliteDB).start()


def application(page: ft.Page):
    page.title = "Audio Vetting Application"
    page.window.height = None
    page.window.width = None
    page.window.maximized = True
    fileSQL = SQLDataTable(
        "sqlite",
        "audio.db",
        statement="""
                  SELECT Folders.FolderName, Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments
                  FROM Files
                  LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
                  LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                  """,
    )
    folderSQL = SQLDataTable(
        "sqlite",
        "audio.db",
        statement="""
                  SELECT Folders.FolderName, Folders.TotalFiles, Folders.FolderPath
                  FROM Folders
                  """,
    )
    workerSQL = SQLDataTable(
        "sqlite",
        "audio.db",
        statement="""
                  SELECT Workers.WorkerName, Workers.WorkerType
                  FROM Workers
                  """,
    )

    vetting_dropdown = create_worker_dropdown()
    vetting_row = ft.Row(
        controls=[ft.Text("Select Worker:"), vetting_dropdown],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_tab = ft.Column([vetting_row], tight=True, scroll="auto")
    files_tab = ft.Column([fileSQL.datatable], tight=True, scroll="auto")
    folders_tab = ft.Column([folderSQL.datatable], tight=True, scroll="auto")

    def workerButtonClick(e):
        if (workerTF1.value != "") and (workerTF2.value != ""):
            add_worker(workerTF1.value, workerTF2.value)
            new_workerSQL = SQLDataTable(
                "sqlite",
                "audio.db",
                statement="""
                      SELECT Workers.WorkerName, Workers.WorkerType
                      FROM Workers
                      """,
            )

        workers_table.controls[0] = add_delete_column(
            new_workerSQL.datatable, delete_and_refresh_workers
        )
        page.update()
        vetting_dropdown.options = [
            ft.dropdown.Option(name) for name in generate_dropdown_options()
        ]
        page.update()

        workerTF1.value = ""
        workerTF2.value = ""
        page.update()

    def add_delete_column(data_table, delete_function):
        new_columns = data_table.columns.copy()
        new_rows = data_table.rows.copy()
        new_columns.append(ft.DataColumn(ft.Text("Delete")))
        updated_rows = []
        for row in new_rows:
            delete_button = ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color="red",
                on_click=lambda e, name=row.cells[0].content.value: delete_function(
                    name
                ),
            )
            updated_row = row.cells + [ft.DataCell(delete_button)]
            updated_rows.append(ft.DataRow(cells=updated_row))
        new_data_table = ft.DataTable(columns=new_columns, rows=updated_rows)
        return new_data_table

    def delete_and_refresh_workers(worker_name):
        delete_worker(worker_name)
        new_workerSQL = SQLDataTable(
            "sqlite",
            "audio.db",
            statement="""
                    SELECT Workers.WorkerName, Workers.WorkerType
                    FROM Workers
                    """,
        )
        workers_table.controls[0] = add_delete_column(
            new_workerSQL.datatable, delete_and_refresh_workers
        )
        vetting_dropdown.options = [
            ft.dropdown.Option(name) for name in generate_dropdown_options()
        ]
        page.update()

    workers_table = ft.Column(
        [add_delete_column(workerSQL.datatable, delete_and_refresh_workers)],
        tight=True,
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )
    workerTF1 = ft.TextField(label="New Worker Name")
    workerTF2 = ft.TextField(label="New Worker Type")
    workers_controls = ft.Column(
        [
            workerTF1,
            workerTF2,
            ft.ElevatedButton(text="Add Worker", on_click=workerButtonClick),
        ],
        tight=True,
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )
    workers_tab = ft.Row(
        [workers_table, workers_controls],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )

    tabs = ft.Tabs(
        selected_index=1,
        animation_duration=200,
        tabs=[
            ft.Tab(
                text="Vetting",
                content=ft.Container(
                    content=vetting_tab, alignment=ft.alignment.top_left, padding=20
                ),
            ),
            ft.Tab(
                text="All Files",
                content=ft.Container(
                    content=files_tab, alignment=ft.alignment.top_left, padding=20
                ),
            ),
            ft.Tab(
                text="All Folders",
                content=ft.Container(
                    content=folders_tab, alignment=ft.alignment.center, padding=20
                ),
            ),
            ft.Tab(
                text="All Workers",
                content=ft.Container(
                    content=workers_tab, alignment=ft.alignment.center, padding=20
                ),
            ),
        ],
        expand=1,
    )
    page.add(tabs)
    page.update()


ft.app(target=main)
