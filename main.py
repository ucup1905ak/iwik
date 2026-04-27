import argparse

from gui.app import App
from api.db_master import connect_db, init_db
from utils.generateData import generate_data
from utils.generate_profit_prediction import generate_sales_insight, calculate_moving_average


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

    generate_data()
    
    # Generate and display sales insight
    print("\n📊 Sales Prediction:")
    insight = generate_sales_insight(7)
    print(f"   {insight}")
    
    moving_avg_data = calculate_moving_average(7)
    if moving_avg_data["status"] == "success":
        print(f"   Moving Average (7 hari): Rp{moving_avg_data['moving_average']:,.0f}".replace(",", "."))
    
    print()
    app = App()
    app.mainloop()
