import sys
import os

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import qInstallMessageHandler

from database.db_master import DatabaseManager
from gui.views.app_shell import AppShell


def qt_message_handler(msg_type, msg_log_context, msg_string):
    if "QPainter" in msg_string or "QWidgetEffectSource" in msg_string:
        return
    print(msg_string)


qInstallMessageHandler(qt_message_handler)


if __name__ == "__main__":

    # =========================
    # CROSS PLATFORM PATH
    # =========================

    # Cara aman otomatis (recommended)
    db_file = os.path.join("database", "appdata.db")
    sql_init = os.path.join("database", "sql", "init.sql")

    # Alternatif manual:
    # Linux / macOS:
    # db_file = "database/appdata.db"
    # sql_init = "database/sql/init.sql"

    # Windows:
    # db_file = r"database\appdata.db"
    # sql_init = r"database\sql\init.sql"

    # =========================
    # DATABASE INIT
    # =========================
    db = DatabaseManager(
        database_files=db_file,
        sql_script_file=sql_init
    )

    # =========================
    # QT APP
    # =========================
    app = QApplication(sys.argv)
    app.setApplicationName("Warung+")
    app.setOrganizationName("WarungPlus")

    shell = AppShell()
    shell.showMaximized()

    exit_code = app.exec()

    # Tutup DB setelah app selesai
    db.close()

    sys.exit(exit_code)