import flet as ft
from simpledt import SQLDataTable
from dt_updates import (
    create_worker_dropdown,
    create_visit_dropdown,
    add_edit_column,
    add_audioedit_column,
    add_play_column,
    add_pause_column,
    add_pause_column,
    add_status_dropdown,
    refresh_db_status,
    audioedit_function,
    audition_start,
)
from db_updates import (
    update_comments,
    get_filepath,
    generate_incompletevisitdropdown_options,
    generate_completevisitdropdown_options,
    get_directorypath,
)
import os
from just_playback import Playback


def create_vetting_tab(page: ft.Page):
    vettingQuery = """
                    SELECT Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments, Folders.FolderName
                    FROM Files
                    LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                    LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
                    """
    worker_dropdown_vetting = create_worker_dropdown()
    visit_dropdown_vetting = create_visit_dropdown(
        label_arg="Incomplete Visits", indicator="incomplete"
    )
    completed_dropdown_vetting = create_visit_dropdown(
        label_arg="Completed Visits", indicator="complete"
    )
    playback = Playback()

    def get_vettingSQLWorker(visit):
        vettingSQLWorker = SQLDataTable(
            "sqlite",
            os.path.join(get_directorypath("X:\\CHILD TD RSCH\\PRP"), "audio.db"),
            statement=vettingQuery + f"WHERE Folders.FolderName = '{visit}'",
        )
        return vettingSQLWorker

    def on_worker_dropdown_change(e):
        worker = worker_dropdown_vetting.value
        visit_dropdown_vetting.options = [
            ft.dropdown.Option(name)
            for name in generate_incompletevisitdropdown_options(worker)
        ]
        completed_dropdown_vetting.options = [
            ft.dropdown.Option(name)
            for name in generate_completevisitdropdown_options(worker)
        ]
        page.update()

    worker_dropdown_vetting.on_change = on_worker_dropdown_change

    def on_visit_dropdown_change(e):
        visit = visit_dropdown_vetting.value
        vettingSQLWorker = get_vettingSQLWorker(visit)
        vetting_table.controls[0] = refresh_vetting_table(vettingSQLWorker.datatable)
        on_worker_dropdown_change(e)
        page.update()

    def on_completed_dropdown_change(e):
        visit = completed_dropdown_vetting.value
        vettingSQLWorker = get_vettingSQLWorker(visit)
        vetting_table.controls[0] = refresh_vetting_table(vettingSQLWorker.datatable)
        on_worker_dropdown_change(e)
        page.update()

    visit_dropdown_vetting.on_change = on_visit_dropdown_change
    completed_dropdown_vetting.on_change = on_completed_dropdown_change

    def play_function(file_name):
        filepath = get_filepath(file_name)
        playback.load_file(filepath)
        playback.play()

    def pause_function():
        playback.pause()

    def edit_comments(filename, foldername, filetype):
        def close_dlg(e):
            page.close(edit_comments_dlg)

        new_comments = ft.TextField(label="Comments", max_length=50)

        def execute_edit(e):
            update_comments(filename, foldername, filetype, new_comments.value)
            visit = vetting_table.controls[0].rows[0].cells[5].content.value
            vettingSQLWorker = get_vettingSQLWorker(visit)
            vetting_table.controls[0] = refresh_vetting_table(
                vettingSQLWorker.datatable
            )
            page.update()
            close_dlg(e)

        edit_comments_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Editing Comments for {filename}"),
            content=ft.Column([new_comments], tight=True),
            actions=[
                ft.TextButton("Submit Edit", on_click=execute_edit),
                ft.TextButton("Cancel", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(edit_comments_dlg)

    def status_function(e, filename, foldername, filetype):
        filestatus = e.control.value
        refresh_db_status(filename, foldername, filetype, filestatus)
        visit = vetting_table.controls[0].rows[0].cells[5].content.value
        vettingSQLWorker = get_vettingSQLWorker(visit)
        vetting_table.controls[0] = refresh_vetting_table(vettingSQLWorker.datatable)
        page.update()

    def refresh_vetting_table(dt):
        newtable = add_status_dropdown(
            add_pause_column(
                add_play_column(
                    add_audioedit_column(add_edit_column(dt, edit_comments)),
                    play_function,
                ),
                pause_function,
            ),
            status_function,
        )
        return newtable

    def updateClick(e, filetype):
        def status_update_batched(filetype):
            for row in vetting_table.controls[0].rows:
                if row.cells[2].content.value == filetype:
                    if row.cells[3].content.content.value == "Incomplete":
                        refresh_db_status(
                            row.cells[0].content.value,
                            row.cells[5].content.value,
                            filetype,
                            "Complete",
                        )
                    else:
                        refresh_db_status(
                            row.cells[0].content.value,
                            row.cells[5].content.value,
                            filetype,
                            "Incomplete",
                        )

        if filetype == "Both":
            status_update_batched("Long")
            status_update_batched("Short")
        else:
            status_update_batched(filetype)
        vettingSQLWorker = get_vettingSQLWorker(
            vetting_table.controls[0].rows[0].cells[5].content.value
        )
        vetting_table.controls[0] = refresh_vetting_table(vettingSQLWorker.datatable)
        page.update()

    def auditionClick(e, filetype):
        def audition_batched(filetype):
            for row in vetting_table.controls[0].rows:
                if row.cells[2].content.value == filetype:
                    audioedit_function(row.cells[0].content.value)

        def auditionExecute():
            audition_start()
            if filetype == "STOCS":
                audition_batched("Long")
                audition_batched("Short")
            else:
                audition_batched("SSS")
            return None

        auditionExecute()

    vettingSQLNULL = SQLDataTable(
        "sqlite",
        os.path.join(get_directorypath("X:\\CHILD TD RSCH\\PRP"), "audio.db"),
        statement=vettingQuery + "WHERE Files.FileName = ''",
    )
    vetting_row = ft.Row(
        controls=[
            ft.Container(worker_dropdown_vetting, padding=10),
            ft.Container(visit_dropdown_vetting, padding=10),
            ft.Container(completed_dropdown_vetting, padding=10),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    audio_buttons = ft.Row(
        [
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Open All STOCS Files in Audition", size=16),
                    padding=ft.padding.all(10),
                ),
                on_click=lambda e: auditionClick(e, "STOCS"),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.PINK_900,
                    bgcolor=ft.colors.PINK_50,
                ),
                width=400,
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Open All SSS Files in Audition", size=16),
                    padding=ft.padding.all(10),
                ),
                on_click=lambda e: auditionClick(e, "SSS"),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.PINK_900,
                    bgcolor=ft.colors.PINK_50,
                ),
                width=400,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    vetting_buttons = ft.Row(
        [
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Toggle Long TOCS Status", size=16),
                    padding=ft.padding.all(10),
                ),
                on_click=lambda e: updateClick(e, "Long"),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Toggle Short TOCS Status", size=16),
                    padding=ft.padding.all(10),
                ),
                on_click=lambda e: updateClick(e, "Short"),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Toggle All TOCS Status", size=16),
                    padding=ft.padding.all(10),
                ),
                on_click=lambda e: updateClick(e, "Both"),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Toggle SSS Status", size=16),
                    padding=ft.padding.all(10),
                ),
                text="Toggle Short SSS Complete",
                on_click=lambda e: updateClick(e, "SSS"),
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
    vetting_table = ft.Row(
        [refresh_vetting_table(vettingSQLNULL.datatable)],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_controls = ft.Container(
        ft.Column(
            [vetting_row, audio_buttons, vetting_buttons, vetting_table],
            scroll="auto",
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        padding=ft.Padding(30, 50, 0, 50),
    )

    vetting_tab = ft.Row(
        controls=[vetting_controls],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30,
    )
    return vetting_tab, worker_dropdown_vetting
