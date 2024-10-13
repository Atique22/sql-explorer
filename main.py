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

from database.mongodb_models import mongo_db 
from pymongo import MongoClient
from database.mongodb_models import insert_sample_mongodb_data, insert_table_mongodb_data, insert_dependency_mongodb_data


# MongoDB Configuration
MONGO_DATABASE_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_DATABASE_URL)
mongo_db = client['sql_explorer']


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

# @app.on_event("startup")
# def startup_event():
#     insert_sample_sqlite_data() 





# Endpoint to get all servers
@app.get("/mongodb/get_servers")
async def get_servers():
    servers = list(mongo_db.servers.find({}, {"_id": 0, "id": 1, "name": 1}))
    return servers

# Endpoint to get all databases
@app.get("/mongodb/get_databases")
async def get_databases():
    databases = list(mongo_db.databases.find({}, {"_id": 0, "id": 1, "name": 1}))
    return databases

# Endpoint to get all tables
@app.get("/mongodb/get_tables")
async def get_tables():
    tables = list(mongo_db.tables.find({}, {"_id": 0, "id": 1, "name": 1}))
    return tables

# Endpoint to get all dependencies
@app.get("/mongodb/get_dependencies")
async def get_dependencies():
    dependencies = list(mongo_db.dependencies.find({}, {"_id": 0, "source_table_id": 1, "target_table_id": 1}))
    return dependencies

@app.get("/mongodb/dependencies")
async def get_mongodb_dependencies():
    try:
        # Fetch dependencies from MongoDB
        dependencies_collection = mongo_db["dependencies"]
        dependencies = list(dependencies_collection.find())

        # Fetch tables (nodes) from MongoDB
        tables_collection = mongo_db["tables"]
        nodes = list(tables_collection.find())

        # Convert dependencies and nodes to the required format, including stringifying ObjectId
        dependencies_data = [{"source_table_id": str(dep["source_table_id"]), "target_table_id": str(dep["target_table_id"])} for dep in dependencies]
        nodes_data = [{"id": str(node["_id"]), "name": node["name"]} for node in nodes]

        return {"nodes": nodes_data, "links": dependencies_data}
    except Exception as e:
        return {"error": str(e)}

# Get databases for a specific server
@app.get("/mongodb/get_databases/{server_id}")
async def get_databases(server_id: int):
    databases = list(mongo_db.databases.find({"server_id": server_id}, {"_id": 0, "id": 1, "name": 1}))
    return databases

# Add a new table
@app.post("/mongodb/add_table")
async def add_table(table: TableCreate):
    return insert_table_mongodb_data(table)

# Get tables for a specific database
@app.get("/mongodb/get_tables/{database_id}")
async def get_tables(database_id: int):
    tables = list(mongo_db.tables.find({"database_id": database_id}, {"_id": 0, "id": 1, "name": 1}))
    return tables

# Add a new dependency
@app.post("/mongodb/add_dependency")
async def add_dependency(dependency: DependencyCreate):
    return insert_dependency_mongodb_data
    
# Search for MongoDB objects
@app.get("/mongodb/search")
async def search_mongodb(query: str = None):
    try:
        if not query:
            # Return all tables if no query is provided
            results = mongo_db["tables"].find()
        else:
            # Perform search query on MongoDB if query is provided
            results = mongo_db["tables"].find({"name": {"$regex": query, "$options": "i"}})

        # Convert MongoDB ObjectId to string for JSON serialization
        search_results = []
        for result in results:
            result["_id"] = str(result["_id"])  # Convert ObjectId to string
            search_results.append(result)

        return {"results": search_results}
    except Exception as e:
        return {"error": str(e)}



@app.on_event("startup")
def startup_event():
    insert_sample_mongodb_data()
    insert_sample_sqlite_data() 