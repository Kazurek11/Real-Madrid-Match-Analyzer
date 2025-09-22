# 📄 Dokumentacja skryptów modułu `rm_team`

---

## Skrypt `analyzer.py`

Główny moduł do kompleksowej analizy drużyny Realu Madryt. Integruje dane dotyczące zawodników z analizą drużynową, obliczając szeroki zakres statystyk. Obejmują one dane o trenerze (ID, oceny formy), statystyki drużynowe z ostatnich meczów (gole, punkty, różnica bramek), średnie sezonowe oraz szczegółową wydajność przeciwko różnym kategoriom przeciwników (TOP, MID, LOW). Celem jest wygenerowanie kompletnego DataFrame, gotowego do dalszych analiz i modelowania predykcyjnego.

**Główne funkcjonalności:**

- Automatyczne ładowanie i przygotowywanie danych źródłowych (mecze Realu Madryt, mecze wszystkich drużyn La Liga, dane trenerów).
- Inicjalizacja specjalizowanych managerów i kalkulatorów (`CoachManager`, `StatsCalculator`, `SeasonCalculator`, `SeasonManager`).
- Ustawianie i przygotowywanie bazowego DataFrame (zazwyczaj wynik analizy na poziomie zawodników) poprzez dodanie predefiniowanych kolumn na statystyki drużynowe.
- Iteracyjne obliczanie statystyk drużynowych dla każdego meczu Realu Madryt, uwzględniając kontekst czasowy (np. statystyki z poprzedniego sezonu, ostatnich 5 meczów).
- Wypełnianie przygotowanego DataFrame obliczonymi wartościami, mapując je na podstawie `MATCH_ID`.
- Obsługa błędów i brakujących danych, z możliwością zapisu wartości `NaN` w przypadku problemów.
- Logowanie postępu i wyników analizy na różnych etapach przetwarzania.

**Proces działania:**

1. Inicjalizacja `RealMadridTeamAnalyzer` z opcjonalnym `team_id` (domyślnie 1 dla Realu Madryt).
2. Ustawienie bazowego DataFrame za pomocą metody `set_base_dataframe()`.
3. Automatyczne załadowanie danych źródłowych (`setup_data_sources()`) i inicjalizacja managerów (`setup_managers()`).
4. Przygotowanie DataFrame do analizy drużynowej poprzez dodanie nowych kolumn (`prepare_dataframe()`).
5. Obliczenie statystyk meczowych dla każdego meczu w analizowanym okresie (`calculate_match_statistics()`).
6. Wypełnienie DataFrame obliczonymi statystykami (`fill_dataframe_with_stats()`).
7. Zwrócenie finalnego DataFrame przez metodę `analyze()`, który łączy dane z poziomu zawodników i drużyny.

---

## Skrypt `coach_manager.py`

Moduł odpowiedzialny za zarządzanie danymi dotyczącymi trenerów Realu Madryt. Umożliwia pobieranie informacji o trenerze na podstawie daty meczu, ID trenera lub jego nazwiska. Jest kluczowy dla przypisania odpowiedniego trenera do każdego analizowanego meczu.

**Główne funkcje:**

- `get_coach_id_by_date()`: Zwraca ID trenera, który prowadził Real Madryt w dniu określonego meczu. Działa na podstawie przedziałów czasowych kadencji (`start_date`, `end_date`).
- `get_coach_id_by_name()`: Zwraca ID trenera na podstawie jego pełnej nazwy.
- `get_coach_name_by_id()`: Zwraca nazwisko trenera na podstawie jego ID.
- `validate_coach_exists()`: Sprawdza, czy trener o podanym ID istnieje w bazie danych trenerów, logując błąd w przypadku braku.

**Kluczowe aspekty:**

- Operuje na DataFrame z danymi trenerów, który musi zawierać kolumny: `coach_id`, `coach_name`, `start_date`, `end_date`.
- Zapewnia spójny sposób identyfikacji trenera dla każdego meczu.
- Obsługuje przypadki, gdy trener nie zostanie znaleziony dla danej daty lub ID.

