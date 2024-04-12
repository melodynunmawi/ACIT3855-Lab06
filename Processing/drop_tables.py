import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('stats.sqlite')
c = conn.cursor()

# Drop the 'stats' table if it exists
try:
    c.execute('DROP TABLE stats')
    print("Table 'stats' dropped successfully.")
except sqlite3.OperationalError as e:
    print(f"Error occurred: {e}. Likely the 'stats' table does not exist, which is fine.")

# Create the 'stats' table
c.execute('''
    CREATE TABLE IF NOT EXISTS stats
    (id INTEGER PRIMARY KEY ASC,
     number_of_thermostat_events INTEGER NOT NULL,
     number_of_lighting_events INTEGER NOT NULL,
     average_temperature FLOAT NOT NULL,
     average_light_intensity FLOAT NOT NULL,
     last_updated DATETIME NOT NULL)
''')

print("Table 'stats' created or already exists.")

# Commit changes and close connection
conn.commit()
conn.close()
