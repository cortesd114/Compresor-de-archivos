from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import flet as ft

from app.services.compression_service import compress_folders


@dataclass
class AppState:
    source_folders: list[str] = field(default_factory=list)
    destination_folder: str | None = None
    zip_file_path: str | None = None


def build_home_page(page: ft.Page) -> None:
    page.title = "Compresor"
    page.padding = 0
    page.bgcolor = "#e6ecf7"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.AUTO
    page.window_width = 1060
    page.window_height = 760

    state = AppState()

    destination_text = ft.Text("Sin destino", color="#52607a", size=13)
    generated_zip_text = ft.Text("", color="#0f766e", selectable=True, size=13)
    selected_count_text = ft.Text("0 carpetas", color="#3a4a69", size=12)
    status_text = ft.Text("", color="#1f2a44", size=13)
    progress_ring = ft.ProgressRing(width=20, height=20, visible=False, color="#1f6feb")

    archive_name_input = ft.TextField(
        hint_text="Nombre del ZIP",
        dense=True,
        border_radius=12,
        text_size=14,
        height=44,
        content_padding=12,
    )

    selected_list = ft.Column(spacing=8)

    def set_status(message: str, color: str = "#0f172a") -> None:
        status_text.value = message
        status_text.color = color

    def set_busy(is_busy: bool) -> None:
        progress_ring.visible = is_busy

    def refresh_view() -> None:
        selected_count_text.value = f"{len(state.source_folders)} carpetas"
        page.update()

    folder_picker = ft.FilePicker()
    destination_picker = ft.FilePicker()
    page.services.extend([folder_picker, destination_picker])

    def remove_folder(index: int) -> None:
        if 0 <= index < len(state.source_folders):
            state.source_folders.pop(index)
            render_selected_folders()
            if not state.source_folders:
                set_status("Lista de carpetas vacia", "#92400e")

    def render_selected_folders() -> None:
        rows: list[ft.Control] = []
        for index, folder in enumerate(state.source_folders):
            path_obj = Path(folder)
            row = ft.Container(
                bgcolor="#f8fafc",
                border=ft.border.all(1, "#d8e1f0"),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                content=ft.Row(
                    [
                        ft.Text(folder, size=12, color="#34425d", expand=6, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(path_obj.name, size=12, color="#1f2a44", weight=ft.FontWeight.W_600, expand=3, no_wrap=True),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            tooltip="Eliminar",
                            style=ft.ButtonStyle(
                                color="#b91c1c",
                                shape=ft.RoundedRectangleBorder(radius=8),
                                bgcolor={ft.ControlState.HOVERED: "#fee2e2"},
                            ),
                            on_click=lambda _, idx=index: remove_folder(idx),
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
            rows.append(row)

        if not rows:
            rows.append(
                ft.Container(
                    border_radius=12,
                    padding=10,
                    bgcolor="#f8fafc",
                    border=ft.border.all(1, "#d8e1f0"),
                    content=ft.Text("Sin carpetas seleccionadas", size=12, color="#64748b"),
                )
            )

        selected_list.controls = rows
        refresh_view()

    async def add_folder(_: ft.ControlEvent) -> None:
        path = await folder_picker.get_directory_path(
            dialog_title="Selecciona una carpeta para agregar"
        )

        if path:
            if path in state.source_folders:
                set_status("Esa carpeta ya esta en la lista", "#92400e")
                refresh_view()
                return

            state.source_folders.append(path)
            render_selected_folders()
            set_status("Carpeta agregada", "#0f766e")
        else:
            set_status("Seleccion cancelada", "#9a3412")

        refresh_view()

    async def pick_destination(_: ft.ControlEvent) -> None:
        path = await destination_picker.get_directory_path(
            dialog_title="Selecciona la carpeta para guardar el ZIP"
        )

        if path:
            state.destination_folder = path
            destination_text.value = path
            set_status("Carpeta destino seleccionada", "#0f766e")
        else:
            set_status("Seleccion de carpeta destino cancelada", "#9a3412")

        refresh_view()

    def clear_folders(_: ft.ControlEvent) -> None:
        state.source_folders.clear()
        render_selected_folders()
        set_status("Lista limpiada", "#92400e")

    def clear_result() -> None:
        state.zip_file_path = None
        generated_zip_text.value = ""

    def compress_action(_: ft.ControlEvent) -> None:
        if not state.source_folders:
            set_status("Debes agregar al menos una carpeta", "#b91c1c")
            page.update()
            return

        if not state.destination_folder:
            set_status("Debes seleccionar una carpeta destino local", "#b91c1c")
            page.update()
            return

        try:
            set_busy(True)
            set_status("Comprimiendo carpetas...", "#1d4ed8")
            clear_result()
            page.update()

            state.zip_file_path = compress_folders(
                state.source_folders,
                state.destination_folder,
                archive_name_input.value,
            )
            generated_zip_text.value = state.zip_file_path
            set_status("Compresion completada", "#166534")
        except Exception as error:
            set_status(f"Error al comprimir: {error}", "#b91c1c")
        finally:
            set_busy(False)
            refresh_view()

    actions_row = ft.ResponsiveRow(
        [
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=ft.FilledButton(
                    "Agregar carpeta",
                    icon=ft.Icons.CREATE_NEW_FOLDER,
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    on_click=add_folder,
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=ft.OutlinedButton(
                    "Destino",
                    icon=ft.Icons.FOLDER_OPEN,
                    height=44,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
                    on_click=pick_destination,
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=ft.OutlinedButton(
                    "Limpiar",
                    icon=ft.Icons.CLEANING_SERVICES,
                    height=44,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=12),
                        color="#92400e",
                    ),
                    on_click=clear_folders,
                ),
            ),
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 3},
                content=ft.FilledButton(
                    "Comprimir",
                    icon=ft.Icons.ARCHIVE,
                    height=44,
                    style=ft.ButtonStyle(
                        bgcolor="#0f766e",
                        color="#ffffff",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                    on_click=compress_action,
                ),
            ),
        ],
        run_spacing=10,
        spacing=10,
    )

    list_header = ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=12,
        bgcolor="#eef3fb",
        content=ft.Row(
            [
                ft.Text("Ubicacion", size=12, color="#4a5a78", weight=ft.FontWeight.W_600, expand=6),
                ft.Text("Nombre", size=12, color="#4a5a78", weight=ft.FontWeight.W_600, expand=3),
                ft.Text("", expand=1),
            ],
            spacing=10,
        ),
    )

    result_row = ft.Row(
        [
            progress_ring,
            ft.Text("ZIP:", size=12, color="#52607a"),
            ft.Text("", size=12, expand=1),
            generated_zip_text,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    main_surface = ft.Container(
        width=960,
        padding=28,
        border_radius=24,
        border=ft.border.all(1, "#d4deed"),
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=20,
            color="#1f2a4430",
            offset=ft.Offset(0, 8),
        ),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, -1),
            end=ft.Alignment(1, 1),
            colors=["#ffffff", "#f3f7ff"],
        ),
        content=ft.Column(
            [
                actions_row,
                archive_name_input,
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=2),
                    content=ft.Row(
                        [
                            ft.Text("Destino:", size=12, color="#52607a", weight=ft.FontWeight.W_600),
                            destination_text,
                            ft.Container(expand=True),
                            selected_count_text,
                        ]
                    ),
                ),
                list_header,
                ft.Container(
                    height=300,
                    padding=4,
                    border_radius=14,
                    border=ft.border.all(1, "#d8e1f0"),
                    bgcolor="#fcfdff",
                    content=ft.ListView(
                        expand=True,
                        spacing=8,
                        controls=[selected_list],
                    ),
                ),
                result_row,
                status_text,
            ],
            spacing=14,
        ),
    )

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            content=main_surface,
            padding=24,
        )
    )

    render_selected_folders()
    refresh_view()
