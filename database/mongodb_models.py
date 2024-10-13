from pymongo import MongoClient

MONGO_DATABASE_URL = "mongodb://localhost:27017"
client = MongoClient(MONGO_DATABASE_URL)
mongo_db = client['sql_explorer']

# Insert a new table
def insert_table_mongodb_data(table):
    # Check if the table already exists
    existing_table = mongo_db.tables.find_one({"name": table.name, "database_id": table.database_id})
    
    if existing_table:
        return {"message": "Table already exists."}

    # Insert the new table
    mongo_db.tables.insert_one({"name": table.name, "database_id": table.database_id})
    return {"message": "Table added successfully."}

# Insert a new dependency
def insert_dependency_mongodb_data(dependency):
    # Check if the dependency already exists in the MongoDB collection
    existing_dependency = mongo_db.dependencies.find_one({
        "source_table_id": dependency.source_table_id,
        "target_table_id": dependency.target_table_id
    })
    
    if existing_dependency:
        # Raise an HTTPException if the dependency already exists
        return {"message": "The dependency already exists."}

    # Insert the new dependency into the collection
    mongo_db.dependencies.insert_one({
        "source_table_id": dependency.source_table_id,
        "target_table_id": dependency.target_table_id
    })
    
    # Return a success message
    return {"message": "Dependency added successfully."}

# Insert sample MongoDB data
def insert_sample_mongodb_data():
    servers = ['Server1', 'Server2']
    databases = [('Database1', 1), ('Database2', 1), ('Database3', 2)]
    tables = [
        {'name': 'employees', 'database_id': 1},
        {'name': 'sales', 'database_id': 1},
        {'name': 'products_catalog', 'database_id': 2},
        {'name': 'clients', 'database_id': 2},
        {'name': 'payments', 'database_id': 3},
        {'name': 'stock', 'database_id': 3}
    ]
    dependencies = [
        {'source_table_id': 1, 'target_table_id': 2},
        {'source_table_id': 2, 'target_table_id': 3},
        {'source_table_id': 1, 'target_table_id': 4},
        {'source_table_id': 4, 'target_table_id': 5},
        {'source_table_id': 5, 'target_table_id': 6}
    ]

    # Insert sample servers, databases, tables, and dependencies
    if not mongo_db.servers.find_one():
        mongo_db.servers.insert_many([{"id": i+1, "name": server} for i, server in enumerate(servers)])
    if not mongo_db.databases.find_one():
        mongo_db.databases.insert_many([{"id": i+1, "name": db[0], "server_id": db[1]} for i, db in enumerate(databases)])
    if not mongo_db.tables.find_one():
        mongo_db.tables.insert_many(tables)
    if not mongo_db.dependencies.find_one():
        mongo_db.dependencies.insert_many(dependencies)
