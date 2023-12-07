<h1 align="center">CS 257 Database System Principles</h1>
<h1 align="center">SQL Query Optimizer</h1>

## Instructions & Installation:

1. Install Yarn and NodeJS.

2. Frontend Setup: In /frontend, run yarn install for dependencies.

3. Backend Setup: Install Python 3.8+ and Poetry (pip install poetry). In /api, run poetry install for Python packages, using   Flask.

4. Database Configuration:
Host: localhost
Database Name: TPC-H
User: postgres
Password: postgres
Port: 5432

5. PostgreSQL & TPC-H Dataset: Use pgAdmin to create a postgres user. Initialize tables and constraints in the database with psql -U postgres -f dss.ddl TPC-H - The commands will initialize empty tables in the database and psql -U postgres -f dss.ri TPC-H - This command will create the constraints on the tables, including initializing the primary keys and foreign keys on the various tables. Import CSV files into each table via pgAdmin. CSVs are available at the provided link.
https://drive.google.com/drive/folders/14sreSkDvA5myz_vSBukSR2ZPMwMNM2pc

6. Running the Application: From the root folder, run yarn start to launch both the API server and frontend client.

## Team & Roles in the project :
1.  Geethika Vadlamudi 	
 • Query Execution Plan and Generation
 • Generating multiple Query Plan Executions and costs involved in it
 • UI of the application using React


 2. Pavan Myana 
• UI of the application using React 
• Ensuring smooth flow between frontend ,backend and database 
• Visualization and natural language explanation of optimal QEP 

3. Sai Bhargav Vallabhaneni 
• Tables creation and referential integrity relation on tables 
• Connecting Flask to Database 
• Data Ingestion and query preprocessing