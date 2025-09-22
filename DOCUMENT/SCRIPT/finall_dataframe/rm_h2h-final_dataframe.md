# 📄 Dokumentacja skryptów modułu `rm_h2h`

---

## Skrypt `analyzer.py`

Główny moduł do analizy statystyk Head-to-Head (H2H) dla meczów Realu Madryt. Oblicza kompleksowe metryki historycznych starć między Realem Madryt a jego przeciwnikami. Statystyki te obejmują wyniki z ostatnich 5 spotkań, średnie punkty na mecz w całej historii oraz kursy bukmacherskie na zwycięstwo Realu Madryt.

**Główne funkcjonalności:**

- Automatyczne ładowanie danych meczowych Realu Madryt i wszystkich meczów La Liga.
- Przygotowywanie bazowego DataFrame poprzez dodanie dedykowanych kolumn na statystyki H2H.
- Obliczanie kluczowych wskaźników H2H dla każdego meczu Realu Madryt, takich jak:
  - Procent wygranych Realu Madryt w ostatnich 5 meczach H2H (`H2H_RM_W_L5`).
  - Różnica bramkowa Realu Madryt w ostatnich 5 meczach H2H (`H2H_RM_GDIF_L5`).
  - Średnie punkty na mecz Realu Madryt w ostatnich 5 meczach H2H (`H2H_PPM_L5`).
  - Średnie punkty na mecz Realu Madryt we wszystkich historycznych meczach H2H (`H2H_PPM`).
  - Wskaźnik istnienia wcześniejszych meczów H2H (`H2H_EXISTS`).
  - Odmarżowiony kurs na zwycięstwo Realu Madryt (`RM_ODD_W`).
- Wypełnianie głównego DataFrame obliczonymi statystykami H2H.
- Walidacja wyników analizy pod kątem kompletności i jakości danych.

**Proces działania:**

1. Inicjalizuje `H2HDataLoader` w celu załadowania niezbędnych danych meczowych.
2. Ustawia bazowy DataFrame (wynik poprzednich analiz) i przygotowuje go dodając puste kolumny H2H.
3. Iteruje przez mecze Realu Madryt, identyfikuje przeciwnika i datę meczu.
4. Dla każdego meczu wywołuje funkcje z `h2h_calculator.py` i `odds_calculator.py` w celu obliczenia poszczególnych statystyk H2H.
5. Agreguje obliczone statystyki i wypełnia nimi odpowiednie kolumny w DataFrame.
6. Przeprowadza walidację końcowego DataFrame za pomocą `validators.py`.
7. Zwraca kompletny DataFrame wzbogacony o szczegółowe statystyki H2H.

---

## Skrypt `config.py`

Moduł konfiguracyjny dla analizy Head-to-Head. Definiuje stałe i listy kolumn używane w całym module `rm_h2h`, zapewniając spójność i łatwość w zarządzaniu nazwami kolumn oraz identyfikatorami.

**Zdefiniowane konfiguracje:**

- `H2H_COLUMNS`: Lista nazw kolumn, które zostaną dodane do DataFrame i wypełnione statystykami H2H. Obejmuje metryki takie jak procent wygranych, różnica bramek, średnie punkty oraz kursy.
- `REQUIRED_MATCH_COLUMNS`: Lista kluczowych kolumn, które muszą być obecne w wejściowym DataFrame z danymi meczowymi, aby kalkulatory H2H działały poprawnie (np. `match_date`, `home_team_id`, `away_team_id`, `home_goals`, `away_goals`).
- `REQUIRED_ODDS_COLUMNS`: Lista kluczowych kolumn wymaganych w DataFrame przy przetwarzaniu kursów bukmacherskich (np. `match_id`, `home_odds_fair`, `away_odds_fair`).
- `REAL_MADRID_ID`: Stała definiująca unikalny identyfikator drużyny Realu Madryt (domyślnie 1), używana do filtrowania i identyfikacji meczów Realu.

---

## Skrypt `data_loader.py`

Moduł odpowiedzialny za wczytywanie i wstępne przygotowanie danych meczowych niezbędnych do przeprowadzenia analizy Head-to-Head. Klasa `H2HDataLoader` zarządza dostępem do plików CSV zawierających historię meczów Realu Madryt oraz wszystkich meczów La Liga.

**Kluczowe zadania:**

- Lokalizowanie i wczytywanie plików `RM_all_matches_stats.csv` (szczegółowe dane meczów Realu Madryt) oraz `all_matches.csv` (wszystkie mecze La Liga).
- Wykorzystanie `FileUtils` do bezpiecznego ładowania plików CSV.
- Konwersja kolumn zawierających daty (`match_date`) do formatu `datetime` w celu zapewnienia spójności.
- Przechowywanie załadowanych DataFrame'ów (`rm_matches` i `opp_matches`) jako atrybuty klasy, gotowe do użycia przez inne komponenty modułu `rm_h2h`.
- Obsługa błędów związanych z brakiem plików lub problemami podczas ich wczytywania, z odpowiednim logowaniem informacji, ostrzeżeń lub błędów.

**Funkcje klasy `H2HDataLoader`:**

