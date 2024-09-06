import unittest
from unittest.mock import MagicMock, patch
from data_load import DataBaseWork


class TestDataBaseWork(unittest.TestCase):
    @patch('sqlite3.connect')  # Mockuj sqlite3.connect
    def test_db_operations(self, mock_connect):
        """
        Testuje metodę `db_operations` klasy `DataBaseWork`.

        Metoda ta sprawdza, czy `db_operations` prawidłowo wykonuje zapytania SQL
        oraz zwraca oczekiwane wyniki.

        Parametry
        ----------
        mock_connect : unittest.mock.MagicMock
            Mock dla funkcji `sqlite3.connect`, używany do testowania bez rzeczywistego połączenia z bazą danych.

        Sprawdzane aspekty
        ------------------
        - Czy metoda `cursor.execute()` została wywołana z odpowiednimi argumentami.
        - Czy metoda `cursor.fetchall()` została wywołana.
        - Czy wynik zwrócony przez `db_operations` jest zgodny z oczekiwanym wynikiem.
        """
        # Utwórz instancję klasy
        db_work = DataBaseWork()

        # Przygotuj mocka dla kursora
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value.cursor.return_value = mock_cursor

        # Przygotuj dane do testu
        sql = "SELECT * FROM test_table WHERE id=?"
        values = (1,)
        mock_cursor.fetchall.return_value = [(1, 'test')]

        # Wywołaj metodę
        result = db_work.db_operations(sql, values)

        # Sprawdź, czy metoda cursor.execute() została wywołana z odpowiednimi argumentami
        mock_cursor.execute.assert_called_once_with(sql, values)
        # Sprawdź, czy metoda cursor.fetchall() została wywołana
        mock_cursor.fetchall.assert_called_once()
        # Sprawdź, czy wynik jest zgodny z oczekiwanym
        self.assertEqual(result, [(1, 'test')])


if __name__ == '__main__':
    unittest.main()
