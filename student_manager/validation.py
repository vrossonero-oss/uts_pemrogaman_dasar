"""Validasi data mahasiswa.

Aturan: nim/nama/prodi teks tidak kosong, nilai dan kehadiran bilangan
bulat 0-100 (0 sah, True ditolak). Mengikuti Praktikum 3, 4, dan 5.
"""
from .exceptions import DataMahasiswaError, NamaKosongError


def validate_text(value, label):
    """Kembalikan teks yang sudah di-strip, tolak None/kosong/bukan str."""
    if not isinstance(value, str) or not value.strip():
        raise DataMahasiswaError(f"{label} wajib diisi.")
    return value.strip()


def validate_nim(value):
    """NIM harus teks tidak kosong yang hanya berisi angka."""
    nim = validate_text(value, "NIM")
    if not nim.isdigit():
        raise DataMahasiswaError("NIM harus berupa angka.")
    return nim


def validate_name(value):
    """Nama tidak boleh kosong setelah strip()."""
    if not isinstance(value, str) or not value.strip():
        raise NamaKosongError("Nama wajib diisi.")
    return value.strip()


def validate_number(value, label):
    """Nilai/kehadiran: int 0-100. type() is int agar True ditolak."""
    if type(value) is not int:
        raise DataMahasiswaError(f"{label} harus bilangan bulat.")
    if not 0 <= value <= 100:
        raise DataMahasiswaError(f"{label} harus antara 0 dan 100.")
    return value


def parse_int(text, label):
    """Ubah teks (misal dari CSV/input) menjadi int dengan pesan jelas."""
    try:
        return int(str(text).strip())
    except ValueError:
        raise DataMahasiswaError(f"{label} harus bilangan bulat.") from None


def validate_number_text(text, label):
    """Gabungan parse_int dan validate_number untuk input pengguna."""
    return validate_number(parse_int(text, label), label)


def validate_student(raw):
    """Validasi satu record (dict) lalu kembalikan dict bersih."""
    if not isinstance(raw, dict):
        raise DataMahasiswaError("Data mahasiswa harus berupa dictionary.")
    score = raw.get("score")
    attendance = raw.get("attendance")
    if isinstance(score, str):
        score = parse_int(score, "Nilai")
    if isinstance(attendance, str):
        attendance = parse_int(attendance, "Kehadiran")
    return {
        "nim": validate_nim(raw.get("nim")),
        "name": validate_name(raw.get("name")),
        "program": validate_text(raw.get("program"), "Program studi"),
        "score": validate_number(score, "Nilai"),
        "attendance": validate_number(attendance, "Kehadiran"),
    }
