import flet as ft
from simpledt import SQLDataTable
from db_updates import *


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


def create_worker_dropdown():
    worker_names = generate_dropdown_options()
    return ft.Dropdown(
        label="Select Worker",
        options=[ft.dropdown.Option(name) for name in worker_names],
    )
