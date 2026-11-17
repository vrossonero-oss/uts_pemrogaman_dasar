# Student Grade Manager

Aplikasi pengolahan data nilai dan kehadiran mahasiswa berbasis command line.
Dibuat untuk UTS Pemrograman Dasar (TK091), memakai Python dan standard library saja.

## Tujuan
Dosen atau admin prodi dapat membaca data mahasiswa dari file CSV/JSON, menghitung status
kelulusan, mencari dan memfilter data, membuat ranking dan rekap, lalu menyimpan hasilnya
ke JSON dan CSV.

## Cara menjalankan
Python 3.10 atau lebih baru. Dari folder proyek:

```
python main.py
python main.py --input data/students.csv --output-dir data/output
python -m unittest discover tests -v
```

Di Linux/macOS pakai `python3` jika `python` tidak dikenali. Virtual environment tidak wajib
karena tidak ada package eksternal (lihat `requirements.txt`). Jika ingin memakainya:

```
python -m venv .venv
.venv\Scripts\activate          (Windows)
source .venv/bin/activate       (macOS/Linux)
```

## Struktur program
```
uts-student-manager/
├── main.py                  # menu, input(), print(), logging
├── student_manager/         # package buatan sendiri
│   ├── __init__.py          # API package
│   ├── exceptions.py        # exception khusus
│   ├── validation.py        # validasi data
│   ├── processing.py        # status, cari, filter, grup, ranking, rekap
│   ├── file_handler.py      # baca/tulis CSV dan JSON
│   └── report.py            # pembuat teks laporan
├── data/
│   ├── students.csv         # contoh input utama
│   ├── students_kosong.csv  # edge case: hanya header
│   ├── students_rusak.csv   # error: kolom kurang
│   ├── students_rusak.json  # error: JSON rusak
│   └── output/              # hasil program (JSON, CSV, TXT)
├── tests/test_student_manager.py
├── debug/                   # skenario debugging + pembuat transkrip
├── hasil_output/            # contoh output sesi terminal dan log
├── requirements.txt
└── README.md
```

Alur dependensi: `main.py` -> `student_manager` (lewat `__init__.py`) ->
`file_handler` -> `validation` -> `exceptions`; `processing` -> `exceptions`;
`report` berdiri sendiri. Hanya `main.py` yang memakai `print()` dan `input()`.

## Format input (CSV)
Header wajib: `nim,name,program,score,attendance`

| Kolom | Aturan |
|---|---|
| nim | teks tidak kosong, hanya angka, tidak boleh duplikat |
| name | teks tidak kosong setelah strip |
| program | teks tidak kosong |
| score | bilangan bulat 0-100 (0 sah) |
| attendance | bilangan bulat 0-100 (persen) |

File `.json` berisi list of dictionary dengan kunci yang sama juga didukung.

## Aturan status (urutan prioritas)
1. kehadiran < 75 -> Peringatan Kehadiran
2. nilai >= 90 dan kehadiran >= 90 -> Lulus dengan Pujian
3. nilai >= 80 -> Lulus
4. nilai >= 60 -> Remedial
5. selain itu -> Tidak Lulus

## Fitur menu
1. Tampilkan semua mahasiswa (daftar bernomor)
2. Cari berdasarkan NIM
3. Filter berdasarkan status
4. Filter berdasarkan program studi
5. Rekap per program studi (jumlah dan rata-rata)
6. Ranking nilai (data asli tidak berubah)
7. Ringkasan statistik
8. Tambah mahasiswa (validasi, input diulang jika salah)
9. Simpan `students.json`, `laporan_nilai.csv`, `laporan_nilai.txt` ke `data/output/`
0. Keluar

## Penanganan error
- File tidak ada -> pesan jelas, program mulai dengan data kosong
- Kolom CSV kurang / JSON rusak -> `FormatDataError`, program mulai dengan data kosong
- Baris data tidak valid -> dilewati, dilaporkan beserta nomor baris
- NIM duplikat di file -> record pertama dipakai, sisanya dibuang
- Input menu/data salah -> diminta ulang, program tidak berhenti
- Data kosong -> laporan "Belum ada data." tanpa pembagian nol
- Log ke `logs/app.log` (INFO, WARNING, ERROR)

## Referensi
Modul Praktikum 1-7 TK091, dokumentasi Python (https://docs.python.org/3/),
PEP 8. Bantuan AI: lihat catatan pada lembar jawaban PDF.
