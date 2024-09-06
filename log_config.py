import logging
import logging.handlers

def setup_logger(name):
    """
    Konfiguruje logger z określoną nazwą, który wysyła logi do usługi Papertrail.

    Logger jest ustawiony na poziom INFO, a logi są formatowane jako:
    'nazwa loggera' - 'poziom logowania' - 'wiadomość logu'.

    Parametry
    ----------
    name : str
        Nazwa loggera.

    Zwraca
    -------
    logger : logging.Logger
        Instancja loggera, który wysyła logi do usługi Papertrail.

    Przykłady
    --------
    >>> logger = setup_logger("my_app")
    >>> logger.info("To jest log informacyjny.")
    """
    # Tworzenie loggera
    logger = logging.getLogger(name)

    # Ustawienie poziomu logowania
    logger.setLevel(logging.INFO)

    # Tworzenie handlera, który wysyła logi do Papertrail
    handler = logging.handlers.SysLogHandler(address=('logs3.papertrailapp.com', 34215))

    # Ustawienie formatu logu
    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Dodanie handlera do loggera
    logger.addHandler(handler)

    return logger