---

## Skrypt `config.py`

Centralny moduł konfiguracyjny dla analizy drużyny Realu Madryt. Definiuje wszystkie stałe, listy kolumn oraz progi używane w obliczeniach statystyk drużynowych, ocen trenerów i kategoryzacji przeciwników. Ułatwia zarządzanie parametrami analizy i zapewnia spójność w całym module `rm_team`.

**Zdefiniowane konfiguracje:**

- `RM_COACH_RATING`, `RM_TEAM_RATING`, `OPP_RATING`: Wybór źródła ocen (redaktorzy 'EDI' lub użytkownicy 'USR').
- `COLUMNS_TO_ADD`: Kompletna lista nazw kolumn, które zostaną dodane do DataFrame podczas analizy drużynowej. Obejmuje statystyki trenera, formę drużyny z ostatnich 5 meczów, wydajność sezonową oraz metryki przeciwko drużynom TOP/MID/LOW.
- `WIN_POINTS`, `DRAW_POINTS`: Standardowy system punktacji w La Liga.
- `TOP_TIER_MIN_PPM`, `MID_TIER_MIN_PPM`, `MID_TIER_MAX_PPM`, `LOW_TIER_MAX_PPM`: Progi punktów na mecz (PPM) używane do kategoryzacji siły przeciwników.
- `SPECIAL_DATA`: Zarezerwowane dla przyszłych konfiguracji.
- Dokumentacja użycia wyjaśniająca sposób kategoryzacji drużyn i znaczenie generowanych kolumn.

---

## Skrypt `data_loader.py` (w module `rm_h2h`, ale używany kontekstowo)

Chociaż ten plik znajduje się w module `rm_h2h`, jego funkcjonalność ładowania danych meczowych (`RM_all_matches_stats.csv` i `all_matches.csv`) jest fundamentalna również dla modułu `rm_team`, który potrzebuje tych samych źródeł danych do analizy. `RealMadridTeamAnalyzer` bezpośrednio ładuje te pliki za pomocą `FileUtils`.

**Kluczowe zadania (w kontekście `rm_team`):**

- Dostarczenie danych meczowych Realu Madryt, które są podstawą do obliczeń statystyk drużynowych.
- Dostarczenie danych wszystkich meczów La Liga, które są wykorzystywane do analizy formy przeciwników i kontekstu ligowego (np. przy obliczaniu PPM przeciwników).

---

## Skrypt `season_calculator.py`

Moduł specjalizujący się w obliczaniu statystyk sezonowych dla drużyn La Liga, w tym Realu Madryt. Kalkuluje średnie punkty na mecz w sezonie oraz szczegółową wydajność (średnie gole i punkty) przeciwko drużynom sklasyfikowanym według ich siły (TOP, MID, LOW tier) na podstawie ich średniej liczby punktów na mecz (PPM).

**Główne funkcje:**

- `get_all_opp_matches()`: Funkcja pomocnicza pobierająca wszystkie mecze danej drużyny z pliku `all_matches.csv`.
- `calculate_team_points_per_match_season()`: Oblicza średnią liczbę punktów zdobywanych przez drużynę na mecz w poprzednim sezonie (lub od początku bieżącego sezonu, jeśli poprzedni nie istnieje w danych).
- `calculate_team_stats_against_tier()`: Generyczna funkcja obliczająca średnią liczbę goli i punktów zdobytych przez drużynę przeciwko przeciwnikom z określonego przedziału PPM.
- Specjalizowane funkcje (`calculate_team_goals_against_top`, `calculate_team_points_against_top`, itd.) opakowujące `calculate_team_stats_against_tier` dla predefiniowanych kategorii TOP, MID, LOW.

**Kluczowe aspekty:**

