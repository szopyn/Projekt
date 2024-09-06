import requests
import json
import sqlite3
import time

from config import db_name
from api_handler import api_connecting
from log_config import setup_logger

logger = setup_logger(__name__)

class DataBaseWork:
    """
    Zbiór funkcji do pracy z bazą danych, obejmujący nawiązywanie połączenia,
    wykonywanie zapytań oraz szereg działań, takich jak inicjalne ładowanie danych.
    """

    def db_operations(self, sql, values=None):
        """
        Wykonuje operacje na bazie danych, takie jak zapytania SELECT lub INSERT.

        Parametry
        ----------
        sql : str
            Zapytanie SQL do wykonania.
        values : tuple, opcjonalnie
            Wartości do podstawienia w zapytaniu SQL. Domyślnie None.

        Zwraca
        -------
        search_result : list
            Lista wyników zapytania SELECT lub pusty wynik dla operacji INSERT.
        """
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                if values:
                    cursor.execute(sql, values)
                else:
                    cursor.execute(sql)
                search_result = cursor.fetchall()
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print("Błąd bazy danych:", e)
            search_result = []
        return search_result

    def db_operations_many(self, sql, values=None):
        """
        Wykonuje operacje na bazie danych z wieloma wartościami, takie jak wsadowe INSERT.

        Parametry
        ----------
        sql : str
            Zapytanie SQL do wykonania.
        values : list of tuples, opcjonalnie
            Lista krotek wartości do podstawienia w zapytaniu SQL. Domyślnie None.
        """
        try:
            with sqlite3.connect(db_name) as conn:
                cursor = conn.cursor()
                if values:
                    cursor.executemany(sql, values)
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print("Błąd bazy danych:", e)

    def db_create(self):
        """
        Tworzy trzy określone tabele w bazie danych: 'sensors', 'sensors_data', i 'stations'.
        """
        try:
            sql1 = '''CREATE TABLE "sensors" (
                   "sensor_id" INT,
                   "stations_id" INT,
                   "param_name" VARCHAR(255),
                   "param_formula" VARCHAR(20),
                   "param_code" VARCHAR(20),
                   "param_id" INT,
                   UNIQUE(sensor_id, stations_id, param_name, param_formula, param_code, param_id))'''
            sql2 = '''CREATE TABLE "sensors_data" (
                   "sensor_id" INT,
                   "key" VARCHAR(20),
                   "date" datetime,
                   "value" INT,
                   UNIQUE(sensor_id, key, date, value))'''
            sql3 = '''CREATE TABLE "stations" (
                   "stations_id" INT,
                   "station_name" VARCHAR(255),
                   "gegr_lat" VARCHAR(20),
                   "gegr_lon" VARCHAR(20),
                   "city_id" INT,
                   "city_name" VARCHAR(255),
                   "commune_name" VARCHAR(255),
                   "district_name" VARCHAR(255),
                   "province_name" VARCHAR(255),
                   "address_street" VARCHAR(255),
                   UNIQUE(stations_id, station_name, gegr_lat, gegr_lon, city_id, city_name,
                   commune_name, district_name, province_name, address_street))'''
            sql = [sql1, sql2, sql3]
            for i in sql:
                self.db_operations(i)
        except (sqlite3.OperationalError, sqlite3.Error) as e:
            print("Błąd bazy danych:", e)

    def initial_payment_stations(self):
        """
        Wywołuje API 'station/findAll' w celu pobrania danych o stacjach i zapisuje je w tabeli 'stations'.
        """
        api_url = 'https://api.gios.gov.pl/pjp-api/rest/station/findAll'
        response = api_connecting(api_url)
        data = response.json()
        for station in data:
            city = station['city']
            commune = city['commune']
            sql = '''INSERT OR IGNORE INTO stations
                     (stations_id, station_name, gegr_lat, gegr_lon, city_id,
                      city_name, commune_name, district_name,
                      province_name, address_street)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
            values = (station['id'], station['stationName'], station['gegrLat'],
                      station['gegrLon'], city['id'], city['name'],
                      commune['communeName'], commune['districtName'],
                      commune['provinceName'], station['addressStreet'])
            self.db_operations(sql, values)

    def initial_payment_sensors(self):
        """
        Wywołuje API 'station/findAll' w celu pobrania ID stacji, a następnie
        używa tych ID do wywołania API 'station/sensors/' w celu pobrania danych o czujnikach i zapisuje je w tabeli 'sensors'.
        """
        api_url = 'https://api.gios.gov.pl/pjp-api/rest/station/findAll'
        response = api_connecting(api_url)
        data = response.json()
        ids = [station['id'] for station in data]
        sensors_data = []
        for i in ids:
            api_url = f'https://api.gios.gov.pl/pjp-api/rest/station/sensors/{i}'
            response = api_connecting(api_url)
            data = response.json()
            sensors_data.append(data)
            for sensor in data:
                sql = '''INSERT OR IGNORE INTO sensors
                         (sensor_id, stations_id, param_name, param_formula, param_code, param_id)
                         VALUES (?, ?, ?, ?, ?, ?)'''
                values = (sensor['id'], sensor['stationId'], sensor['param']['paramName'],
                          sensor['param']['paramFormula'], sensor['param']['paramCode'], sensor['param']['idParam'])
                self.db_operations(sql, values)

    def initial_payment_getData(self):
        """
        Wywołuje API 'station/findAll' w celu pobrania ID stacji, następnie
        używa tych ID do wywołania API 'station/sensors/' w celu pobrania ID czujników,
        a następnie używa tych ID do wywołania API 'data/getData/' w celu pobrania danych czujników i zapisuje je w tabeli 'sensors_data'.
        """
        # Początek pomiaru czasu dla wywołań API
        start_time_api = time.time()

        api_url = 'https://api.gios.gov.pl/pjp-api/rest/station/findAll'
        response = api_connecting(api_url)
        data = response.json()
        ids = [station['id'] for station in data]
        api_url = 'https://api.gios.gov.pl/pjp-api/rest/station/sensors/'
        sensors_data = [requests.get(api_url + str(i)).json() for i in ids]
        ids_sensors = [s['id'] for lst in sensors_data for s in lst]
        api_url = 'https://api.gios.gov.pl/pjp-api/rest/data/getData/'
        sensors_data = [{'sensor_id': i, 'data': api_connecting(api_url + str(i)).json()} for i in ids_sensors]

        # Koniec pomiaru czasu dla wywołań API i obliczanie czasu trwania
        end_time_api = time.time()
        elapsed_time_api = end_time_api - start_time_api
        logger.info(f"Czas trwania wywołań API: {elapsed_time_api} sekund")

        sensors_data_null = []
        for dictionary in sensors_data:
            if dictionary.get("data").get("values") is None:
                for value in dictionary["data"].get("values", []):
                    if value.get("value") is None:
                        sensors_data_null.append(dictionary)
                        sensors_data.remove(dictionary)

        blank = []
        for i in sensors_data:
            sensor_id = i['sensor_id']
            data = i['data']
            key = data['key']
            if data['values'] is not None:
                for value in data['values']:
                    date = value['date']
                    value = value['value']
                    # Tylko wstawianie wierszy z nie-nullowymi wartościami
                    if value is not None:
                        sql = "INSERT OR IGNORE INTO sensors_data " \
                              "(sensor_id, key, date, value) VALUES (?, ?, ?, ?)"
                        values = (sensor_id, key, date, value)
                        blank.append(values)

        # Początek pomiaru czasu dla operacji DB
        start_time_db = time.time()

        self.db_operations_many(sql, blank)

        # Koniec pomiaru czasu dla operacji DB i obliczanie czasu trwania
        end_time_db = time.time()
        elapsed_time_db = end_time_db - start_time_db
        logger.info(f"Czas trwania operacji DB: {elapsed_time_db} sekund")
