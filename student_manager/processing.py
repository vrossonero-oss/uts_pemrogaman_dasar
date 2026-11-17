"""Pemrosesan data: status, pencarian, filter, grouping, ranking, rekap.

Semua fungsi hanya mengembalikan nilai (tanpa print) dan tidak mengubah
data masukan.
"""
from .exceptions import DuplicateNimError

STATUS_LIST = (
    "Peringatan Kehadiran",
    "Lulus dengan Pujian",
    "Lulus",
    "Remedial",
    "Tidak Lulus",
)
PASSED_STATUS = ("Lulus", "Lulus dengan Pujian")
MIN_ATTENDANCE = 75


def determine_status(score, attendance):
    """Status sesuai urutan prioritas aturan Praktikum 3."""
    if attendance < MIN_ATTENDANCE:
        return "Peringatan Kehadiran"
    if score >= 90 and attendance >= 90:
        return "Lulus dengan Pujian"
    if score >= 80:
        return "Lulus"
    if score >= 60:
        return "Remedial"
    return "Tidak Lulus"


def add_status(students):
    """List baru yang setiap record-nya punya kunci status."""
    return [
        {**s, "status": determine_status(s["score"], s["attendance"])}
        for s in students
    ]


def calculate_average(values):
    """Rata-rata, None untuk list kosong (bukan ZeroDivisionError)."""
    if not values:
        return None
    return sum(values) / len(values)


def remove_duplicates(students):
    """Pisahkan record unik dan duplikat berdasarkan NIM (set)."""
    seen = set()
    unique, duplicates = [], []
    for student in students:
        if student["nim"] in seen:
            duplicates.append(student)
            continue
        seen.add(student["nim"])
        unique.append(student)
    return unique, duplicates


def get_unique_programs(students):
    """Set program studi tanpa duplikasi (set comprehension)."""
    return {s["program"] for s in students}


def search_by_nim(students, nim):
    """Cari lewat indeks dictionary, None jika tidak ada."""
    index = {s["nim"]: s for s in students}
    return index.get(nim)


def filter_by_status(students, status):
    """Filter status tanpa membedakan huruf besar/kecil."""
    return [s for s in students if s["status"].lower() == status.lower()]


def filter_by_program(students, program):
    """Filter berdasarkan program studi."""
    return [s for s in students if s["program"].lower() == program.lower()]


def group_by_program(students):
    """Dictionary: program studi -> list mahasiswa."""
    groups = {}
    for student in students:
        groups.setdefault(student["program"], []).append(student)
    return groups


def summarize_groups(groups):
    """Dictionary comprehension: jumlah dan rata-rata nilai per program."""
    return {
        program: {
            "jumlah": len(members),
            "rata_rata": calculate_average([m["score"] for m in members]),
        }
        for program, members in sorted(groups.items())
    }


def create_ranking(students):
    """Ranking nilai tertinggi; nilai sama mendapat rank sama.

    Memakai sorted() sehingga list asli tidak berubah.
    """
    ordered = sorted(students, key=lambda s: (-s["score"], s["name"]))
    ranking = []
    previous_score, rank = None, 0
    for position, student in enumerate(ordered, start=1):
        if student["score"] != previous_score:
            rank = position
            previous_score = student["score"]
        ranking.append({"rank": rank, **student})
    return ranking


def summarize(students):
    """Rekapitulasi jumlah, rata-rata, min, max, dan jumlah per status."""
    if not students:
        return {
            "jumlah": 0, "rata_rata": None, "minimum": None,
            "maksimum": None, "jumlah_lulus": 0, "per_status": {},
        }
    scores = [s["score"] for s in students]
    per_status = {}
    for student in students:
        per_status[student["status"]] = per_status.get(student["status"], 0) + 1
    return {
        "jumlah": len(students),
        "rata_rata": calculate_average(scores),
        "minimum": min(scores),
        "maksimum": max(scores),
        "jumlah_lulus": sum(1 for s in students if s["status"] in PASSED_STATUS),
        "per_status": per_status,
    }


def add_student(student, students):
    """Tambah mahasiswa tanpa mutasi; tolak NIM duplikat."""
    if any(item["nim"] == student["nim"] for item in students):
        raise DuplicateNimError("NIM sudah terdaftar.")
    new_student = {
        **student,
        "status": determine_status(student["score"], student["attendance"]),
    }
    return [*students, new_student]
