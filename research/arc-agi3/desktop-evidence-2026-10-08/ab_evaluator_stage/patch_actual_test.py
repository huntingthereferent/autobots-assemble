from pathlib import Path
p=Path(r"C:\Users\teepa\continuity-live\network\tests\test_arc_native_observer.py")
s=p.read_text(encoding="utf-8")
s=s.replace("        old_color = int(before.frame[-1][36 * 64 + 36])\n", "        import numpy as np\n        old_color = int(np.asarray(before.frame[-1]).reshape(-1)[36 * 64 + 36])\n")
s=s.replace("        new_color = int(after.frame[-1][36 * 64 + 36])\n", "        new_color = int(np.asarray(after.frame[-1]).reshape(-1)[36 * 64 + 36])\n")
p.write_text(s,encoding="utf-8")
print("patched_test")
