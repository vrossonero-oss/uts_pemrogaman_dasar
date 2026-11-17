"""Pembacaan dan penyimpanan file CSV/JSON (Praktikum 6)."""
import csv
import json
import logging
from pathlib import Path

from .exceptions import DataMahasiswaError, FormatDataError
from .validation import validate_student

logger = logging.getLogger("student_manager")

REQUIRED_COLUMNS = ("nim", "name", "program", "score", "attendance")
EXPORT_COLUMNS = ("nim", "name", "program", "score", "attendance", "status")


def _validate_rows(rows):
    """Validasi tiap baris; kembalikan (record valid, daftar error)."""
    valid, errors = [], []
    for line_number, row in rows:
        try:
            valid.append(validate_student(row))
        except DataMahasiswaError as error:
            logger.warning("Baris %d ditolak: %s", line_number, error)
            errors.append((line_number, str(error)))
    return valid, errors


def load_students_csv(path):
    """Baca CSV mahasiswa. FileNotFoundError dibiarkan naik ke pemanggil."""
    try:
        with open(Path(path), "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or []
            missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
            if missing:
                raise FormatDataError("kolom tidak lengkap: " + ", ".join(missing))
            rows = list(enumerate(reader, start=2))
    except (UnicodeDecodeError, csv.Error) as error:
        raise FormatDataError(f"CSV tidak dapat dibaca ({error})") from error
    return _validate_rows(rows)


def load_students_json(path):
    """Baca JSON berisi list dictionary mahasiswa."""
    try:
        with open(Path(path), "r", encoding="utf-8") as file:
            raw = json.load(file)
    except json.JSONDecodeError as error:
        raise FormatDataError(f"JSON rusak ({error})") from error
    if not isinstance(raw, list):
        raise FormatDataError("isi JSON harus berupa list")
    return _validate_rows(enumerate(raw, start=1))


def load_students(path):
    """Pilih pembaca berdasarkan ekstensi file."""
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return load_students_csv(path)
    if suffix == ".json":
        return load_students_json(path)
    raise FormatDataError(f"ekstensi '{suffix}' tidak didukung (.csv/.json)")


def save_students_json(students, path):
    """Simpan list mahasiswa ke JSON (serialization)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)
    logger.info("%d record disimpan ke %s", len(students), path.name)


def export_report_csv(students, path):
    """Ekspor laporan (termasuk kolom status) ke CSV."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=EXPORT_COLUMNS)
        writer.writeheader()
        writer.writerows(students)
    logger.info("Laporan CSV dibuat: %s", path.name)


def save_text(text, path):
    """Simpan teks laporan ke file .txt."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(text + "\n")
    logger.info("Laporan teks dibuat: %s", path.name)
