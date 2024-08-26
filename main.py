import flet as ft
from db_updates import make_conn, commit_conn
import threading
from db_initialization import init_db
from simpledt import SQLDataTable
from db_updates import *


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


def gen_specific_worker_table(workerID=1):
    if type(workerID) is int:
        filteredSQL = SQLDataTable(
            "sqlite",
            "audio.db",
            statement=f"""
                       SELECT FileName, FileStatus, Comments
                       FROM Files
                       WHERE WorkerID = {workerID}
                       """,
        )
    else:
        filteredSQL = SQLDataTable(
            "sqlite",
            "audio.db",
            statement=f"""
                       SELECT Files.FileName, Files.FileStatus, Files.Comments
                       FROM Files
                       LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                       WHERE WorkerName = {workerID}
                       """,
        )
    return filteredSQL.datatable


def generate_dropdown_options():
    conn, cursor = make_conn()
    conn.row_factory = lambda cursor, row: row[0]
    worker_list = cursor.execute("SELECT WorkerName FROM Workers").fetchall()
    commit_conn(conn, cursor)
    return worker_list


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
                  SELECT Workers.WorkerName, Workers.WorkerType, COUNT(Files.FileName) AS FileCount
                  FROM Files
                  LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                  GROUP BY Workers.WorkerName, Workers.WorkerType
                  """,
    )

    workers_tab = ft.Column([workerSQL.datatable], tight=True, scroll="auto")
    files_tab = ft.Column([fileSQL.datatable], tight=True, scroll="auto")
    folders_tab = ft.Column([folderSQL.datatable], tight=True, scroll="auto")
    vetting_dropdown = ft.Dropdown(
        width=250,
        options=generate_dropdown_options(),
        on_change=lambda x: gen_specific_worker_table(x.control.value),
    )
    vetting_row = ft.Row(
        controls=[ft.Text("Select Worker:"), vetting_dropdown],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_tab = ft.Column(
        [vetting_row, gen_specific_worker_table()], tight=True, scroll="auto"
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
                    content=folders_tab, alignment=ft.alignment.top_center, padding=20
                ),
            ),
            ft.Tab(
                text="All Workers",
                content=ft.Container(
                    content=workers_tab, alignment=ft.alignment.top_center, padding=20
                ),
            ),
        ],
        expand=1,
    )
    page.add(tabs)
    page.update()


ft.app(target=main)
