import logging
import os
import datetime as dt
from typing import Optional, Union
class Logger:
    """
    Klasa do obsługi logowania w aplikacji.
    Umożliwia zapisywanie komunikatów do pliku i/lub konsoli,
    z różnymi poziomami ważności informacji.
    """
    
    LEVELS = {
        "DEBUG": logging.DEBUG,        # Szczegółowe informacje
        "INFO": logging.INFO,          # Potwierdzenie, że wszystko działa jak powinno
        "WARNING": logging.WARNING,    # Wskazanie na potencjalny problem (program nadal działa)
        "ERROR": logging.ERROR,        # Poważny problem, program nie mógł wykonać jakiejś funkcji
        "CRITICAL": logging.CRITICAL   # Bardzo poważny błąd, program może przestać działać
    }
    
    def __init__(self, 
                 name: str = "PYTHON_REAL", 
                 level: str = "INFO", 
                 log_file: Optional[str] = None,
                 console_output: bool = False):
        """
        Inicjalizacja loggera.
        
        Args:
            name: Nazwa loggera
            level: Poziom logowania (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Ścieżka do pliku, do którego będą zapisywane logi
            console_output: Czy wyświetlać logi w konsoli (domyślnie False)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVELS.get(level.upper(), logging.INFO))
        
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if log_file:
            log_dir = os.path.dirname(os.path.abspath(log_file))
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Loguje komunikat na poziomie DEBUG"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Loguje komunikat na poziomie INFO"""
        self.logger.info(message)
        print(f"INFO: {message}")
    
    def warning(self, message: str):
        """Loguje komunikat na poziomie WARNING"""
        self.logger.warning(message)
        print(f"WARNING: {message}")
    
    def error(self, message: str):
        """Loguje komunikat na poziomie ERROR"""
        self.logger.error(message)
        print(f"ERROR: {message}")
    
    def critical(self, message: str):
        """Loguje komunikat na poziomie CRITICAL"""
        self.logger.critical(message)
        print(f"CRITICAL: {message}")
    
    def set_level(self, level: str):
        """Zmienia poziom logowania"""
        if level.upper() in self.LEVELS:
            self.logger.setLevel(self.LEVELS[level.upper()])
            print(f"Ustawiono poziom logowania: {level}")
    
    @staticmethod
    def get_default_logger(level: str = "INFO") -> 'Logger':
        """
        Tworzy i zwraca domyślny logger dla aplikacji.
        
        Args:
            level: Poziom logowania (domyślnie INFO)
            
        Returns:
            Instancja Logger z domyślnymi ustawieniami
        """
        from src.helpers.file_utils import FileUtils  
        log_dir = os.path.join(FileUtils.get_project_root(),"src", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        today = dt.datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"python_real_{today}.log")
        
        return Logger(level=level, log_file=log_file, console_output=False)

default_logger = Logger.get_default_logger()

def debug(message: str):
    default_logger.debug(message)

def info(message: str):
    default_logger.info(message)

def warning(message: str):
    default_logger.warning(message)

def error(message: str):
    default_logger.error(message)

def critical(message: str):
    default_logger.critical(message)

def set_level(level: str):
    default_logger.set_level(level)

# Przykład użycia:
if __name__ == "__main__":
    debug("To jest wiadomość debugowania - widoczna tylko gdy poziom to DEBUG")
    info("To jest informacja")
    warning("To jest ostrzeżenie")
    error("To jest błąd")
    critical("To jest błąd krytyczny")
    
    # Zmiana poziomu logowania
    set_level("DEBUG")
    debug("Teraz wiadomości debugowania są widoczne")