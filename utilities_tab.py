import flet as ft
import os

utility_text = "Utility Outputs are Displayed Here:"


def create_utilities_tab(page: ft.Page):

    def updateDataClick(e):
        global utility_text
        utility_text += "\nSomething else."
        util_tab.controls[1].content.controls[0].value = utility_text
        page.update()

    def updateVettedClick(e):
        global utility_text
        utility_text += "\nAnother thing."
        util_tab.controls[1].content.controls[0].value = utility_text
        page.update()

    def generateProgressReport(e):
        global utility_text
        utility_text += "\nOther Text."
        util_tab.controls[1].content.controls[0].value = utility_text
        page.update()

    util_buttons = ft.Column(
        [
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Update AVA Data with New Files and Visits", size=16),
                    padding=ft.padding.all(20),
                ),
                on_click=updateDataClick,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.GREEN_900,
                    bgcolor=ft.colors.GREEN_50,
                ),
                width=450,
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(
                        value="Update Vetted Data Folder with Completed Files", size=16
                    ),
                    padding=ft.padding.all(20),
                ),
                on_click=updateVettedClick,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.GREEN_900,
                    bgcolor=ft.colors.GREEN_50,
                ),
                width=450,
            ),
            ft.ElevatedButton(
                content=ft.Container(
                    ft.Text(value="Generate New Progress Report", size=16),
                    padding=ft.padding.all(20),
                ),
                on_click=generateProgressReport,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5),
                    color=ft.colors.GREEN_900,
                    bgcolor=ft.colors.GREEN_50,
                ),
                width=450,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=50,
    )

    util_text = ft.Text(utility_text, weight=ft.FontWeight.BOLD)

    util_controls = ft.Container(
        ft.Column(
            [util_buttons],
            scroll="auto",
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
        ),
        padding=ft.Padding(100, 50, 50, 50),
    )

    util_output = ft.Container(
        ft.Column(
            [util_text],
            scroll="auto",
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
            auto_scroll=True,
        ),
        padding=ft.Padding(50, 50, 0, 50),
        bgcolor=ft.colors.BLACK12,
        width=700,
        height=400,
    )

    util_tab = ft.Row(
        controls=[util_controls, util_output],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=30,
    )
    return util_tab
