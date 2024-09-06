import sqlite3
import folium
import geopy
from geopy import geocoders
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

from data_load import DataBaseWork
from log_config import setup_logger

logger = setup_logger(__name__)

data_base_work = DataBaseWork()


class StationsMap():
    """
    Klasa, która grupuje metody związane z wyświetlaniem mapy i obliczaniem odległości
    od danego punktu, a także wyciąganiem najbliższych stacji. Klasa korzysta z bibliotek
    folium i geopy.
    """

    def show_station_on_map(self):
        """
        Metoda pobiera współrzędne wszystkich stacji z bazy danych i
        za pomocą biblioteki folium tworzy mapę, umieszczając znaczniki w lokalizacjach stacji.

        :return: Lista wyników zawierająca informacje o stacjach (nazwa, szerokość i długość geograficzna).
        """
        sql = 'SELECT station_name, gegr_lat, gegr_lon FROM stations'
        search_result = data_base_work.db_operations(sql)
        latitude, longitude = float(search_result[0][1]), float(search_result[0][2])
        zoom_level = 6  # Dostosuj poziom powiększenia według własnych preferencji
        map = folium.Map(location=(latitude, longitude), zoom_start=zoom_level)
        for point in search_result:
            name, lat, lon = point
            lat, lon = float(lat), float(lon)
            marker = folium.Marker(location=(lat, lon), popup=name)
            marker.add_to(map)
        map.save('map.html')
        return search_result

    def show_station_on_map_by_distance(self, location, distance_point):
        """
        Metoda, która na podstawie podanego punktu na mapie i zasięgu w kilometrach,
        pokazuje stacje znajdujące się w tym zasięgu.

        :param location: Punkt startowy, z którego mierzymy odległość.
        :param distance_point: Zasięg w kilometrach, w obrębie którego szukamy stacji.
        :return: Lista stacji, które znajdują się w określonym zasięgu od podanego punktu.
        :raises: Logowanie błędów w przypadku problemów z lokalizacją lub obliczeniami.
        """
        try:
            geolocator = Nominatim(user_agent="myGeocoder")
            location_check = geolocator.geocode(location)
            if location_check is not None:
                location_check = (location_check.latitude, location_check.longitude)
            else:
                pass
        except (ValueError, AttributeError) as e:
            logger.info(f"Błąd lokalizacji: {e}")
            return []

        sql = 'SELECT gegr_lat, gegr_lon, station_name, stations_id, city_name FROM stations'
        search_result = data_base_work.db_operations(sql)
        try:
            point1 = location_check
            locations = []
            for i in search_result:
                point2 = (i[0], i[1])
                distance = geodesic(point1, point2)
                locations.append(distance.kilometers)

            result_km = []
            for index, x in enumerate(locations):
                if x <= distance_point:
                    result_km.append(search_result[index][2:5])
        except TypeError as te:
            logger.info(f"Błąd obliczeń: {te}")
            return []

        return result_km
