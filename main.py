"""Student Grade Manager - aplikasi command line pengolah data nilai mahasiswa.

Jalankan dari folder proyek:  python main.py
Opsi:                          python main.py --input data/students.csv
"""
import argparse
import logging
from pathlib import Path

from student_manager import (
    STATUS_LIST, DataMahasiswaError, DuplicateNimError, FormatDataError,
    add_status, add_student, create_group_text, create_ranking,
    create_ranking_text, create_report, create_summary_text,
    export_report_csv, filter_by_program, filter_by_status,
    get_unique_programs, group_by_program, load_students, parse_int,
    remove_duplicates, save_students_json, save_text, search_by_nim,
    summarize, summarize_groups, validate_name, validate_nim,
    validate_number_text, validate_text,
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = BASE_DIR / "data" / "students.csv"
DEFAULT_OUTPUT = BASE_DIR / "data" / "output"
LOG_FILE = BASE_DIR / "logs" / "app.log"

logger = logging.getLogger("student_manager")

MENU = """
========================================
        STUDENT GRADE MANAGER
========================================
1. Tampilkan semua mahasiswa
2. Cari mahasiswa berdasarkan NIM
3. Filter berdasarkan status
4. Filter berdasarkan program studi
5. Rekap per program studi
6. Ranking nilai
7. Ringkasan statistik
8. Tambah mahasiswa
9. Simpan JSON dan ekspor laporan CSV
0. Keluar
========================================"""


def setup_logging():
    """Log lengkap ke file, hanya WARNING ke terminal."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def read_valid(prompt, validator):
    """Ulangi input sampai lolos validator (pola Praktikum 5)."""
    while True:
        try:
            return validator(input(prompt))
        except DataMahasiswaError as error:
            logger.warning("Input ditolak: %s", error)
            print(f"Input salah: {error}")


def load_initial_data(path):
    """Muat file awal; jika gagal, mulai dengan data kosong."""
    try:
        raw, errors = load_students(path)
    except FileNotFoundError:
        logger.error("File tidak ditemukan: %s", path)
        print(f"File '{path}' tidak ditemukan. Program dimulai dengan data kosong.")
        return []
    except FormatDataError as error:
        logger.error("Format data tidak valid: %s", error)
        print(f"Format data tidak valid: {error}. Program dimulai dengan data kosong.")
        return []
    except OSError as error:
        logger.error("Gagal membuka file: %s", error)
        print(f"File tidak dapat dibuka: {error}. Program dimulai dengan data kosong.")
        return []
    unique, duplicates = remove_duplicates(raw)
    logger.info(
        "Data dimuat: %d valid, %d duplikat, %d ditolak",
        len(unique), len(duplicates), len(errors),
    )
    print(
        f"Data dimuat: {len(unique)} mahasiswa, "
        f"{len(duplicates)} duplikat dibuang, {len(errors)} baris ditolak."
    )
    for line_number, message in errors:
        print(f"  Baris {line_number}: {message}")
    return add_status(unique)


def menu_show(students):
    print(create_report(students))


def menu_search(students):
    nim = input("Masukkan NIM: ").strip()
    student = search_by_nim(students, nim)
    if student is None:
        logger.info("Pencarian NIM %s: tidak ditemukan", nim)
        print("Mahasiswa tidak ditemukan.")
        return
    print(f"NIM     : {student['nim']}")
    print(f"Nama    : {student['name']}")
    print(f"Program : {student['program']}")
    print(f"Nilai   : {student['score']}")
    print(f"Hadir   : {student['attendance']}%")
    print(f"Status  : {student['status']}")


def menu_filter_status(students):
    print("Pilihan status: " + ", ".join(STATUS_LIST))
    status = input("Status: ").strip()
    if status.lower() not in (s.lower() for s in STATUS_LIST):
        logger.warning("Status tidak dikenal: %s", status)
        print("Status tidak dikenal.")
        return
    print(create_report(filter_by_status(students, status)))


def menu_filter_program(students):
    programs = sorted(get_unique_programs(students))
    if not programs:
        print("Belum ada data.")
        return
    print("Program studi: " + ", ".join(programs))
    program = input("Program studi: ").strip()
    result = filter_by_program(students, program)
    if not result:
        logger.warning("Program tidak ditemukan: %s", program)
        print("Program studi tidak ditemukan.")
        return
    print(create_report(result))


def menu_group(students):
    print(create_group_text(summarize_groups(group_by_program(students))))


def menu_ranking(students):
    print(create_ranking_text(create_ranking(students)))


def menu_summary(students):
    print(create_summary_text(summarize(students)))


def menu_add(students):
    """Tambah mahasiswa; kembalikan list baru (list lama tidak diubah)."""
    existing = {s["nim"] for s in students}

    def validate_new_nim(text):
        nim = validate_nim(text)
        if nim in existing:
            raise DuplicateNimError("NIM sudah terdaftar.")
        return nim

    nim = read_valid("NIM: ", validate_new_nim)
    name = read_valid("Nama: ", validate_name)
    program = read_valid("Program studi: ", lambda t: validate_text(t, "Program studi"))
    score = read_valid("Nilai (0-100): ", lambda t: validate_number_text(t, "Nilai"))
    attendance = read_valid("Kehadiran % (0-100): ", lambda t: validate_number_text(t, "Kehadiran"))
    new_student = {
        "nim": nim, "name": name, "program": program,
        "score": score, "attendance": attendance,
    }
    updated = add_student(new_student, students)
    logger.info("Mahasiswa ditambahkan: NIM %s", nim)
    print("Data ditambahkan.")
    return updated


def menu_save(students, output_dir):
    if not students:
        logger.warning("Simpan dibatalkan: data kosong")
        print("Belum ada data untuk disimpan.")
        return
    try:
        save_students_json(students, output_dir / "students.json")
        export_report_csv(students, output_dir / "laporan_nilai.csv")
        save_text(
            create_report(students) + "\n\n" + create_summary_text(summarize(students)),
            output_dir / "laporan_nilai.txt",
        )
    except OSError as error:
        logger.error("Gagal menyimpan file: %s", error)
        print(f"Gagal menyimpan file: {error}")
        return
    print(f"File tersimpan di {output_dir}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Student Grade Manager")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="file .csv atau .json")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT), help="folder hasil")
    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging()
    output_dir = Path(args.output_dir)
    logger.info("Program dimulai")
    students = load_initial_data(args.input)

    actions = {
        "1": menu_show, "2": menu_search, "3": menu_filter_status,
        "4": menu_filter_program, "5": menu_group, "6": menu_ranking,
        "7": menu_summary,
    }
    while True:
        print(MENU)
        try:
            choice = input("Pilihan: ").strip()
            if choice == "0":
                break
            if choice in actions:
                actions[choice](students)
            elif choice == "8":
                students = menu_add(students)
            elif choice == "9":
                menu_save(students, output_dir)
            else:
                logger.warning("Pilihan menu tidak tersedia: %r", choice)
                print("Pilihan tidak tersedia.")
        except (EOFError, KeyboardInterrupt):
            print("\nInput dihentikan.")
            break
    logger.info("Program selesai")
    print("Selesai.")


if __name__ == "__main__":
    main()
