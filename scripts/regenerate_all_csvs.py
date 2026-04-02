import os
import glob
import shutil
from datetime import datetime
import subprocess
import sys

ROOT = os.getcwd()
CSV_DIR = os.path.join(ROOT, "csv_new")


def archive_csvs():
    csv_files = glob.glob(os.path.join(CSV_DIR, "*.csv"))
    if not csv_files:
        print("No CSV files found to archive in", CSV_DIR)
        return None

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(CSV_DIR, f"archive_{ts}")
    os.makedirs(archive_dir, exist_ok=True)

    moved = 0
    for f in csv_files:
        # skip any archive folders accidentally matching pattern
        if os.path.isdir(f):
            continue
        try:
            shutil.move(f, archive_dir)
            moved += 1
        except Exception as e:
            print("Failed to move", f, e)

    print(f"Archived {moved} CSV files to: {archive_dir}")
    return archive_dir


def run_generator():
    py = sys.executable or "python"
    script = os.path.join(ROOT, "scripts", "generate_csvs_from_repo.py")
    if not os.path.exists(script):
        print("Generator script not found:", script)
        return 1
    cmd = [py, script]
    print("Running generator:", " ".join(cmd))
    try:
        res = subprocess.run(cmd, check=False)
        print("Generator exited with code", res.returncode)
        return res.returncode
    except Exception as e:
        print("Failed to run generator:", e)
        return 2


if __name__ == '__main__':
    print("Archiving existing CSVs and regenerating all CSVs...")
    archive_dir = archive_csvs()
    code = run_generator()
    if code == 0:
        print("Regeneration completed successfully.")
    else:
        print("Regeneration finished with code:", code)
