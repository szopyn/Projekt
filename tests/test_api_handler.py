import unittest
import requests
from api_handler import api_connecting



class TestApiConnecting(unittest.TestCase):
    """
    Klasa testowa dla funkcji `api_connecting` z modułu `api_handler`.

    Testy sprawdzają, czy funkcja `api_connecting` prawidłowo obsługuje
    poprawne i niepoprawne adresy URL API.
    """

    def test_valid_api_url(self):
        """
        Testuje funkcję `api_connecting` dla poprawnego adresu URL API.

        Sprawdza, czy funkcja `api_connecting` prawidłowo zwraca odpowiedź
        o statusie 200 (OK) dla poprawnego adresu URL API.

        Parametry
        ----------
        brak
        """
        api_url = 'https://api.gios.gov.pl/pjp-api/rest/station/findAll'
        result_test = api_connecting(api_url)
        self.assertEqual(result_test.status_code, 200)

    def test_unvalid_api_url(self):
        """
        Testuje funkcję `api_connecting` dla niepoprawnego adresu URL API.

        Sprawdza, czy funkcja `api_connecting` podnosi wyjątek `requests.exceptions.HTTPError`
        dla niepoprawnego adresu URL API, który zwraca błąd HTTP.

        Parametry
        ----------
        brak
        """
        api_url = 'https://api.gios.gov.pl/pjp-api/rest/station/findAlll'
        with self.assertRaises(requests.exceptions.HTTPError):
            api_connecting(api_url)

if __name__ == '__main__':
    unittest.main()
