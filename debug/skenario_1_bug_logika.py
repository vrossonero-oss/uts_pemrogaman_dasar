"""Skenario debugging 1: bug logika tanpa exception (if not score)."""


def label_nilai_bug(score):
    if not score:                      # BUG: 0 dianggap kosong
        return "Belum ada nilai"
    return "Ada nilai"


def label_nilai_fix(score):
    return "Belum ada nilai" if score is None else "Ada nilai"


for value in (None, 0, 80):
    print(f"score={value!r:5} bug -> {label_nilai_bug(value):16} fix -> {label_nilai_fix(value)}")
