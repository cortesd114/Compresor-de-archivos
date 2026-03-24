import flet as ft
import tkinter as tk
from tkinter import filedialog
import zipfile
import os


def seleccionar_carpeta():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    ruta = filedialog.askdirectory()
    root.destroy()
    return ruta


def seleccionar_guardado():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    ruta = filedialog.askdirectory()
    root.destroy()
    return ruta

def comprimir_carpeta(ruta, destino):
    nombre = os.path.basename(ruta)
    zip_path = os.path.join(destino, nombre + ".zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(ruta):
            for file in files:
                archivo = os.path.join(root, file)
                zipf.write(archivo)

    return zip_path

def main(page: ft.Page):
    page.title = "Compresor de Carpetas"
    page.window_width = 600
    page.window_height = 400
    page.bgcolor = "#f0f2f5"

    ruta_seleccionada = {"path": None}

    texto = ft.Text("Ninguna carpeta seleccionada", size=14)

    estado = ft.Text("", size=14)

    barra = ft.ProgressBar(width=300, visible=False)


    def seleccionar(e):
        ruta = seleccionar_carpeta()

        if ruta:
            ruta_seleccionada["path"] = ruta
            texto.value = f"{ruta}"
        else:
            texto.value = "Cancelado"

        page.update()


    def comprimir(e):
        if not ruta_seleccionada["path"]:
            estado.value = " Primero selecciona una carpeta"
            estado.color = "red"
            page.update()
            return

        destino = seleccionar_guardado()

        if not destino:
            estado.value = "Cancelaste el guardado"
            estado.color = "red"
            page.update()
            return

        barra.visible = True
        estado.value = "⏳ Comprimiendo..."
        estado.color = "blue"
        page.update()

        try:
            zip_path = comprimir_carpeta(ruta_seleccionada["path"], destino)

            estado.value = f"Guardado en:\n{zip_path}"
            estado.color = "green"

        except Exception as e:
            estado.value = f"Error: {str(e)}"
            estado.color = "red"

        barra.visible = False
        page.update()


    boton_seleccionar = ft.Button(
        "Seleccionar carpeta",
        on_click=seleccionar
    )

    boton_comprimir = ft.Button(
        "Comprimir",
        on_click=comprimir
    )

    contenido = ft.Column(
        [
            ft.Text("Compresor de Carpetas", size=22, weight="bold"),
            boton_seleccionar,
            boton_comprimir,
            texto,
            barra,
            estado
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15
    )

    card = ft.Container(
        content=contenido,
        padding=30,
        border_radius=15,
        bgcolor="white",
        width=500
    )

    page.add(
        ft.Container(
            content=card,
            alignment=ft.Alignment(0, 0),
            expand=True
        )
    )


ft.run(main)