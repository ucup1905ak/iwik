import argparse

from gui.app import App
from api.db_master import connect_db, init_db


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="IWIK GUI Launcher")
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.dev:
        print("[DEV] Development mode enabled")

    db_file = "dev_data.db" if args.dev else "appdata.db"
    connect_db(db_file)
    init_db(db_file, r"sql\init.sql")

    app = App()
    app.mainloop()

    
    
