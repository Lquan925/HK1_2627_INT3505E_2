"""Run A/B/C against an isolated database; preserve the user's books.db."""
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PORT = 5054


def main():
    os.chdir(ROOT)
    REPORTS.mkdir(exist_ok=True)
    env = dict(os.environ, PYTHONUTF8="1", LAB_FAIL_RATE="0.01")
    database = REPORTS / "lab4-test.db"
    for label, users, rate, duration in [("A", 10, 2, "30s"), ("B", 50, 5, "60s"), ("C", 200, 50, "30s")]:
        # The same snapshot before every scenario avoids cumulative data growth.
        with sqlite3.connect(ROOT / "instance/books.db") as source:
            with sqlite3.connect(database) as target:
                source.backup(target)
        server_code = (
            "from app import create_app; "
            f"app=create_app({{'SQLALCHEMY_DATABASE_URI': {('sqlite:///' + database.as_posix())!r}}}); "
            f"app.run(host='127.0.0.1', port={PORT}, debug=False, use_reloader=False)"
        )
        with (REPORTS / f"{label}-server.log").open("w", encoding="utf-8") as server_log:
            server = subprocess.Popen([sys.executable, "-X", "utf8", "-c", server_code], stdout=server_log, stderr=subprocess.STDOUT, env=env)
            try:
                for attempt in range(100):
                    if server.poll() is not None:
                        raise RuntimeError(f"Server exited; inspect {label}-server.log")
                    try:
                        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1) as response:
                            if response.status == 200:
                                break
                    except OSError:
                        time.sleep(0.1)
                else:
                    raise RuntimeError("Server did not become ready")
                args = [sys.executable, "-X", "utf8", "-m", "locust", "-f", "performance/locustfile.py", "--headless", "-H", f"http://127.0.0.1:{PORT}", "-u", str(users), "-r", str(rate), "-t", duration, "--html", f"reports/{label}.html", "--csv", f"reports/{label}"]
                print(f"Running {label}: {users} users, {duration}", flush=True)
                with (REPORTS / f"{label}-locust.log").open("w", encoding="utf-8") as log:
                    result = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, env=env)
                if result.returncode not in (0, 1) or not (REPORTS / f"{label}_stats.csv").exists():
                    raise RuntimeError(f"Locust failed; inspect {label}-locust.log")
                print(f"Finished {label}, exit={result.returncode} (1 is expected with injected failures)", flush=True)
            finally:
                server.terminate()
                server.wait(timeout=10)


if __name__ == "__main__":
    main()
