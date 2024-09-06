import requests

from log_config import setup_logger

logger = setup_logger(__name__)

def api_connecting(api_url):
    """
    Funkcja do nawiązywania połączenia z określonym API.

    Funkcja ta przyjmuje URL do API jako zmienną i próbuje nawiązać z nim połączenie.
    Obsługuje różne kody odpowiedzi HTTP oraz błędy związane z połączeniem.

    Parameters
    ----------
    api_url : str
        URL API, z którym ma być nawiązane połączenie.

    Returns
    -------
    response : requests.Response
        Obiekt odpowiedzi z serwera, jeśli połączenie było udane.

    Raises
    ------
    requests.exceptions.RequestException
        W przypadku wystąpienia błędów związanych z żądaniem HTTP.

    """
    try:
        response = requests.get(api_url, timeout=1800)
        if response.status_code == 400:
            logger.info("Bad Request: Serwer nie mógł zrozumieć żądania z powodu nieprawidłowej składni.")
        elif response.status_code == 401:
            logger.info("Unauthorized: Brak autoryzacji do wykonania żądania.")
        elif response.status_code == 500:
            logger.info("Internal Server Error: Serwer napotkał błąd podczas przetwarzania żądania.")
        else:
            response.raise_for_status()

        return response

    except requests.exceptions.ConnectTimeout:
        logger.info("Timeout: Przekroczono limit czasu połączenia.")
    except requests.exceptions.ConnectionError:
        logger.info("Błąd sieciowy: Problemy z połączeniem (błąd DNS, odmowa połączenia, itp.)")
    except requests.exceptions.URLRequired:
        logger.info("URLRequired: Wymagany jest prawidłowy URL do wykonania żądania.")
    except requests.exceptions.TooManyRedirects:
        logger.info("TooManyRedirects: Zbyt wiele przekierowań.")
