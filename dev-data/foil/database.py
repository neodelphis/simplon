# Création et manipulation de la base de données SQLite
import sqlite3
import os


def create_database(db_name):
    """ Création de la base de données SQLite db_name
    """
    conn = sqlite3.connect(db_name)
    # Autorisation des clefs externes sur la base
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    # Création de la table `station`
    c.execute('''CREATE TABLE IF NOT EXISTS station
                (id INTEGER PRIMARY KEY,
                latitude REAL,
                longitude REAL)
                ''')

    # Création de la table `measurement`
    c.execute('''CREATE TABLE IF NOT EXISTS measurement
                (date_time TEXT,
                wind_heading REAL,
                wind_speed_avg REAL,
                wind_speed_max REAL,
                wind_speed_min REAL,
                station_id INTEGER,
                FOREIGN KEY (station_id) REFERENCES station(id),
                PRIMARY KEY (date_time, station_id))
                ''')

    # commit changes to db
    conn.commit()
    # close connection
    conn.close()
    return True


def insert_station(db_name, station):
    """Insertion d'une nouvelle station
    """
    station_id, latitude, longitude = station

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Vérification que la station n'est pas déjà présente
    c.execute("SELECT * FROM station WHERE id=?", (station_id,))  # usage de `?` important pour éviter les injections SQL
    station_exists = c.fetchone()
    if not station_exists:
        c.execute("INSERT INTO station VALUES (?,?,?)", station)
    conn.commit()
    conn.close()


def insert_measurement(db_name, measurement, MAX_MEASUREMENTS):
    """ Insertion d'une nouvelle mesure
    """
    date_time, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station_id = measurement

    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Vérification que la mesure associée à une date et à une station n'est pas déjà présente
    # (Option possible avec un test d'insertion sur la clé primaire)
    c.execute("SELECT * FROM measurement WHERE date_time=? AND station_id=?", (date_time, station_id))
    measurement_exists = c.fetchone()
    if not measurement_exists:
        # Vérification qu'il n'y ai pas plus de MAX_MEASUREMENTS-1 déjà présentes en base
        measurements_check_max(c, station_id, MAX_MEASUREMENTS)

        c.execute("INSERT INTO measurement VALUES (?,?,?,?,?,?)", measurement)

    conn.commit()
    conn.close()


def measurements_check_max(c, station_id, MAX_MEASUREMENTS):
    """ Vérification qu'il n'y ai pas plus de MAX_MEASUREMENTS-1 déjà présentes en base
        On récupère tous les enregistrements pour une station classés par ordre ascendant selon `date_time`
    """
    c.execute("SELECT * FROM measurement WHERE station_id=? ORDER BY datetime(date_time) ASC", (station_id,))
    measurements_for_station = c.fetchall()
    measurements_count = len(measurements_for_station)
    if measurements_count >= MAX_MEASUREMENTS:
        # Suppression les anciennes valeurs
        for measurement_to_be_deleted in measurements_for_station[:measurements_count - MAX_MEASUREMENTS + 1]:
            date_time_tbd, _, _, _, _, station_id_tbd = measurement_to_be_deleted
            c.execute("DELETE FROM measurement WHERE date_time=? AND station_id=?", (date_time_tbd, station_id_tbd))


def test():
    """Test de la création et manipulation de la base de données SQLite
    """
    db_name = 'wind.db'
    MAX_MEASUREMENTS = 2

    # Supression des tables
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS station;")
    c.execute("DROP TABLE IF EXISTS measurement;")

    conn.commit()
    conn.close()

    # Création des tables
    create_database(db_name)

    # Insertion d'une nouvelle station
    station_id = 110
    latitude = 51.36846
    longitude = 3.458852
    station = (station_id, latitude, longitude)
    insert_station(db_name, station)

    # Vérification de l'insertion
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM station;")
    assert c.fetchall() == [(110, 51.36846, 3.458852)], "Problème lors de l'insertion de la station"
    print("OK Insertion station")
    conn.commit()
    conn.close()

    # Insertion d'une nouvelle mesure
    date_time = "2015-08-17T22:07:27.000Z"
    wind_heading = 292.5
    wind_speed_avg = 14
    wind_speed_max = 22.5
    wind_speed_min = 7
    measurement = (date_time, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station_id)
    insert_measurement(db_name, measurement, MAX_MEASUREMENTS)

    # Vérification de l'insertion
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM measurement;")
    # print(c.fetchall())
    assert c.fetchall() == [('2015-08-17T22:07:27.000Z', 292.5, 14.0, 22.5, 7.0, 110)], "Problème lors de l'insertion de la mesure"
    print("OK Insertion mesure")
    conn.commit()
    conn.close()

    # Insertion de mesures pour une station telles que le nombre de mesures en base soit > MAX_MEASUREMENTS
    date_times = ["2015-08-17T22:07:28.000Z", "2015-08-17T22:07:29.000Z"]
    for date_time in date_times:
        measurement = (date_time, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station_id)
        insert_measurement(db_name, measurement, MAX_MEASUREMENTS)

    # Vérification que le nombre de mesures en base ne soit > MAX_MEASUREMENTS
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT * FROM measurement;")
    # print(c.fetchall())
    assert c.fetchall() == [('2015-08-17T22:07:28.000Z', 292.5, 14.0, 22.5, 7.0, 110), ('2015-08-17T22:07:29.000Z', 292.5, 14.0, 22.5, 7.0, 110)],\
        "Problème lors de la vérification du nombre maximum de mesures par station en base"
    print("OK Vérification du nombre maximum de mesures par station en base")
    conn.commit()
    conn.close()

    # Suppression éventuelle du fichier contenant la db
    delete = None
    while (delete is not 'Y') and (delete is not 'n'):
        delete = input("Supprimer le fichier wind.db après vérification? Y/[n]") or 'n'
    if delete is 'Y':
        os.remove(db_name)


# Lorsque le fichier est appelé directement on exécute la fonction de test
if __name__ == "__main__":
    test()
