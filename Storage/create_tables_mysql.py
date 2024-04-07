import mysql.connector

# db_conn = mysql.connector.connect(
#     host="localhost",
#     user="root",  # Adjust user as needed
#     password="Passw0rd",  # Adjust password as needed
#     database="smart_home"  # Adjust database as needed
# )

db_conn = mysql.connector.connect(host="acit4850-group10.westus3.cloudapp.azure.com", user="root", password="password", database="events")
db_cursor = db_conn.cursor()
db_cursor.execute('''
        CREATE TABLE thermostat_event
        (id INT NOT NULL AUTO_INCREMENT,
        trace_id VARCHAR(50) NOT NULL,
        temperature FLOAT NOT NULL,
        status VARCHAR(50) NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        date_created DATETIME NOT NULL,
        PRIMARY KEY (id))
        ''')
db_cursor.execute('''
        CREATE TABLE lighting_event
        (id INT NOT NULL AUTO_INCREMENT,
        trace_id VARCHAR(50) NOT NULL,
        intensity FLOAT NOT NULL,
        status VARCHAR(50) NOT NULL,
        timestamp VARCHAR(100) NOT NULL,
        date_created DATETIME NOT NULL,
        PRIMARY KEY (id))
        ''')
db_conn.commit()
db_conn.close()
