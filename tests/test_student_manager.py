"""Uji dasar: normal, kasus batas, dan error. Jalankan: python -m unittest discover tests -v"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from student_manager import (  # noqa: E402
    DataMahasiswaError, DuplicateNimError, FormatDataError, NamaKosongError,
    add_status, add_student, calculate_average, create_ranking,
    determine_status, get_unique_programs, load_students, parse_int,
    remove_duplicates, search_by_nim, summarize, validate_student,
)

VALID = {"nim": "1", "name": "Andi", "program": "TK", "score": 85, "attendance": 92}


class TestStatus(unittest.TestCase):
    def test_priority_attendance_first(self):
        self.assertEqual(determine_status(88, 70), "Peringatan Kehadiran")

    def test_boundaries(self):
        self.assertEqual(determine_status(90, 90), "Lulus dengan Pujian")
        self.assertEqual(determine_status(90, 89), "Lulus")
        self.assertEqual(determine_status(80, 75), "Lulus")
        self.assertEqual(determine_status(79, 75), "Remedial")
        self.assertEqual(determine_status(60, 75), "Remedial")
        self.assertEqual(determine_status(59, 75), "Tidak Lulus")

    def test_zero_score_is_valid(self):
        self.assertEqual(determine_status(0, 80), "Tidak Lulus")


class TestValidation(unittest.TestCase):
    def test_valid_student_is_stripped(self):
        raw = {**VALID, "name": "  Andi "}
        self.assertEqual(validate_student(raw)["name"], "Andi")

    def test_zero_accepted(self):
        self.assertEqual(validate_student({**VALID, "score": 0})["score"], 0)

    def test_rejects_bad_values(self):
        for bad in (101, -1, True, None, "abc", ""):
            with self.assertRaises(DataMahasiswaError, msg=repr(bad)):
                validate_student({**VALID, "score": bad})

    def test_empty_name_custom_error(self):
        with self.assertRaises(NamaKosongError):
            validate_student({**VALID, "name": "   "})

    def test_parse_int_message(self):
        with self.assertRaises(DataMahasiswaError):
            parse_int("abc", "Nilai")


class TestProcessing(unittest.TestCase):
    def setUp(self):
        raw = [
            VALID,
            {**VALID, "nim": "2", "name": "Budi", "program": "IF", "score": 72, "attendance": 81},
            {**VALID, "nim": "3", "name": "Citra", "score": 92, "attendance": 95},
        ]
        self.students = add_status(raw)

    def test_average_empty_is_none(self):
        self.assertIsNone(calculate_average([]))

    def test_unique_programs_is_set(self):
        self.assertEqual(get_unique_programs(self.students), {"TK", "IF"})

    def test_remove_duplicates(self):
        unique, dup = remove_duplicates(self.students + [self.students[0]])
        self.assertEqual((len(unique), len(dup)), (3, 1))

    def test_search(self):
        self.assertEqual(search_by_nim(self.students, "2")["name"], "Budi")
        self.assertIsNone(search_by_nim(self.students, "999"))

    def test_ranking_does_not_mutate(self):
        before = [s["nim"] for s in self.students]
        ranking = create_ranking(self.students)
        self.assertEqual(ranking[0]["name"], "Citra")
        self.assertEqual([s["nim"] for s in self.students], before)

    def test_ranking_ties_share_rank(self):
        tied = add_status([VALID, {**VALID, "nim": "9", "name": "Zed"}])
        self.assertEqual([r["rank"] for r in create_ranking(tied)], [1, 1])

    def test_summary_empty_no_division_error(self):
        self.assertEqual(summarize([])["jumlah"], 0)

    def test_add_student_no_mutation_and_duplicate(self):
        new = add_student({**VALID, "nim": "7"}, self.students)
        self.assertEqual((len(self.students), len(new)), (3, 4))
        with self.assertRaises(DuplicateNimError):
            add_student(VALID, self.students)


class TestFiles(unittest.TestCase):
    def write(self, name, text):
        path = Path(self.tmp.name) / name
        path.write_text(text, encoding="utf-8")
        return path

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_students(Path(self.tmp.name) / "tidak_ada.csv")

    def test_missing_column(self):
        path = self.write("a.csv", "nim,name\n1,Andi\n")
        with self.assertRaises(FormatDataError):
            load_students(path)

    def test_bad_json(self):
        path = self.write("a.json", '[{"nim": "1"')
        with self.assertRaises(FormatDataError):
            load_students(path)

    def test_invalid_rows_collected(self):
        path = self.write("a.csv", "nim,name,program,score,attendance\n1,Andi,TK,85,92\n2,Budi,TK,abc,90\n")
        valid, errors = load_students(path)
        self.assertEqual((len(valid), len(errors)), (1, 1))
        self.assertEqual(errors[0][0], 3)


if __name__ == "__main__":
    unittest.main()
