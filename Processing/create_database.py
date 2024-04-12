import sqlite3

conn = sqlite3.connect('stats.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE IF NOT EXISTS stats
          (id INTEGER PRIMARY KEY ASC,
           number_of_thermostat_events INTEGER NOT NULL,
           number_of_lighting_events INTEGER NOT NULL,
           average_temperature FLOAT NOT NULL,
           average_light_intensity FLOAT NOT NULL,
           last_updated DATETIME NOT NULL)
          ''')

conn.commit()
conn.close()
