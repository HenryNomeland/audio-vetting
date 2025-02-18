import flet as ft
from db_updates import *
from dt_updates import *
from vetting_tab import *
from utilities_tab import *
import pandas as pd
from typing import List


class SQLDataTable:
    def __init__(self, statement: str) -> None:
        self.statement = statement
        self._set_datatable()

    def _set_datatable(self) -> None:
        df = self._df
        dt_columns = [ft.DataColumn(ft.Text(col)) for col in df.columns]
        dt_rows = [
            ft.DataRow([ft.DataCell(ft.Text(str(cell))) for cell in row])
            for row in df.values
        ]
        self.datatable = ft.DataTable(columns=dt_columns, rows=dt_rows)

    @property
    def _df(self) -> pd.DataFrame:
        with make_conn() as conn:
            df = pd.read_sql_query(self.statement, conn)
        return df

    @property
    def _cols(self) -> List[str]:
        return self._df.columns.to_list()

    @property
    def _rows(self) -> List[List[str]]:
        return self._df.values.tolist()


def main(page: ft.Page):
    page.title = "Audio Vetting Application"
    page.window.height = None
    page.window.width = None
    page.window.maximized = True
    fileQuery = """
                SELECT Folders.FolderName, Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments
                FROM Files
                LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
                LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                """
    folderQuery1 = """
                   SELECT Folders.FolderName, Folders.TotalFiles, Folders.FolderPath, 
                   CASE 
                       WHEN COUNT(DISTINCT Files.WorkerID) = 1 THEN MAX(Workers.WorkerName)
                       ELSE ''
                   END AS WorkerName
                   FROM Folders
                   LEFT JOIN Files ON Folders.FolderID = Files.FolderID
                   LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                   """
    folderQuery2 = """
                   GROUP BY 
                       Folders.FolderName, 
                       Folders.TotalFiles, 
                       Folders.FolderPath
                   """
    workerQuery = """
                  SELECT Workers.WorkerName, Workers.WorkerType
                  FROM Workers
                  """
    fileSQL = SQLDataTable(
        statement=fileQuery + f"WHERE Folders.FolderName = '{get_default_visit()}'",
    )
    fileDataTable = fileSQL.datatable
    folderSQL = SQLDataTable(
        statement=folderQuery1
        + f"WHERE Folders.FolderGroup = '{get_default_foldergroup()}'"
        + folderQuery2,
    )
    folderDataTable = folderSQL.datatable
    workerSQL = SQLDataTable(
        statement=workerQuery,
    )
    workerDataTable = workerSQL.datatable

    def update_files_and_folders(
        visit=get_default_visit(), foldergroup=get_default_foldergroup()
    ):
        if visit == "":
            visit = get_default_visit()
        if foldergroup == "":
            foldergroup = get_default_foldergroup()
        new_fileSQL = SQLDataTable(
            statement=fileQuery + f"WHERE Folders.FolderName = '{visit}'",
        )
        new_fileDataTable = new_fileSQL.datatable
        new_folderSQL = SQLDataTable(
            statement=folderQuery1
            + f"WHERE Folders.FolderGroup = '{foldergroup}'"
            + folderQuery2,
        )
        new_folderDataTable = new_folderSQL.datatable
        files_table.controls[0] = color_status_col(add_check_column(new_fileDataTable))
        folders_table.controls[0] = add_check_column(new_folderDataTable)
        page.update()

    vetting_tab, worker_dropdown_vetting = create_vetting_tab(page)
    utilities_tab = create_utilities_tab(page)
    worker_dropdown = create_worker_dropdown()

    def fileButtonClick(e):
        if worker_dropdown.value != "":
            filelist = []
            for row in files_table.controls[0].rows:
                if row.cells[6].content.value:
                    filelist.append(row.cells[1].content.value)
            update_file_assignments(worker_dropdown.value, filelist)
            update_files_and_folders(visit=visit_dropdown_files.value)
            worker_dropdown.value = ""
            worker_dropdown_vetting.value = ""
            page.update()

    def fileAltButtonClick(e):
        filelist = []
        for row in files_table.controls[0].rows:
            if row.cells[6].content.value:
                filelist.append(row.cells[1].content.value)
        scrub_file_assignments(filelist)
        update_files_and_folders(visit=visit_dropdown_files.value)
        worker_dropdown.value = ""
        worker_dropdown_vetting.value = ""
        page.update()

    def on_visitfiles_dropdown_change(e):
        visit = visit_dropdown_files.value
        fileSQL = SQLDataTable(
            statement=fileQuery + f"WHERE Folders.FolderName = '{visit}'",
        )
        fileDataTable = fileSQL.datatable
        files_table.controls[0] = color_status_col(add_check_column(fileDataTable))
        page.update()

    visit_dropdown_files = create_visit_dropdown()
    visit_dropdown_files.on_change = on_visitfiles_dropdown_change

    files_table = ft.Column(
        [color_status_col(add_check_column(fileDataTable))],
        tight=True,
        scroll="auto",
    )
    files_controls = ft.Column(
        [
            visit_dropdown_files,
            worker_dropdown,
            ft.ElevatedButton(
                text="Assign Selected to Worker", on_click=fileButtonClick
            ),
            ft.ElevatedButton(
                text="Unassign Selected Files", on_click=fileAltButtonClick
            ),
        ],
        tight=True,
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )
    files_tab = ft.Container(
        ft.Row(
            [files_table, files_controls],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
        ),
        padding=ft.Padding(0, 50, 0, 50),
    )

    def folderButtonClick(e):
        if worker_dropdown.value != "":
            folderlist = []
            for row in folders_table.controls[0].rows:
                if row.cells[4].content.value:
                    folderlist.append(row.cells[2].content.value)
            update_folder_assignments(worker_dropdown.value, folderlist)
            update_files_and_folders(foldergroup=foldergroup_dropdown.value)
            worker_dropdown.value = ""
            worker_dropdown_vetting.value = ""
            page.update()

    def folderAltButtonClick(e):
        folderlist = []
        for row in folders_table.controls[0].rows:
            if row.cells[4].content.value:
                folderlist.append(row.cells[2].content.value)
        scrub_folder_assignments(folderlist)
        update_files_and_folders(foldergroup=foldergroup_dropdown.value)
        worker_dropdown.value = ""
        worker_dropdown_vetting.value = ""
        page.update()

    def on_foldergroup_dropdown_change(e):
        group = foldergroup_dropdown.value
        folderSQL = SQLDataTable(
            statement=folderQuery1
            + f"WHERE Folders.FolderGroup = '{group}'"
            + folderQuery2,
        )
        folderDataTable = folderSQL.datatable
        folders_table.controls[0] = add_check_column(folderDataTable)
        page.update()

    foldergroup_dropdown = create_foldergroup_dropdown()
    foldergroup_dropdown.on_change = on_foldergroup_dropdown_change

    folders_table = ft.Column(
        [add_check_column(folderDataTable)], tight=True, scroll="auto"
    )
    folders_controls = ft.Column(
        [
            foldergroup_dropdown,
            worker_dropdown,
            ft.ElevatedButton(
                text="Assign Selected to Worker", on_click=folderButtonClick
            ),
            ft.ElevatedButton(
                text="Unassign Selected Files", on_click=folderAltButtonClick
            ),
        ],
        tight=True,
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20,
    )
    folders_tab = ft.Container(
        ft.Row(
            [folders_table, folders_controls],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30,
        ),
        padding=ft.Padding(0, 50, 0, 50),
    )

    def workerButtonClick(e):
        if (workerTF1.value != "") and (workerTF2.value != ""):
            add_worker(workerTF1.value, workerTF2.value)
            new_workerSQL = SQLDataTable(
                statement=workerQuery,
            )
            new_workerDataTable = new_workerSQL.datatable

        workers_table.controls[0] = add_delete_column(
            new_workerDataTable, delete_and_refresh_workers
        )
        page.update()
        worker_dropdown.options = [
            ft.dropdown.Option(name) for name in generate_dropdown_options()
        ]
        worker_dropdown_vetting.options = [
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
                statement=workerQuery,
            )
            new_workerDataTable = new_workerSQL.datatable
            workers_table.controls[0] = add_delete_column(
                new_workerDataTable, delete_and_refresh_workers
            )
            worker_dropdown.options = [
                ft.dropdown.Option(name) for name in generate_dropdown_options()
            ]
            worker_dropdown_vetting.options = [
                ft.dropdown.Option(name) for name in generate_dropdown_options()
            ]
            page.update()
            update_files_and_folders()
            close_dlg(e)

        delete_worker_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Warning!"),
            content=ft.Text(
                """
                Warning: Deleting a worker will result in losing all of their assignment info!\n
                Note: closing and reopening the program is necessary for the effects of the deletion to be present in the files/folders tables.\n
                Are you sure that you want to continue?
                """
            ),
            actions=[
                ft.TextButton("Yes", on_click=execute_deletion),
                ft.TextButton("No", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(delete_worker_dialog)

    workers_table = ft.Column(
        [add_delete_column(workerDataTable, delete_and_refresh_workers)],
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
                    content=vetting_tab, alignment=ft.alignment.center, padding=20
                ),
            ),
            ft.Tab(
                text="All Files",
                content=ft.Container(
                    content=files_tab, alignment=ft.alignment.center, padding=20
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
            ft.Tab(
                text="Utilities",
                content=ft.Container(
                    content=utilities_tab, alignment=ft.alignment.center, padding=20
                ),
            ),
        ],
        on_click=lambda e: update_files_and_folders(),
        expand=1,
    )
    page.add(tabs)
    page.update()


ft.app(target=main)
