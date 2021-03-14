from data import *
from database import *
import time
import sqlite3

MAX_MEASUREMENTS = 4  # Nombre maximal de mesures en base par station
BACKUP_PERIOD = 2  # Nombre de mesure après lesquelles on fait une sauvegarde

stations = [410, 307, 432]
db_name = 'wind.db'

create_database(db_name)

i = 0  # Compteur d'insertion
start_time = time.time()
while True:
    for station_id in stations:
        status_code, station, measurement = get_data(str(station_id))
        if status_code == 200:
            insert_station(db_name, station)
            insert_measurement(db_name, measurement, MAX_MEASUREMENTS)
    i += 1
    # Sauvegarde
    if i == BACKUP_PERIOD:
        # sauvegarde du fichier de la db
        source = sqlite3.connect(db_name)
        destination = sqlite3.connect('backup.db')
        source.backup(destination)
        i = 0

    time.sleep(60.0 - ((time.time() - start_time) % 60.0))
