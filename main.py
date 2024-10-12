from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text 
import asyncio
from database.sqlite_models import insert_sample_sqlite_data, insert_table_data, insert_dependency_data
from database.pydantic_models import TableCreate, DependencyCreate

app = FastAPI()

# SQLite Configuration
SQLITE_DATABASE_URL = "sqlite:///sql_explorer.db"
sqlite_engine = create_engine(SQLITE_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_root():
    return HTMLResponse(open("static/index.html").read())

# Endpoint to get all servers
@app.get("/sqlite/get_servers")
async def get_servers():
    db = SessionLocal()
    servers = db.execute(text("SELECT id, name FROM servers")).fetchall()
    return [{"id": server.id, "name": server.name} for server in servers]

# Endpoint to get all databases
@app.get("/sqlite/get_databases")
async def get_databases():
    db = SessionLocal()
    databases = db.execute(text("SELECT id, name FROM databases")).fetchall()
    return [{"id": db.id, "name": db.name} for db in databases]

# Endpoint to get all tables
@app.get("/sqlite/get_tables")
async def get_tables():
    db = SessionLocal()
    tables = db.execute(text("SELECT id, name FROM tables")).fetchall()
    return [{"id": table.id, "name": table.name} for table in tables]

# Endpoint to get all dependencies
@app.get("/sqlite/get_dependencies")
async def get_dependencies():
    db = SessionLocal()
    dependencies = db.execute(text("SELECT id, source_table_id, target_table_id FROM dependencies")).fetchall()
    return [{"id": dep.id, "source_table_id": dep.source_table_id, "target_table_id": dep.target_table_id} for dep in dependencies]

@app.get("/sqlite/get_databases/{server_id}")
async def get_databases(server_id: int):
    db = SessionLocal()
    databases = db.execute(text("SELECT id, name FROM databases WHERE server_id = :server_id"), {"server_id": server_id}).fetchall()
    return [{"id": db.id, "name": db.name} for db in databases]

@app.post("/sqlite/add_table")
async def add_table(table: TableCreate):
    return insert_table_data(table) 
    
@app.get("/sqlite/get_tables/{database_id}")
async def get_tables(database_id: int):
    db = SessionLocal()
    tables = db.execute(text("SELECT id, name FROM tables WHERE database_id = :database_id"), {"database_id": database_id}).fetchall()
    return [{"id": table.id, "name": table.name} for table in tables]

@app.post("/sqlite/add_dependency")
async def add_dependency(dependency: DependencyCreate):
    return  insert_dependency_data(dependency)

@app.get("/sqlite/dependencies")
def get_dependencies():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM dependencies")).fetchall()
        dependencies = [{"source_table_id": row.source_table_id, "target_table_id": row.target_table_id} for row in result]

        # Assuming you have a way to get node data
        nodes = db.execute(text("SELECT id, name FROM tables")).fetchall()
        node_data = [{"id": row.id, "name": row.name} for row in nodes]

        return {"nodes": node_data, "links": dependencies}
    except Exception as e:
        print(f"Error retrieving dependencies: {e}")
        return {"nodes": [], "links": []}
    finally:
        db.close()

# Search for SQLite
@app.get("/sqlite/search")
def search_sqlite_objects(query: str):
    db = SessionLocal()
    try:
        # Use text() to wrap the SQL query
        results = db.execute(text(f"SELECT * FROM tables WHERE name LIKE :query"), {'query': f'%{query}%'})
        
        # Convert the results to a list of dictionaries
        results_list = []
        for result in results.fetchall():
            result_dict = {column: value for column, value in result._mapping.items()}
            results_list.append(result_dict)

        return {"results": results_list}
    except Exception as e:
        return {"error": str(e)}  # Return the error message if an exception occurs
    finally:
        db.close()  # Ensure the database session is closed

@app.on_event("startup")
def startup_event():
    insert_sample_sqlite_data() 