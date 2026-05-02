import argparse
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QtMsgType, qInstallMessageHandler

from database.db_master import connect_db, init_db
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

    db_file = "database/dev_data.db" if args.dev else "database/appdata.db"
    connect_db(db_file)
    
    init_db(db_file, r"database\sql\init.sql")

    # generate_data()
    
    # Generate and display sales insight
    # print("\n📊 Sales Prediction:")
    # insight = generate_sales_insight(7)
    # print(f"   {insight}")
    
    # moving_avg_data = calculate_moving_average(7)
    # if moving_avg_data["status"] == "success":
    #     print(f"   Moving Average (7 hari): Rp{moving_avg_data['moving_average']:,.0f}".replace(",", "."))
    
    app = QApplication(sys.argv)
    app.setApplicationName("Warung+")
    app.setOrganizationName("WarungPlus")

    shell = AppShell()
    shell.showMaximized()

    sys.exit(app.exec())
