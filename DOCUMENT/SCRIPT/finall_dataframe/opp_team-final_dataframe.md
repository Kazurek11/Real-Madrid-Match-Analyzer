# 📄 Dokumentacja skryptów modułu `opp_team`

---

## Skrypt `analyzer.py`

Główny moduł do analizy statystyk drużyn przeciwników Realu Madryt. Oblicza kompleksowe metryki formy, statystyki sezonowe, wydajność przeciwko różnym poziomom drużyn oraz kursy bukmacherskie dla każdego meczu Realu Madryt, aby dostarczyć pełnej oceny siły przeciwnika.

**Główne funkcjonalności:**

- Inicjalizacja źródeł danych i komponentów analitycznych.

- Definiowanie i przygotowywanie kolumn do analizy statystyk przeciwników.
  
- Obliczanie 17 różnych statystyk dla każdego przeciwnika w każdym meczu Realu Madryt.

- Wypełnianie głównego DataFrame obliczonymi statystykami.

- Walidacja wyników analizy pod kątem kompletności i jakości danych.

**Proces działania:**

1. Ustawia bazowy DataFrame (wynik poprzednich analiz).
2. Ładuje dane meczowe Realu Madryt oraz wszystkich drużyn La Liga.
3. Przygotowuje DataFrame poprzez dodanie predefiniowanych kolumn na statystyki przeciwników.
4. Iteruje przez mecze Realu Madryt, identyfikuje przeciwnika i oblicza jego statystyki przed danym meczem.
5. Wypełnia przygotowany DataFrame obliczonymi wartościami.
6. Przeprowadza walidację i zwraca kompletny DataFrame.

---

## Skrypt `data_loader.py`

Moduł odpowiedzialny za wczytywanie, synchronizację i przygotowanie wszystkich źródeł danych wymaganych do analizy statystyk przeciwników Realu Madryt. Zapewnia spójny dostęp do danych meczowych Realu oraz wszystkich meczów La Liga.

**Kluczowe zadania:**

- Wykorzystuje `RealMadridTeamAnalyzer` jako punkt odniesienia i źródło bazowych danych meczów Realu Madryt.
- Wczytuje dane wszystkich meczów La Liga potrzebne do analizy formy i statystyk przeciwników.
- Przygotowuje DataFrame poprzez dodanie nowych kolumn (inicjalizowanych jako `pd.NA`) na statystyki przeciwników.

**Funkcje:**

- `load_base_data()`: Wczytuje i przygotowuje dane meczów Realu Madryt.
- `load_match_data()`: Wczytuje dane meczowe Realu Madryt oraz wszystkich drużyn La Liga z odpowiednich plików CSV.
- `prepare_columns()`: Dodaje do DataFrame puste kolumny na statystyki przeciwników.
- `get_data_summary()`: Zwraca podsumowanie stanu załadowanych danych.

---

## Skrypt `extended_stats.py`

Moduł zawierający funkcje do obliczania rozszerzonych statystyk dla drużyn przeciwników. Te statystyki wykraczają poza podstawowe metryki i dostarczają głębszego wglądu w długoterminową formę i charakterystykę gry przeciwnika.

**Obliczane statystyki:**

- `calculate_OP_G_SCO_ALL()`: Łączne gole strzelone przez przeciwnika w bieżącym i poprzednim sezonie do dnia meczu.
- `calculate_OP_G_CON_ALL()`: Łączne gole stracone przez przeciwnika w bieżącym i poprzednim sezonie do dnia meczu.
- `calculate_OP_G_SCO_G_CON_RAT()`: Stosunek goli strzelonych do straconych przez przeciwnika.
- `calculate_OP_ODD_W_L5()`: Średni kurs bukmacherski na wygraną przeciwnika w jego ostatnich 5 meczach.
- `calculate_OP_ODD_L_L5()`: Średni kurs bukmacherski na porażkę przeciwnika w jego ostatnich 5 meczach.

**Cechy:**

- Funkcje operują na danych historycznych przeciwnika.
- Wykorzystują `SeasonManager` do określania zakresów dat dla sezonów.
- Obsługują przypadki brzegowe (np. brak danych, pierwszy sezon w analizie).
- Zapewniają logowanie błędów.

---

## Skrypt `stats_functions.py`

Moduł grupujący funkcje, które wykorzystują istniejące kalkulatory (`StatsCalculator`, `SeasonCalculator`) do obliczania specyficznych statystyk przeciwników. Służy jako warstwa pośrednicząca, upraszczając wywołania bardziej złożonych metod z głównych klas kalkulatorów.

**Główne zadanie:**

- Dostarczenie prostego interfejsu do uzyskiwania konkretnych metryk przeciwnika, takich jak średnie gole, punkty, czy statystyki przeciwko różnym typom drużyn.

**Przykładowe funkcje:**

- `calculate_OP_G_SCO_L5()`: Średnia goli zdobytych przez przeciwnika w ostatnich 5 meczach.
- `calculate_OP_PPM_L5()`: Średnia punktów na mecz przeciwnika z ostatnich 5 meczów.
- `calculate_OP_PPM_SEA()`: Średnia punktów na mecz przeciwnika w bieżącym sezonie.
- Funkcje obliczające gole i punkty przeciwko drużynom z czołówki (`TOP`), środka tabeli (`MID`) i dołu tabeli (`LOW`).

**Działanie:**

- Każda funkcja przyjmuje odpowiedni obiekt kalkulatora (`stats` lub `calc`), datę meczu i ID drużyny (jeśli potrzebne).
- Wywołuje odpowiednią metodę z przekazanego kalkulatora.
- Zwraca obliczoną wartość lub `np.nan` w przypadku braku danych lub błędu.
