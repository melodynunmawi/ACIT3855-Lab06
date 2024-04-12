import mysql.connector

# conn = mysql.connector.connect(host="127.0.0.1", user="user", password="Password", database="smart_home")

# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",  # Adjust user as needed
#     password="Passw0rd",  # Adjust password as needed
#     database="smart_home"  # Adjust database as needed
# )
conn = mysql.connector.connect(host="acit4850-group10.westus3.cloudapp.azure.com", user="root", password="password", database="events")

c = conn.cursor()

c.execute('''
          DROP TABLE IF EXISTS thermostat_event, lighting_event          
          ''')

conn.commit()
conn.close()