import flet as ft
from db_updates import make_conn, commit_conn

def main(page: ft.Page):
    page.title = "PRP Vetting"
    page.appbar = ft.AppBar(
        title = ft.Text("PRP Vetting Application"),
        actions = [
            ft.IconButton(ft.icons.MINIMIZE, on_click = lambda e: page.window_minimized()),
            ft.IconButton(ft.icons.CROP_SQUARE, on_click = lambda e: page.window_maximized()),
            ft.IconButton(ft.icons.CLOSE, on_click = lambda e: page.window_close())
        ]
    ) 
    page.window_frameless = True

    vetting_tab = ft.Container(
        content = ft.Text("This is the Vetting Tab"), alignment = ft.alignment.center
    )
    files_tab = ft.Container(
        content = ft.Text("This is the Files Tab"), alignment = ft.alignment.center
    )
    folders_tab = ft.Container(
        content = ft.Text("This is the Folders Tab"), alignment = ft.alignment.center
    )

    tabs = ft.Tabs(
        selected_index = 1,
        animation_duration = 300,
        tabs = [
            ft.Tab(
                text = "Vetting",
                content = vetting_tab
            ),
            ft.Tab(
                text = "All Data by File",
                content = files_tab
            ),
            ft.Tab(
                text = "All Data by Folder",
                content = folders_tab
            )
        ],
        expand = 1
    )
    page.add(tabs)

ft.app(target=main)