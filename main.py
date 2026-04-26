from gui.app import App
from api.db_master import *
if __name__ == "__main__":
    connect_db("abc.db")
    init_db("abc.db", r"sql\init.sql")
    app = App()
    app.mainloop()

    
    
