"""Exception khusus untuk aturan data mahasiswa (pola dari Praktikum 5)."""


class DataMahasiswaError(ValueError):
    """Data mahasiswa tidak sesuai aturan."""


class NamaKosongError(DataMahasiswaError):
    """Nama mahasiswa tidak boleh kosong."""


class DuplicateNimError(DataMahasiswaError):
    """NIM sudah terdaftar."""


class FormatDataError(Exception):
    """Isi atau struktur file data tidak valid (kolom kurang, JSON rusak)."""
