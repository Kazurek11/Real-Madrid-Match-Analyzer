# Opis aktualnych skryptów w folderze ***help_script***

## Skrypt `logger.py`

Skrypt ten odpowiada za obsługę logowania w całej aplikacji. Umożliwia zapisywanie komunikatów o różnych poziomach ważności (DEBUG, INFO, WARNING, ERROR, CRITICAL) zarówno do pliku, jak i opcjonalnie do konsoli. Pozwala na łatwą zmianę poziomu logowania w trakcie działania programu oraz automatycznie tworzy katalog na logi, jeśli nie istnieje. Dzięki temu wszystkie ważne zdarzenia, ostrzeżenia i błędy są rejestrowane i mogą być później analizowane. Skrypt udostępnia funkcje pomocnicze (`info`, `warning`, `error`, `debug`, `critical`, `set_level`) do wygodnego logowania z innych modułów.

---

## Skrypt `file_utils.py`

Skrypt ten zawiera klasę `FileUtils`, która dostarcza narzędzi do zarządzania plikami i operacji na plikach CSV. Umożliwia m.in. bezpieczne wczytywanie i zapisywanie plików CSV z obsługą błędów, sprawdzanie istnienia plików i katalogów, pobieranie wszystkich plików z wybranego katalogu oraz tworzenie katalogów na wyniki. Dzięki temu obsługa plików w projekcie jest ustandaryzowana i odporna na typowe błędy związane z operacjami wejścia-wyjścia. Skrypt pozwala także na łatwe ustalanie ścieżek do katalogu projektu i katalogów wynikowych.
