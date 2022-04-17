from sqlalchemy import create_engine
from .transaction import process_data

def append_table(path, db_settings, table_name="test"):
    df = process_data(path)
    engine = create_engine(f'mysql+pymysql://{db_settings["user"]}:{db_settings["password"]}\
@localhost:3306/{db_settings["db"]}')
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    print("Write to MySQL successfully!")