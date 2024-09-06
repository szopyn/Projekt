import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from unidecode import unidecode

from config import date_range_list, km_list
from stations import StationInfo
from station_map import StationsMap
from data_load import DataBaseWork
from log_config import setup_logger

# Inicjalizacja loggera
logger = setup_logger(__name__)

# Inicjalizacja obiektów
station_info = StationInfo()
stations_map = StationsMap()
data_base_work = DataBaseWork()

# Ustawienia strony Streamlit
st.set_page_config(
    page_title="Aplikacja Jakości Powietrza",
    page_icon="🌍",
    layout="wide",  # Lub "centered"
    initial_sidebar_state="expanded"  # Lub "collapsed"
)

# Wczytaj plik HTML z mapą
with open("map.html", "r", encoding="utf-8") as file:
    map_html = file.read()

# Ustawienia tytułu i układu
st.title("Aplikacja Jakości Powietrza")
main_container = st.container()
col1, col2 = main_container.columns([1, 1])

# Ustawienie kolumn w pasku bocznym
with st.sidebar:
    st.sidebar.title("Filtracja danych")
    radio_value = st.sidebar.radio(
        "Wybierz sposób wyszukiwania danych",
        ["Lista miast", "Szukaj miasta", "Punkt odległości"]
    )

def sensor_filtr(sensors_mesure):
    """
    Funkcja filtrująca dane sensorów według wybranego parametru i zakresu dat.

    Parameters
    ----------
    sensors_mesure : list
        Lista danych sensorów do filtrowania.

    """
    if sensors_mesure:
        parameters = [i[2] for i in sensors_mesure]
        selected_parameters = st.sidebar.selectbox("Wybierz parametr", parameters)
        if selected_parameters:
            selected_parameter_index = parameters.index(selected_parameters)
            parameters_id = sensors_mesure[selected_parameter_index][0]
            parameters_data = station_info.sensors_data_by_sensors_db(parameters_id)
            if len(parameters_data) == 0:
                st.sidebar.write("Brak danych dla tego sensora")
            else:
                df = pd.DataFrame(parameters_data,
                                  columns=['Kolumna 1', 'Kolumna 2', 'Kolumna 3', 'Kolumna 4'])
                df = df.loc[:, ['Kolumna 3', 'Kolumna 4']].rename(
                    columns={'Kolumna 3': 'Data', 'Kolumna 4': 'Wartość'})
                date_range = st.sidebar.selectbox("Wybierz zakres dat", date_range_list)
                current_date = pd.Timestamp.now()
                delta = pd.Timedelta(days=date_range)
                result_date = current_date - delta
                result_date_str = result_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    df = df.loc[df['Data'] > result_date_str]
                    if df.empty:
                        st.sidebar.write("Brak danych w tym okresie")
                    else:
                        with col1:
                            st.write("Dane tabelaryczne.")
                            st.dataframe(df, width=500, height=800)
                        with col2:
                            st.write("Wykresy i dane mapowe.")
                            average_value = df['Wartość'].mean()
                            max_value_index = df['Wartość'].idxmax()
                            min_value_index = df['Wartość'].idxmin()
                            max_value = df.loc[max_value_index, 'Wartość']
                            min_value = df.loc[min_value_index, 'Wartość']
                            max_date = df.loc[max_value_index, 'Data']
                            min_date = df.loc[min_value_index, 'Data']
                            avg_string = f"Średnia wartość: {average_value:.2f}"
                            max_string = f"Najwyższa wartość: {max_value:.2f} w {max_date}"
                            min_string = f"Najniższa wartość: {min_value:.2f} w {min_date}"
                            st.write(avg_string, "-", max_string, "-", min_string)
                            x = np.arange(len(df))
                            y = df["Wartość"]
                            coefficients = np.polyfit(x, y, 1)
                            trend_line = np.poly1d(coefficients)
                            df["Trend"] = trend_line(x)
                            st.line_chart(df.set_index("Data"))
                        with col2:
                            csv = df.to_csv()
                            st.download_button(
                                label="Pobierz dane CSV",
                                data=csv,
                                file_name='dane.csv',
                                mime='text/csv'
                            )
                except (ValueError, TypeError) as error:
                    logger.info("Błąd: %s", error)

def station_filtr(stations):
    """
    Funkcja filtrująca dane stacji według wybranego parametru.

    Parameters
    ----------
    stations : list
        Lista stacji do filtrowania.

    """
    station_list = [i[1] for i in stations]
    stations_id = {i[1]: i[2] for i in stations}
    selected_station = st.sidebar.selectbox("Wybierz stację", station_list)
    if station_list:
        stations_id = stations_id[selected_station]
        sensors_mesure = station_info.sensors_list_by_station_all_db(stations_id)
        sensor_filtr(sensors_mesure)

# Wybór miasta
if radio_value == "Szukaj miasta":
    city_name = st.sidebar.text_input("Znajdź stacje w podanym mieście")
    stations = station_info.station_list_by_city_user_db(city_name)
    if stations:
        st.sidebar.write("Stacje pomiarowe w mieście:")
        station_filtr(stations)
    else:
        if city_name == "":
            pass
        else:
            st.sidebar.write("Miasto nie istnieje")

# Lista miast
if radio_value == "Lista miast":
    city_list = station_info.station_list_by_city_all_db()
    city_list = sorted([i[0] for i in city_list], key=lambda city_list: unidecode(city_list))
    city_list = st.sidebar.selectbox("Wybierz miasto:", city_list)
    if city_list and radio_value == "Lista miast":
        stations = station_info.station_list_by_city_user_db(city_list)
        station_filtr(stations)
else:
    pass

# Punkt odległości
if radio_value == "Punkt odległości":
    point_chose = st.sidebar.text_input("Znajdź stacje w danym punkcie")
    km = st.sidebar.selectbox("Kilometry", km_list)
    if point_chose:
        try:
            station_list_point = stations_map.show_station_on_map_by_distance(point_chose, km)
            station_list_point_list = {i[0]: i[1] for i in station_list_point}
            select_point_stations = st.sidebar.selectbox("Wybierz stację według punktu odległości",
                                                         station_list_point_list)
            stations_id = station_list_point_list[select_point_stations]
            sensors_mesure = station_info.sensors_list_by_station_all_db(stations_id)
            sensor_filtr(sensors_mesure)
        except (ValueError, TypeError, KeyError) as error:
            logger.info(f"Lokalizacja nie znaleziona: {point_chose}")
    else:
        pass

# Dodaj mapę
with col2:
    components.html(map_html, width=800, height=600)

# Przyciski na dole
with st.sidebar:
    update_button = st.button("Zaktualizuj dane")
    show_map_button = st.button('Pokaż dane na mapie')
    if update_button:
        data_base_work.initial_payment_getData()
        st.sidebar.success("Dane zostały zaktualizowane!")
