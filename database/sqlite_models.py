from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


SQLALCHEMY_DATABASE_URL = "sqlite:///sql_explorer.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

class Server(Base):
    __tablename__ = "servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Database(Base):
    __tablename__ = "databases"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    server_id = Column(Integer, ForeignKey("servers.id"))

class Table(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    database_id = Column(Integer, ForeignKey("databases.id"))

class Dependency(Base):
    __tablename__ = "dependencies"
    id = Column(Integer, primary_key=True, index=True)
    source_table_id = Column(Integer, ForeignKey("tables.id"))
    target_table_id = Column(Integer, ForeignKey("tables.id"))

# Create the SQLite database
def init_sqlite_db(database_url: str):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

init_sqlite_db(SQLALCHEMY_DATABASE_URL)
# Insert sample data

def insert_table_data(table: Table):
    db = SessionLocal()
    # Check if the table already exists
    existing_table = db.execute(
        text("SELECT * FROM tables WHERE name = :name AND database_id = :database_id"),
        {"name": table.name, "database_id": table.database_id}
    ).fetchone()

    if existing_table:
        return {"message": "Table already exists."}

    # Insert the new table
    db.execute(
        text("INSERT INTO tables (name, database_id) VALUES (:name, :database_id)"),
        {"name": table.name, "database_id": table.database_id}
    )
    db.commit()
    return {"message": "Table added successfully."}

def insert_sample_sqlite_data():
    db = SessionLocal()
    try:
        # Insert sample data into servers if they don't exist
        servers = ['Server1', 'Server2']
        for server in servers:
            result = db.execute(text("SELECT COUNT(*) FROM servers WHERE name = :name"), {"name": server}).fetchone()
            if result[0] == 0:  # If count is 0, then insert
                db.execute(text("INSERT INTO servers (name) VALUES (:name)"), {"name": server})

        # Insert sample data into databases if they don't exist
        databases = [('Database1', 1), ('Database2', 1), ('Database3', 2)]
        for db_name, server_id in databases:
            result = db.execute(text("SELECT COUNT(*) FROM databases WHERE name = :name AND server_id = :server_id"),
                                {"name": db_name, "server_id": server_id}).fetchone()
            if result[0] == 0:  # If count is 0, then insert
                db.execute(text("INSERT INTO databases (name, server_id) VALUES (:name, :server_id)"),
                           {"name": db_name, "server_id": server_id})

        # Insert sample data into tables if they don't exist
        tables = [
            ('users', 1), 
            ('orders', 1), 
            ('products', 2), 
            ('customers', 2), 
            ('transactions', 3), 
            ('inventory', 3)
        ]
        for table_name, database_id in tables:
            result = db.execute(text("SELECT COUNT(*) FROM tables WHERE name = :name AND database_id = :database_id"),
                                {"name": table_name, "database_id": database_id}).fetchone()
            if result[0] == 0:  # If count is 0, then insert
                db.execute(text("INSERT INTO tables (name, database_id) VALUES (:name, :database_id)"),
                           {"name": table_name, "database_id": database_id})

        # Insert sample dependencies
        dependencies = [
            (1, 2),  # users -> orders
            (2, 3),  # orders -> products
            (1, 4),  # users -> customers
            (4, 5),  # customers -> transactions
            (5, 6)   # transactions -> inventory
        ]
        for source_table_id, target_table_id in dependencies:
            result = db.execute(text("SELECT COUNT(*) FROM dependencies WHERE source_table_id = :source_id AND target_table_id = :target_id"),
                                {"source_id": source_table_id, "target_id": target_table_id}).fetchone()
            if result[0] == 0:  # If count is 0, then insert
                db.execute(text("INSERT INTO dependencies (source_table_id, target_table_id) VALUES (:source_id, :target_id)"),
                           {"source_id": source_table_id, "target_id": target_table_id})

        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
