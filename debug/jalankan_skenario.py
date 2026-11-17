"""Menjalankan main.py dengan input terskrip dan mencetak input ke layar,
supaya hasil_output/ terbaca seperti sesi terminal sungguhan.

Pemakaian: python debug/jalankan_skenario.py "1,2,2301003,0" [--input file]
"""
import builtins
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
answers = iter(sys.argv[1].split(","))
sys.argv = ["main.py"] + sys.argv[2:]


def fake_input(prompt=""):
    try:
        value = next(answers)
    except StopIteration:
        raise EOFError from None
    print(f"{prompt}{value}")
    return value


builtins.input = fake_input
runpy.run_path(str(root / "main.py"), run_name="__main__")