- `__init__()`: Inicjalizuje puste atrybuty dla DataFrame'ów.
- `load_data()`: Główna metoda ładująca dane z plików, przeprowadzająca konwersję dat i walidację podstawową. Zwraca krotkę zawierającą DataFrame z meczami Realu Madryt i DataFrame z meczami wszystkich drużyn.

---

## Skrypt `h2h_calculator.py`

Moduł zawierający logikę obliczeniową dla statystyk Head-to-Head. Dostarcza funkcji do analizy historii bezpośrednich spotkań między Realem Madryt a danym przeciwnikiem.

**Główne funkcje:**

- `get_h2h_matches()`: Pobiera DataFrame zawierający mecze H2H między Realem Madryt a określonym przeciwnikiem, które odbyły się przed podaną datą. Umożliwia ograniczenie wyników do `last_n` ostatnich spotkań.
- `calculate_h2h_stats()`: Oblicza kompleksowe statystyki H2H na podstawie `last_n` ostatnich meczów. Zwraca słownik zawierający:
  - `win_ratio`: Procent wygranych Realu Madryt.
  - `points_per_match`: Średnie punkty zdobywane przez Real Madryt na mecz.
  - `goals_balance`: Różnica bramek Realu Madryt (gole strzelone - gole stracone).
- `calculate_h2h_overall_ppm()`: Oblicza średnie punkty na mecz zdobywane przez Real Madryt przeciwko danemu przeciwnikowi w całej dostępnej historii meczów H2H.
- `is_playing_before()`: Sprawdza, czy Real Madryt rozegrał jakiekolwiek mecze H2H z danym przeciwnikiem przed określoną datą. Zwraca `True` lub `False`.

**Cechy:**

- Wykorzystanie `REAL_MADRID_ID` z modułu `config` do identyfikacji Realu Madryt.
- Walidacja DataFrame wejściowego za pomocą funkcji z `validators.py`.
- Obsługa przypadków, gdy nie ma wcześniejszych meczów H2H (zwracanie `None` lub odpowiednich wartości domyślnych).
- Logowanie ostrzeżeń w przypadku braku danych H2H.

---

## Skrypt `odds_calculator.py`

Moduł dedykowany do pobierania i przetwarzania kursów bukmacherskich związanych z meczami Realu Madryt. Głównym celem jest dostarczenie odmarżowionego (fair) kursu na zwycięstwo Realu Madryt w konkretnym meczu.

**Główna funkcja:**

- `get_rm_odds()`: Pobiera odmarżowiony kurs na zwycięstwo Realu Madryt dla określonego `match_id`, `opp_id` i `match_date`. Funkcja identyfikuje, czy Real Madryt grał jako gospodarz czy gość, i zwraca odpowiedni kurs (`home_odds_fair` lub `away_odds_fair`).

**Kluczowe aspekty:**

- Wykorzystanie odmarżowionych kursów, które lepiej odzwierciedlają rzeczywiste prawdopodobieństwo wyniku, eliminując marżę bukmachera.
- Walidacja DataFrame wejściowego pod kątem obecności wymaganych kolumn z kursami (`REQUIRED_ODDS_COLUMNS` z `config.py`) za pomocą funkcji z `validators.py`.
- Obsługa sytuacji, gdy dane dla konkretnego meczu nie zostaną znalezione, z logowaniem błędu.
- Identyfikacja roli Realu Madryt w meczu (gospodarz/gość) na podstawie `REAL_MADRID_ID`.

---

## Skrypt `validators.py`

Moduł zawierający funkcje walidacyjne, które zapewniają integralność, kompletność i poprawność formatu danych używanych w całym module `rm_h2h`. Walidatory sprawdzają struktury DataFrame'ów, obecność wymaganych kolumn oraz jakość wyników końcowych analizy H2H.

**Główne funkcje walidacyjne:**

- `validate_h2h_dataframe()`: Sprawdza, czy DataFrame z danymi meczowymi zawiera wszystkie kolumny niezbędne do podstawowych obliczeń H2H (zdefiniowane w `REQUIRED_MATCH_COLUMNS`). Automatycznie konwertuje kolumnę `match_date` do typu `datetime64[ns]`, jeśli jest to konieczne.
- `validate_odds_dataframe()`: Weryfikuje, czy DataFrame zawiera wszystkie wymagane kolumny do analizy kursów bukmacherskich (zdefiniowane w `REQUIRED_ODDS_COLUMNS`), w szczególności kolumny z odmarżowionymi kursami.
- `validate_h2h_analysis_results()`: Przeprowadza walidację końcowego DataFrame po analizie H2H. Sprawdza kompletność dodanych kolumn H2H (z prefiksem `H2H_` oraz `RM_ODD_W`), oblicza procent brakujących wartości i generuje statystyki opisowe dla kursów Realu Madryt. Zwraca słownik z raportem walidacji.

**Cechy:**

- Wykorzystanie list wymaganych kolumn z modułu `config.py`.
- Szczegółowe logowanie błędów i ostrzeżeń, co ułatwia diagnozowanie problemów z danymi.
- Kluczowe dla zapewnienia niezawodności obliczeń w całym module `rm_h2h`.
