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
                  SELECT Folders.FolderName, Folders.TotalFiles, Folders.FolderPath, 
                  CASE 
                      WHEN COUNT(DISTINCT Files.WorkerID) = 1 THEN MAX(Workers.WorkerName)
                      ELSE ''
                  END AS WorkerName
                  FROM Folders
                  LEFT JOIN Files ON Folders.FolderID = Files.FolderID
                  LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                  GROUP BY 
                      Folders.FolderName, 
                      Folders.TotalFiles, 
                      Folders.FolderPath
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

    worker_dropdown = create_worker_dropdown()
    vetting_row = ft.Row(
        controls=[ft.Text("Select Worker:"), worker_dropdown],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_tab = ft.Column([vetting_row], tight=True, scroll="auto")

    def fileButtonClick(e):
        if worker_dropdown.value != "":
            filelist = []
            for row in files_table.controls[0].rows:
                if row.cells[6].content.value:
                    filelist.append(row.cells[1].content.value)
            update_file_assignments(worker_dropdown.value, filelist)
            new_fileSQL = SQLDataTable(
                "sqlite",
                "audio.db",
                statement="""
                        SELECT Folders.FolderName, Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments
                        FROM Files
                        LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
                        LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                        """,
            )
            new_folderSQL = SQLDataTable(
                "sqlite",
                "audio.db",
                statement="""
                        SELECT Folders.FolderName, Folders.TotalFiles, Folders.FolderPath, 
                        CASE 
                            WHEN COUNT(DISTINCT Files.WorkerID) = 1 THEN MAX(Workers.WorkerName)
                            ELSE ''
                        END AS WorkerName
                        FROM Folders
                        LEFT JOIN Files ON Folders.FolderID = Files.FolderID
                        LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                        GROUP BY 
                            Folders.FolderName, 
                            Folders.TotalFiles, 
                            Folders.FolderPath
                        """,
            )

            files_table.controls[0] = add_check_column(new_fileSQL.datatable)
            page.update()

            folders_table.controls[0] = add_check_column(new_folderSQL.datatable)
            page.update()

            worker_dropdown.value = ""
            page.update()

    files_table = ft.Column(
        [add_check_column(fileSQL.datatable)], tight=True, scroll="auto"
    )
    files_controls = ft.Column(
        [
            worker_dropdown,
            ft.ElevatedButton(
                text="Assign Selected to Worker", on_click=fileButtonClick
            ),
        ],
        tight=True,
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )
    files_tab = ft.Row(
        [files_table, files_controls],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )

    def folderButtonClick(e):
        if worker_dropdown.value != "":
            folderlist = []
            for row in folders_table.controls[0].rows:
                if row.cells[4].content.value:
                    folderlist.append(row.cells[2].content.value)
            update_folder_assignments(worker_dropdown.value, folderlist)
            new_fileSQL = SQLDataTable(
                "sqlite",
                "audio.db",
                statement="""
                        SELECT Folders.FolderName, Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments
                        FROM Files
                        LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
                        LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                        """,
            )
            new_folderSQL = SQLDataTable(
                "sqlite",
                "audio.db",
                statement="""
                        SELECT Folders.FolderName, Folders.TotalFiles, Folders.FolderPath, 
                        CASE 
                            WHEN COUNT(DISTINCT Files.WorkerID) = 1 THEN MAX(Workers.WorkerName)
                            ELSE ''
                        END AS WorkerName
                        FROM Folders
                        LEFT JOIN Files ON Folders.FolderID = Files.FolderID
                        LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                        GROUP BY 
                            Folders.FolderName, 
                            Folders.TotalFiles, 
                            Folders.FolderPath
                        """,
            )

            files_table.controls[0] = add_check_column(new_fileSQL.datatable)
            page.update()

            folders_table.controls[0] = add_check_column(new_folderSQL.datatable)
            page.update()

            worker_dropdown.value = ""
            page.update()

    folders_table = ft.Column(
        [add_check_column(folderSQL.datatable)], tight=True, scroll="auto"
    )
    folders_controls = ft.Column(
        [
            worker_dropdown,
            ft.ElevatedButton(
                text="Assign Selected to Worker", on_click=folderButtonClick
            ),
        ],
        tight=True,
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )
    folders_tab = ft.Row(
        [folders_table, folders_controls],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
    )

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
        worker_dropdown.options = [
            ft.dropdown.Option(name) for name in generate_dropdown_options()
        ]
        page.update()

        workerTF1.value = ""
        workerTF2.value = ""
        page.update()

    def delete_and_refresh_workers(worker_name):
        def close_dlg(e):
            page.close(delete_worker_dialog)

        def execute_deletion(e):
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
            worker_dropdown.options = [
                ft.dropdown.Option(name) for name in generate_dropdown_options()
            ]
            page.update()
            close_dlg(e)

        delete_worker_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Warning!"),
            content=ft.Text(
                "Warning: Deleting a worker will result in losing all of their assignment info!\n\
                            Are you sure that you want to continue?"
            ),
            actions=[
                ft.TextButton("Yes", on_click=execute_deletion),
                ft.TextButton("No", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(delete_worker_dialog)

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
