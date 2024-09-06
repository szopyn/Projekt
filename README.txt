# Projekt: Air Quality Monitoring

## Opis

Projekt "Air Quality Monitoring" to aplikacja, która łączy się z publicznym API,
pobiera dane dotyczące stacji monitorowania jakości powietrza oraz czujników,
następnie zapisuje te dane do lokalnej bazy danych SQLite.
Aplikacja umożliwia wyświetlanie lokalizacji stacji na mapie,
obliczanie odległości od podanego punktu oraz zarządzanie danymi stacji i czujników.

## Instalacja

1. **Klonowanie repozytorium**

   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo

2. Tworzenie i aktywowanie środowiska wirtualnego

Na Windows:

python -m venv venv
venv\Scripts\activate

Na macOS/Linux:

python3 -m venv venv
source venv/bin/activate

3. Instalacja wymaganych bibliotek

Zainstaluj wszystkie potrzebne biblioteki z pliku requirements.txt:

pip install -r requirements.txt

2. Uruchamianie

W terminalu, przejdź do katalogu, w którym znajduje się plik app.py, i uruchom aplikację Streamlit za pomocą poniższego polecenia:

streamlit run app.py

To polecenie uruchomi lokalny serwer Streamlit i otworzy aplikację w domyślnym przeglądarki internetowej.

3. Uruchamianie testów:

pip install requests pytest

Możesz uruchomić testy, przechodząc do katalogu głównego projektu i używając poniższego polecenia:

pytest
