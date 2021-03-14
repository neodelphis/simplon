# Récupération des données d'un anémomètre pioupiou
import requests


def get_data(pioupiou_id):
    response = requests.get("http://api.pioupiou.fr/v1/live/" + pioupiou_id)
    status_code = response.status_code  # Code d'état http du serveur, 200 = OK
    pioupiou = response.json()

    # Données de la station de mesure
    station_id = pioupiou["data"]["id"]
    latitude = pioupiou["data"]["location"]["latitude"]
    longitude = pioupiou["data"]["location"]["longitude"]
    station = (station_id, latitude, longitude)

    # Mesure
    date_time = pioupiou["data"]["measurements"]["date"]
    wind_heading = pioupiou["data"]["measurements"]["wind_heading"]
    wind_speed_avg = pioupiou["data"]["measurements"]["wind_speed_avg"]
    wind_speed_max = pioupiou["data"]["measurements"]["wind_speed_max"]
    wind_speed_min = pioupiou["data"]["measurements"]["wind_speed_min"]
    measurement = (date_time, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station_id)

    return status_code, station, measurement


def test():
    """Test de la récupération des données d'un anémomètre pioupiou
    """
    status_code, station, measurement = get_data("307")
    station_id, latitude, longitude = station
    date_time, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station_id = measurement

    print("Code réponse web de l'anémomètre {}".format(status_code))

    print("Station de mesure pioupiou: ")
    print("\tstation_id : ", station_id)
    print("\tlatitude : ", latitude)
    print("\tlongitude : ", longitude)

    print("Mesure : ")
    print("\tdate : ", date_time)
    print("\twind_heading : ", wind_heading)
    print("\twind_speed_avg : ", wind_speed_avg)
    print("\twind_speed_max : ", wind_speed_max)
    print("\twind_speed_min : ", wind_speed_min)
    print("\tstation_id : ", station_id)


# Lorsque le fichier est appelé directement on exécute la fonction de test
if __name__ == "__main__":
    test()
