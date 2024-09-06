from data_load import DataBaseWork

data_base_work = DataBaseWork()


class StationInfo():
    """
    Klasa do zarządzania informacjami o stacjach, informacje są pobierane z bazy danych.
    """

    def station_list_by_city_user_db(self, city_name):
        """
        Pobiera listę nazw stacji i adresów z bazy danych SQLite na podstawie podanej nazwy miasta.

        :param city_name: Nazwa miasta, dla którego chcemy pobrać stacje.
        :return: Lista stacji z danymi: nazwa miasta, adres ulica, ID stacji.
        """
        sql = "SELECT city_name, address_street, stations_id FROM stations WHERE city_name = ?"
        data_base_work = DataBaseWork()
        search_result = data_base_work.db_operations(sql, (city_name,))
        return search_result

    def station_list_by_city_all_db(self):
        """
        Pobiera listę wszystkich miast z bazy danych.

        :return: Lista unikalnych nazw miast.
        """
        sql = 'SELECT DISTINCT(city_name) FROM stations'
        search_result = data_base_work.db_operations(sql)
        return search_result

    def sensors_list_by_station_all_db(self, stations_id):
        """
        Pobiera listę wszystkich czujników dla wybranej stacji z bazy danych.

        :param stations_id: ID stacji, dla której chcemy pobrać czujniki.
        :return: Lista czujników dla danej stacji.
        :raises: Print "Sensors list empty error." jeśli brak czujników dla danej stacji.
        """
        sql = "SELECT * FROM sensors WHERE stations_id = ?"
        data_base_work = DataBaseWork()
        search_result = data_base_work.db_operations(sql, (stations_id,))
        if not search_result:
            print("Błąd: lista czujników jest pusta.")
        return search_result

    def sensors_data_by_sensors_db(self, sensor_id):
        """
        Pobiera dane czujnika na podstawie podanego ID czujnika z bazy danych.

        :param sensor_id: ID czujnika, dla którego chcemy pobrać dane.
        :return: Lista danych dla podanego czujnika.
        :raises: Print "No data for this sensor" jeśli brak danych dla danego czujnika.
        """
        sql = "SELECT * FROM sensors_data WHERE sensor_id = ?"
        data_base_work = DataBaseWork()
        search_result = data_base_work.db_operations(sql, (sensor_id,))
        if not search_result:
            print("Brak danych dla tego czujnika.")
        return search_result

    def sensors_data_by_stations_db(self, stations_id):
        """
        Pobiera dane wszystkich czujników dla podanej stacji z bazy danych.

        :param stations_id: ID stacji, dla której chcemy pobrać dane czujników.
        :return: Lista danych czujników dla danej stacji.
        :raises: Print "No data for this sensor" jeśli brak danych dla czujników danej stacji.
        """
        sql = """SELECT * FROM sensors_data AS sd
                 INNER JOIN sensors AS s ON sd.sensor_id = s.sensor_id
                 INNER JOIN stations AS st ON st.stations_id = s.stations_id
                 WHERE st.stations_id = ?"""
        data_base_work = DataBaseWork()
        search_result = data_base_work.db_operations(sql, (stations_id,))
        if not search_result:
            print("Brak danych dla czujników tej stacji.")
        return search_result