- Wykorzystuje `SeasonManager` (z modułu `rm_players`) do określania dat rozpoczęcia i zakończenia sezonów.
- Rozróżnia obliczenia dla Realu Madryt (korzystając z preprocesowanych danych w `rm_matches`) i innych drużyn (korzystając z `get_all_opp_matches` i surowych danych `home_goals`/`away_goals`).
- Obsługuje specjalny przypadek dla pierwszego analizowanego sezonu (2019-2020), gdzie brak jest danych z poprzedniego sezonu.
- Kategoryzuje przeciwników na podstawie progów PPM zdefiniowanych w `config.py`.

---

## Skrypt `stats_calculator.py`

Moduł odpowiedzialny za obliczanie kluczowych statystyk drużynowych i trenerskich, głównie bazujących na formie z ostatnich meczów oraz ocenach z poprzedniego sezonu.

**Główne funkcje:**

- `calculate_coach_rating_last_season()`: Oblicza średnią ocenę trenera Realu Madryt z poprzedniego sezonu na podstawie kolumny `RM_COACH_RATING`. Obsługuje przypadek pierwszego sezonu.
- `calculate_coach_rating_last_5()`: Oblicza średnią ocenę trenera Realu Madryt z ostatnich 5 rozegranych meczów przed daną datą.
- `calculate_last_5_stats()`: Główna funkcja obliczająca statystyki z ostatnich `matches_count` (domyślnie 5) meczów. Rozdziela logikę dla Realu Madryt (`_calculate_real_madrid_last_5`) i drużyn przeciwnych (`_calculate_opponent_last_5`).
  - `_calculate_real_madrid_last_5()`: Oblicza dla Realu Madryt: średnią goli strzelonych (`RM_G_SCO_L5`), straconych (`RM_G_CON_L5`), różnicę bramek (`RM_GDIF_L5`), średnią punktów na mecz (`RM_PPM_L5`) oraz średnią PPM ich przeciwników (`RM_OPP_PPM_L5`).
  - `_calculate_opponent_last_5()`: Analogiczne obliczenia dla drużyny przeciwnej, z prefiksem `OP_`.

**Kluczowe aspekty:**

- Wykorzystuje `SeasonManager` do kontekstu sezonowego.
- Bazujena danych meczowych Realu Madryt (`rm_matches`) oraz wszystkich meczów La Liga (`opp_matches`).
- Stosuje funkcje walidacyjne z `utils.py` (np. `check_NaN_column_in_RM_matches`) do zapewnienia jakości danych wejściowych.
- Loguje proces obliczeń oraz ewentualne błędy lub ostrzeżenia.

---

## Skrypt `utils.py`

Moduł zawierający funkcje pomocnicze używane w całym module `rm_team` do walidacji danych, sprawdzania typów kolumn, obsługi wartości NaN oraz modyfikacji struktur DataFrame.

**Główne funkcje:**

- `check_type_in_dataframe()`: Sprawdza typ danych w określonej kolumnie DataFrame i próbuje dokonać konwersji (np. do `datetime64[ns]`), jeśli typ jest niezgodny z oczekiwanym.
- `check_NAN_in_dataframe()`: Sprawdza, czy w danej kolumnie DataFrame występują wartości NaN.
- `check_NaN_column_in_RM_matches()`: Specjalistyczna funkcja do sprawdzania i uzupełniania wartości NaN (wartością 0) w kluczowych kolumnach DataFrame z meczami Realu Madryt.
- `add_missing_columns()`: Dodaje do DataFrame listę określonych kolumn, jeśli jeszcze nie istnieją, inicjalizując je wartościami `np.nan`.

**Kluczowe aspekty:**

- Wspiera utrzymanie spójności i poprawności danych przetwarzanych przez różne komponenty modułu.
- Ułatwia obsługę błędów i standardowe operacje na DataFrame.
- Loguje informacje o przeprowadzanych operacjach i ewentualnych problemach.
