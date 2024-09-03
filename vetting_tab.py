import flet as ft
from simpledt import SQLDataTable
from dt_updates import (
    create_worker_dropdown,
    add_edit_column,
    add_audacity_column,
    add_image_column,
    add_play_column,
)
from db_updates import update_comments, get_filepath
from playsound import playsound
import os
import matplotlib.pyplot as plt
import librosa
import io
import base64
import numpy as np


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
        vetting_table.controls[0] = add_play_column(
            add_image_column(
                add_audacity_column(
                    add_edit_column(vettingSQLWorker.datatable, edit_comments)
                ),
                image_function,
            ),
            play_function,
        )
        page.update()

    worker_dropdown_vetting.on_change = on_worker_dropdown_change

    def play_function(file_name):
        filepath = get_filepath(file_name)
        playsound(os.path.join(os.getcwd(), filepath))

    def image_function(file_name):
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
            fig, ax = plt.subplots(nrows=3, sharex=True)
            librosa.display.waveshow(y, sr=sr, ax=ax[0], alpha=0.5)
            ax[0].set(title="Singlular Waveform")
            ax[0].set_xlabel("")
            ax[0].label_outer()
            y_harm, y_perc = librosa.effects.hpss(y)
            librosa.display.waveshow(
                y_harm, sr=sr, alpha=0.5, ax=ax[1], label="Harmonic"
            )
            librosa.display.waveshow(
                y_perc, sr=sr, color="r", alpha=0.5, ax=ax[1], label="Percussive"
            )
            ax[1].set(title="Multiple Waveforms")
            ax[1].set_xlabel("")
            ax[1].legend()
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
                ax=ax[2],
                cmap="gray_r",
            )
            ax[2].set(title="Spectrogram")
            ax[2].set_xlabel("Time (s)")
            ax[2].label_outer()
            fig.set_size_inches(9, 12)
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
            vetting_table.controls[0] = add_play_column(
                add_image_column(
                    add_audacity_column(
                        add_edit_column(vettingSQLWorker.datatable, edit_comments)
                    ),
                    image_function,
                ),
                play_function,
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
        [
            add_play_column(
                add_image_column(
                    add_audacity_column(
                        add_edit_column(vettingSQLNULL.datatable, edit_comments)
                    ),
                    image_function,
                ),
                play_function,
            )
        ],
        alignment=ft.MainAxisAlignment.START,
    )
    vetting_controls = ft.Column(
        [vetting_row, vetting_table],
        scroll="auto",
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=20,
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
