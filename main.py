
import sys

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


    db_file = "database/appdata.db"
    sql_init = r"database\sql\init.sql"


    # Ini kelas pembungkus untuk semua akses Datasbase. Bisa dilihat di database.db_master
    db = DatabaseManager(database_files=db_file, sql_script_file=sql_init)
  

    app = QApplication(sys.argv)
    app.setApplicationName("Warung+")
    app.setOrganizationName("WarungPlus")

    shell = AppShell()
    shell.showMaximized()

    sys.exit(app.exec())

    db.close()