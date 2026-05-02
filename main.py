
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QtMsgType, qInstallMessageHandler

from database.db_master import DatabaseManager
from utils.generateData import generate_data
from utils.generate_profit_prediction import generate_sales_insight, calculate_moving_average
from gui.views.app_shell import AppShell

# Custom message handler to suppress known Qt warnings about painter conflicts
# These occur due to graphics effects + SVG rendering interaction at Qt level
def qt_message_handler(msg_type, msg_log_context, msg_string):
    if "QPainter" in msg_string or "QWidgetEffectSource" in msg_string:
        return  # Suppress these known benign warnings
    # Print other messages normally
    print(msg_string)

qInstallMessageHandler(qt_message_handler)


if __name__ == "__main__":


    db_file = "database/appdata.db"
    sql_init = r"database\sql\init.sql"
    db = DatabaseManager(database_files=db_file, sql_script_file=sql_init)
  

    app = QApplication(sys.argv)
    app.setApplicationName("Warung+")
    app.setOrganizationName("WarungPlus")

    shell = AppShell()
    shell.showMaximized()

    sys.exit(app.exec())

    db.close()