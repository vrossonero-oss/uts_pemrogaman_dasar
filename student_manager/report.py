"""Pembuat teks laporan. Hanya mengembalikan string."""


def format_student_line(number, student):
    return (
        f"{number}. {student['nim']} | {student['name']} | {student['program']} "
        f"| {student['score']} | {student['attendance']}% | {student['status']}"
    )


def create_report(students):
    if not students:
        return "Belum ada data."
    return "\n".join(
        format_student_line(number, s) for number, s in enumerate(students, start=1)
    )


def create_ranking_text(ranking):
    if not ranking:
        return "Belum ada data."
    return "\n".join(
        f"Rank {r['rank']}: {r['name']} - {r['score']} ({r['program']})"
        for r in ranking
    )


def create_summary_text(summary):
    if summary["jumlah"] == 0:
        return "Belum ada data."
    lines = [
        f"Jumlah: {summary['jumlah']}",
        f"Rata-rata: {summary['rata_rata']:.2f}",
        f"Minimum: {summary['minimum']} | Maksimum: {summary['maksimum']}",
        f"Lulus (termasuk pujian): {summary['jumlah_lulus']}",
    ]
    lines += [f"  {status}: {total}" for status, total in summary["per_status"].items()]
    return "\n".join(lines)


def create_group_text(group_summary):
    if not group_summary:
        return "Belum ada data."
    return "\n".join(
        f"{program}: {info['jumlah']} mahasiswa, rata-rata {info['rata_rata']:.2f}"
        for program, info in group_summary.items()
    )
