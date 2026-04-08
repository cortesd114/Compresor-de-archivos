from __future__ import annotations

import os
import zipfile
from pathlib import Path


def _validate_destination(destination_folder: str) -> Path:
    destination = Path(destination_folder)
    if not destination.exists() or not destination.is_dir():
        raise ValueError("La carpeta destino no es valida.")

    return destination


def compress_folders(
    source_folders: list[str],
    destination_folder: str,
    archive_name: str | None = None,
) -> str:
    if not source_folders:
        raise ValueError("Debes seleccionar al menos una carpeta origen.")

    destination = _validate_destination(destination_folder)

    source_paths: list[Path] = []
    for item in source_folders:
        source = Path(item)
        if not source.exists() or not source.is_dir():
            raise ValueError(f"La carpeta origen no es valida: {item}")
        source_paths.append(source)

    clean_name = (archive_name or "").strip()
    if clean_name:
        zip_name = clean_name if clean_name.lower().endswith(".zip") else f"{clean_name}.zip"
    else:
        zip_name = f"{source_paths[0].name}.zip"

    zip_path = destination / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        used_root_names: dict[str, int] = {}

        for source in source_paths:
            root_name = source.name
            count = used_root_names.get(root_name, 0)
            used_root_names[root_name] = count + 1
            if count:
                root_name = f"{root_name}_{count + 1}"

            for root, _, files in os.walk(source):
                for file_name in files:
                    full_path = Path(root) / file_name
                    relative_name = full_path.relative_to(source)
                    arc_name = Path(root_name) / relative_name
                    zip_file.write(full_path, arc_name)

    return str(zip_path)


def compress_folder(source_folder: str, destination_folder: str) -> str:
    return compress_folders([source_folder], destination_folder)
