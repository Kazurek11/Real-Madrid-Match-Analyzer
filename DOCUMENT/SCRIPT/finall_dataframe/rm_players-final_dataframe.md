# Tworzenie koncowego DataSetu I

## Opis aktualnych skryptów w folderze ***rm_players***

---

### Skrypt `data_loader.py`

Skrypt odpowiedzialny za załadowanie wszystkich datasetów w formie CSV wykorzystywanych podczas budowy finalnego datasetu. Zapewnia spójny sposób odczytywania danych z plików oraz ich wstępne przetwarzanie.

**Funkcje:**

- Wczytywanie plików CSV różnych formatów
- Podstawowa walidacja danych
- Obsługa błędów podczas ładowania plików

---

### Skrypt `player_manager.py`

Główny moduł do zarządzania danymi o zawodnikach. Pozwala na pobieranie informacji na podstawie ID zawodnika lub jego nazwy.

**Zastosowanie:**

- Centralne źródło danych o graczach
- Eliminacja duplikacji kodu
- Uproszczony dostęp do danych zawodników
- Wykorzystywany przez inne moduły systemu

---

### Skrypt `season_manager.py`

Moduł specjalizujący się w zarządzaniu danymi sezonowymi. Klasyfikuje i dostarcza informacje o sezonach na podstawie dat.

**Cechy:**

- Analogiczna struktura do player_manager.py
- Automatyczna klasyfikacja sezonów
- Spójny interfejs dla danych sezonowych

---

### Skrypt `statistic_calculator.py`

Rdzeń systemu odpowiedzialny za obliczenia statystyczne i tworzenie finalnego zbioru danych.

**Funkcjonalności:**

- Integracja z pozostałymi modułami
- Obliczanie statystyk meczowych i sezonowych
- Elastyczny system parametrów
- Mechanizmy awaryjne dla brakujących danych
- Generowanie ujednoliconych wyników

**Działanie:**

1. Pobiera dane z modułów player_manager i season_manager
2. Wykonuje obliczenia statystyczne
3. Przygotowuje dane wyjściowe

---

### Skrypt `data_agregator.py`

Moduł łączący funkcjonalność wszystkich pozostałych skryptów w kompletny pipeline przetwarzania danych.

**Proces:**

1. Wykorzystuje logikę z statistic_calculator.py
2. Agreguje dane z różnych źródeł
3. Zapisuje wyniki zgodnie ze schematem kolumn
4. Zapewnia spójność z wymaganiami systemu
