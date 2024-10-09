import flet as ft
from simpledt import SQLDataTable
from dt_updates import (
    create_worker_dropdown,
    create_visit_dropdown,
    add_edit_column,
    add_audioedit_column,
    add_image_column,
    add_play_column,
    add_pause_column,
    add_pause_column,
    add_status_dropdown,
    refresh_db_status,
)
from db_updates import update_comments, get_filepath, generate_visitdropdown_options
import winsound
import os
import matplotlib.pyplot as plt
import librosa
import io
import base64
import numpy as np
import seaborn as sns


def create_vetting_tab(page: ft.Page, update_files_and_folders):
    vettingQuery = """
                    SELECT Files.FileName, Workers.WorkerName, Files.FileType, Files.FileStatus, Files.Comments, Folders.FolderName
                    FROM Files
                    LEFT JOIN Workers ON Files.WorkerID = Workers.WorkerID
                    LEFT JOIN Folders ON Files.FolderID = Folders.FolderID
                    """
    worker_dropdown_vetting = create_worker_dropdown()
    worker_dropdown_vetting.options.insert(0, ft.dropdown.Option("All"))
    visit_dropdown_vetting = create_visit_dropdown()
    visit_dropdown_vetting.options.insert(0, ft.dropdown.Option("All"))
    sns.set_theme(
        style="whitegrid",
        rc={"axes.spines.right": False, "axes.spines.top": False, "axes.grid": False},
    )

    def get_vettingSQLWorker(worker, visit):
        if worker != "All":
            if visit != "All":
                vettingSQLWorker = SQLDataTable(
                    "sqlite",
                    "audio.db",
                    statement=vettingQuery
                    + f"WHERE Workers.WorkerName = '{worker}' AND Folders.FolderName = '{visit}'",
                )
            else:
                vettingSQLWorker = SQLDataTable(
                    "sqlite",
                    "audio.db",
                    statement=vettingQuery + f"WHERE Workers.WorkerName = '{worker}'",
                )
        else:
            vettingSQLWorker = SQLDataTable(
                "sqlite",
                "audio.db",
                statement=vettingQuery + f"WHERE Folders.FolderName = '{visit}'",
            )
        return vettingSQLWorker

    def on_worker_dropdown_change(e):
        worker = worker_dropdown_vetting.value
        visit_dropdown_vetting.options = [
            ft.dropdown.Option(name) for name in generate_visitdropdown_options(worker)
        ]
        page.update()

    worker_dropdown_vetting.on_change = on_worker_dropdown_change

    def on_visit_dropdown_change(e):
        worker = worker_dropdown_vetting.value
        visit = visit_dropdown_vetting.value
        vettingSQLWorker = get_vettingSQLWorker(worker, visit)
        vetting_table.controls[0] = refresh_vetting_table(vettingSQLWorker.datatable)
        page.update()

    visit_dropdown_vetting.on_change = on_visit_dropdown_change

    def play_function(file_name):
        filepath = get_filepath(file_name)
        winsound.PlaySound(os.path.join(os.getcwd(), filepath), winsound.SND_ASYNC)

    def pause_function():
        winsound.PlaySound(None, winsound.SND_PURGE)

    def image_function(file_name):
        filenamename = file_name.split(".")[0]
        if file_name == "":
            fig = plt.figure()
        else:
            # plotting the in-progress screen
            fig, ax = plt.subplots()
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect("equal")
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                "Plotting in Progress...",
                fontsize=15,
                ha="center",
                va="center",
            )
            fig.patch.set_alpha(0)
            buf = io.BytesIO()
            plt.savefig(buf, format="png", transparent=True)
            buf.seek(0)
            plt.close(fig)
            img_str = base64.b64encode(buf.read()).decode("utf-8")
            if file_name == "":
                return img_str
            soundplot.src_base64 = img_str
            page.update()
            # plotting the actual plot
            filepath = get_filepath(file_name)
            y, sr = librosa.load(filepath)
            fig, ax = plt.subplots(nrows=2, sharex=True)
            librosa.display.waveshow(y, sr=sr, ax=ax[0], alpha=0.5)
            ax[0].set(title=f"Singular Waveform - {filenamename}")
            ax[0].set_xlabel("")
            ax[0].label_outer()
            hop_length = 1024
            D = librosa.amplitude_to_db(
                np.abs(librosa.stft(y, hop_length=hop_length)), ref=np.max
            )
            librosa.display.specshow(
                D,
                y_axis="log",
                sr=sr,
                hop_length=hop_length,
                x_axis="time",
                ax=ax[1],
                cmap="gray_r",
            )
            ax[1].set(title=f"Spectrogram - {filenamename}")
            ax[1].set_xlabel("Time (s)")
            ax[1].label_outer()
            plt.subplots_adjust(
                left=0.125, right=0.9, bottom=0.1, top=0.9, wspace=0.4, hspace=0.2
            )
            fig.set_size_inches(13, 13)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", transparent=True)
        buf.seek(0)
        plt.close(fig)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        if file_name == "":
            return img_str
        soundplot.src_base64 = img_str
        page.update()

    def edit_comments(file_name):
        def close_dlg(e):
            page.close(edit_comments_dlg)

        new_comments = ft.TextField(label="Comments", max_length=50)

        def execute_edit(e):
            update_comments(file_name, new_comments.value)
            worker = worker_dropdown_vetting.value
            visit = visit_dropdown_vetting.value
            vettingSQLWorker = get_vettingSQLWorker(worker, visit)
            vetting_table.controls[0] = refresh_vetting_table(
                vettingSQLWorker.datatable
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

    def status_function(e, filename):
        filestatus = e.control.value
        refresh_db_status(filename, filestatus)
        vetting_table.controls[0] = add_status_dropdown(
            vetting_table.controls[0], status_function
        )
        update_files_and_folders()
        page.update()

    def refresh_vetting_table(dt):
        newtable = add_status_dropdown(
            add_pause_column(
                add_play_column(
                    add_image_column(
                        add_audioedit_column(add_edit_column(dt, edit_comments)),
                        image_function,
                    ),
                    play_function,
                ),
                pause_function,
            ),
            status_function,
        )
        return newtable

    vettingSQLNULL = SQLDataTable(
        "sqlite", "audio.db", statement=vettingQuery + "WHERE Files.FileName = ''"
    )
    vetting_row = ft.Row(
        controls=[
            ft.Container(ft.Text("Select Worker:"), padding=10),
            ft.Container(worker_dropdown_vetting, padding=10),
            ft.Container(ft.Text("Select Visit:"), padding=10),
            ft.Container(visit_dropdown_vetting, padding=10),
        ],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_table = ft.Row(
        [refresh_vetting_table(vettingSQLNULL.datatable)],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_controls = ft.Container(
        ft.Column(
            [vetting_row, vetting_table],
            scroll="auto",
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        padding=ft.Padding(30, 50, 0, 50),
    )
    soundplot = ft.Image(src=image_function(""))

    vetting_output = ft.Column(
        [ft.Container(content=soundplot, alignment=ft.alignment.center)],
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
