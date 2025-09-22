# Opis Skryptów w Folderze `RM`

Zanim przejdziemy do szczegółowego omówienia skryptów, dokonajmy krótkiej analizy przetwarzanych danych.

Folder `RM` dedykowany jest przetwarzaniu danych dotyczących klubu piłkarskiego Real Madryt. Stanowi on istotny krok w kierunku budowy finalnego, kompleksowego zbioru danych. Informacje te dzielą się na dwie główne kategorie: **dane drużynowe** oraz **dane indywidualne** (dotyczące poszczególnych zawodników).

Warto zaznaczyć, że dane drużynowe Realu Madryt są znacznie bardziej rozbudowane w porównaniu do informacji dostępnych dla drużyn przeciwnych. Oznacza to, że choć posiadamy wszystkie standardowe dane o Realu Madryt, które są zbierane również dla innych zespołów, to dodatkowo dysponujemy unikalnymi, bardziej szczegółowymi informacjami dotyczącymi wyłącznie tego klubu.

Głównym zadaniem modułu `RM` jest zatem przetwarzanie tych rozbudowanych danych, ich uzupełnianie oraz, co kluczowe, efektywne łączenie w spójną całość.

Aby lepiej zobrazować charakterystykę tych danych, przyjrzyjmy się fragmentom pochodzącym z dwóch podstawowych plików źródłowych:

`DANE INDYWIDUALNE`

| match_date | home_team       | away_team   | home_goals | away_goals | player_name   | is_first_squad | player_min | goals | assists | total_shots | shots_on_target | key_passes | fouls | fouled | is_value | editor_rating |
|------------|-----------------|-------------|------------|------------|---------------|----------------|------------|-------|---------|-------------|-----------------|------------|-------|--------|----------|---------------|
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Courtois      | 1              | 96         |       |         |             |                 |            | 0     | 0      | 1        | 5.29          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Lucas Vázquez | 1              | 96         | 0     | 1       | 1           | 0               | 2          | 1     | 3      | 1        | 3.43          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Tchouaméni    | 1              | 96         | 0     | 0       | 0           | 0               | 0          | 1     | 0      | 1        | 3.43          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Asencio       | 1              | 64         | 0     | 0       | 0           | 0               | 0          | 0     | 1      | 1        | 4.14          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Fran García   | 1              | 96         | 0     | 0       | 0           | 0               | 0          | 0     | 2      | 1        | 3.57          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Camavinga     | 1              | 96         | 0     | 0       | 0           | 0               | 0          | 1     | 1      | 1        | 4.14          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Valverde      | 1              | 86         | 0     | 0       | 2           | 1               | 0          | 0     | 2      | 1        | 3.86          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Bellingham    | 1              | 96         | 0     | 0       | 0           | 0               | 1          | 0     | 1      | 1        | 3.43          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Brahim        | 1              | 64         | 0     | 0       | 1           | 1               | 0          | 0     | 0      | 1        | 2.43          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Rodrygo       | 1              | 68         | 0     | 0       | 1           | 1               | 1          | 0     | 1      | 1        | 2.43          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Mbappé        | 1              | 96         | 2     | 0       | 3           | 2               | 2          | 0     | 3      | 1        | 5.14          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Rüdiger       | 0              | 32         | 0     | 0       | 0           | 0               | 0          | 0     | 0      | 1        | 4.29          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Modrić        | 0              | 28         | 0     | 0       | 0           | 0               | 0          | 0     | 0      | 1        | 3.43          |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Arda Güler    | 0              | 11         | 0     | 0       | 1           | 0               | 0          | 0     | 0      | 0        |               |
| 2025-03-15 | Villarreal CF   | Real Madryt | 1          | 2          | Vinícius      | 0              | 32         | 0     | 0       | 0           | 0               | 1          | 0     | 2      | 1        | 2.71          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Courtois      | 1              | 128        |       |         |             |                 |            | 0     | 0      | 1        | 4.70          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Valverde      | 1              | 128        | 0     | 0       | 0           | 0               | 1          | 0     | 0      | 1        | 4.50          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Asencio       | 1              | 128        | 0     | 0       | 0           | 0               | 0          | 1     | 0      | 1        | 4.10          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Rüdiger       | 1              | 128        | 0     | 0       | 1           | 0               | 1          | 0     | 0      | 1        | 4             |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Mendy         | 1              | 83         | 0     | 0       | 0           | 0               | 0          | 2     | 0      | 1        | 2.20          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Tchouaméni    | 1              | 65         | 0     | 0       | 1           | 0               | 1          | 1     | 1      | 1        | 3.30          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Modrić        | 1              | 65         | 0     | 0       | 0           | 0               | 1          | 0     | 0      | 1        | 3             |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Bellingham    | 1              | 128        | 0     | 0       | 2           | 0               | 0          | 1     | 3      | 1        | 3             |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Rodrygo       | 1              | 79         | 0     | 0       | 1           | 1               | 0          | 2     | 0      | 1        | 2.40          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Vinícius      | 1              | 123        | 0     | 0       | 2           | 0               | 1          | 3     | 2      | 1        | 1.70          |
| 2025-03-12 | Atlético Madryt | Real Madryt | 1          | 0          | Mbappé        | 1              | 128        | 0     | 0       | 0           | 0               | 0          | 1     | 3      | 1        | 2.50          |

**Dane indywidualne** - Te dane charakteryzują się niekonwencjonalną strukturą, gdzie pojedynczy wiersz nie reprezentuje jednego zdarzenia (meczu), lecz stanowi szczegółowe podsumowanie występu danego piłkarza. Opiera się ono na statystykach oraz ocenach pomeczowych, pochodzących zarówno od redaktorów, jak i użytkowników. W tym miejscu pragnę ponownie podziękować całej redakcji `REAL MADRYT PL`, a w szczególności Redaktorowi Jarosławowi Chomczykowi, za udostępnienie danych w tej właśnie formie. Dzięki tym informacjom możemy analizować nie tylko zespół jako całość, ale również indywidualne osiągnięcia jego zawodników.

`DANE DRUŻYNOWE`

| round | match_date | home_team_id | away_team_id | home_team      | away_team        | score | result | home_goals | away_goals | home_odds | draw_odds | away_odds | home_odds_fair | draw_odds_fair | away_odds_fair | PPM_H | PPM_A |
|-------|------------|--------------|--------------|----------------|------------------|-------|--------|------------|------------|-----------|-----------|-----------|----------------|----------------|----------------|-------|-------|
| 2     | 2019-08-24 | 1            | 116          | Real Madrid CF | Real Valladolid  | 1:1   | D      | 1          | 1          | 1.23      | 7.14      | 12.48     | 1.27           | 7.38           | 12.89          | 3.0   | 3.0   |
| 4     | 2019-09-14 | 1            | 120          | Real Madrid CF | Levante UD       | 3:2   | H      | 3          | 2          | 1.28      | 6.43      | 10.06     | 1.33           | 6.66           | 10.42          | 1.667 | 2.0   |
| 6     | 2019-09-25 | 1            | 111          | Real Madrid CF | CA Osasuna       | 2:0   | H      | 2          | 0          | 1.39      | 5.29      | 7.72      | 1.44           | 5.49           | 8.01           | 2.2   | 1.4   |
| 8     | 2019-10-05 | 1            | 122          | Real Madrid CF | Granada CF       | 4:2   | H      | 4          | 2          | 1.31      | 5.78      | 9.64      | 1.36           | 6.01           | 10.03          | 2.143 | 2.0   |
| 11    | 2019-10-30 | 1            | 124          | Real Madrid CF | CD Leganes       | 5:0   | H      | 5          | 0          | 1.3       | 5.79      | 10.94     | 1.34           | 5.98           | 11.3           | 1.9   | 0.5   |
| 12    | 2019-11-02 | 1            | 112          | Real Madrid CF | Real Betis       | 0:0   | D      | 0          | 0          | 1.25      | 6.9       | 10.81     | 1.3            | 7.16           | 11.21          | 2.0   | 1.091 |
| 14    | 2019-11-23 | 1            | 113          | Real Madrid CF | Real Sociedad    | 3:1   | H      | 3          | 1          | 1.4       | 5.15      | 7.36      | 1.46           | 5.38           | 7.69           | 2.0   | 1.769 |
| 16    | 2019-12-07 | 1            | 105          | Real Madrid CF | RCD Espanyol     | 2:0   | H      | 2          | 0          | 1.22      | 7.04      | 12.69     | 1.27           | 7.33           | 13.2           | 2.133 | 0.6   |
| 18    | 2019-12-22 | 1            | 101          | Real Madrid CF | Athletic Club    | 0:0   | D      | 0          | 0          | 1.35      | 5.31      | 8.72      | 1.41           | 5.54           | 9.1            | 2.118 | 1.588 |
| 20    | 2020-01-18 | 1            | 114          | Real Madrid CF | Sevilla FC       | 2:1   | H      | 2          | 1          | 1.69      | 3.96      | 4.99      | 1.77           | 4.14           | 5.21           | 2.105 | 1.842 |
| 22    | 2020-02-01 | 1            | 102          | Real Madrid CF | Atletico Madrid  | 1:0   | H      | 1          | 0          | 1.85      | 3.39      | 4.76      | 1.93           | 3.54           | 4.98           | 2.19  | 1.714 |
| 24    | 2020-02-16 | 1            | 104          | Real Madrid CF | RC Celta         | 2:2   | D      | 2          | 2          | 1.23      | 6.44      | 12.66     | 1.29           | 6.74           | 13.26          | 2.261 | 0.87  |
| 26    | 2020-03-01 | 1            | 103          | Real Madrid CF | FC Barcelona     | 2:0   | H      | 2          | 0          | 2.23      | 3.64      | 3.18      | 2.31           | 3.78           | 3.3            | 2.12  | 2.2   |
| 28    | 2020-06-14 | 1            | 126          | Real Madrid CF | SD Eibar         | 3:1   | H      | 3          | 1          | 1.21      | 6.91      | 14.05     | 1.26           | 7.2            | 14.64          | 2.074 | 1.0   |
| 29    | 2020-06-18 | 1            | 115          | Real Madrid CF | Valencia CF      | 3:0   | H      | 3          | 0          | 1.37      | 5.28      | 8.13      | 1.43           | 5.5            | 8.47           | 2.107 | 1.536 |
| 31    | 2020-06-24 | 1            | 110          | Real Madrid CF | RCD Mallorca     | 2:0   | H      | 2          | 0          | 1.17      | 8.0       | 16.62     | 1.22           | 8.32           | 17.28          | 2.167 | 0.867 |

**Dane drużynowe**: Struktura tych danych jest analogiczna do informacji zgromadzonych dla pozostałych zespołów w bazie danych. Obejmują one statystyki dotyczące kursów bukmacherskich, liczby bramek, dat spotkań oraz unikalnych identyfikatorów. Szczegółowe omówienie tych danych znajduje się w pliku `README-data_processing.md`, dlatego też nie będą one tutaj szerzej analizowane.

`DANE DRUZYNOWE 2`

| match_date | name          | name          | home_goals | away_goals | editor_madrid_manager_rating | avg_madrid_manager_rating | editor_madrid_team_rating | avg_madrid_team_rating | editor_opposing_team_rating | avg_opposing_team_rating | editor_referee_rating | avg_referee_rating | editor_all_players_rating |
|------------|---------------|---------------|------------|------------|------------------------------|---------------------------|---------------------------|------------------------|-----------------------------|--------------------------|-----------------------|--------------------|---------------------------|
| 2025-03-15 | Villarreal CF | Real Madryt   | 1          | 2          | 4                            | 3.63                      | 2.43                      | 2.66                   | 4.14                        | 4.11                     | 3.71                  | 3.38               | 3.69                      |
| 2025-03-12 | Atlético Madryt | Real Madryt   | 1          | 0          | 3.50                         | 2.93                      | 2.11                      | 1.99                   | 3.80                        | 3.80                     | 3.70                  | 3.83               | 3.22                      |
| 2025-03-09 | Real Madryt   | Rayo Vallecano| 2          | 1          | 3.83                         | 3.23                      | 2.67                      | 2.67                   | 3                           | 3.08                     | 2.17                  | 2.41               | 3.63                      |
| 2025-03-04 | Real Madryt   | Atlético Madryt | 2          | 1          | 3.89                         | 4.03                      | 3.89                      | 3.69                   | 3.44                        | 3.35                     | 4                     | 4.28               | 3.91                      |
| 2025-03-01 | Real Betis    | Real Madryt   | 2          | 1          | 2                            | 1.91                      | 1.33                      | 1.32                   | 4.67                        | 4.27                     | 3                     | 3.66               | 2.20                      |
| 2025-02-26 | Real Sociedad | Real Madryt   | 0          | 1          | 4.57                         | 4.30                      | 3.86                      | 3.57                   | 3.71                        | 3.63                     | 4.86                  | 4.35               | 3.96                      |
| 2025-02-23 | Real Madryt   | Girona FC     | 2          | 0          | 4.43                         | 3.74                      | 4.14                      | 3.85                   | 3                           | 2.61                     | 4.86                  | 4.18               | 4.14                      |
| 2025-02-19 | Real Madryt   | Manchester City| 3          | 1          | 5.29                         | 4.60                      | 5.71                      | 5.08                   | 1.86                        | 2.06                     | 4.86                  | 4.47               | 4.96                      |
| 2025-02-15 | CA Osasuna    | Real Madryt   | 1          | 1          | 3.80                         | 2.51                      | 3.80                      | 2.85                   | 3                           | 2.47                     | 1                     | 1.10               | 3.53                      |
| 2025-02-11 | Manchester City | Real Madryt   | 2          | 3          | 5                            | 4.33                      | 4.43                      | 4.08                   | 3.14                        | 2.96                     | 4                     | 3.93               | 4.32                      |
| 2025-02-08 | Real Madryt   | Atlético Madryt | 1          | 1          | 4                            | 3.34                      | 4.20                      | 3.66                   | 3.80                        | 3.31                     | 2.20                  | 2.50               | 4.25                      |

## Zaawansowane Dane Ocenowe (`Dane Drużynowe 2`)

Ta kategoria danych znacząco różni się od poprzednio opisywanych zbiorów, koncentrując się niemal wyłącznie na subiektywnych ocenach pomeczowych. Podobnie jak dane indywidualne, pochodzą one z portalu `REAL MADRYT PL` i obejmują dwa rodzaje ocen dla każdego analizowanego aspektu:

* **Ocena redakcji:** Ekspertyza dziennikarzy sportowych.
* **Ocena użytkowników:** Zbiorcza opinia społeczności portalu.

Kluczowe elementy poddawane ocenie to:

* **Występ Realu Madryt:** Ogólna ocena postawy drużyny.

* **Występ drużyny przeciwnej:** Ocena gry rywala.
* **Decyzje trenera Realu Madryt:** Ocena taktyki i zmian personalnych.
* **Praca sędziego:** Ocena arbitrażu, co jest szczególnie istotnym aspektem w kontekście ligi hiszpańskiej.

**Ograniczenie:** Obecnie nie dysponujemy danymi identyfikującymi konkretnych sędziów prowadzących poszczególne mecze. Uniemożliwia to, na tym etapie, uwzględnienie tego czynnika w bardziej szczegółowych analizach (potencjalne rozszerzenie w przyszłych wersjach modelu).

Mimo tego ograniczenia, te trzy zbiory danych (indywidualne, drużynowe podstawowe, drużynowe ocenowe) tworzą bogatą i wielowymiarową bazę informacji o meczach.

## Główne Cele Skryptów w Module `RM`

Mając na uwadze charakterystykę opisanych danych, skrypty zawarte w tym module realizują następujące cele:

1. **Konsolidacja i Porządkowanie Danych:**

    * Efektywne łączenie wszystkich dostępnych zbiorów danych (indywidualnych, drużynowych, ocenowych).
  
    * Standaryzacja nazw drużyn, zawodników i innych encji przy użyciu funkcji z modułu `data_processing`.
    * Nadawanie unikalnych identyfikatorów meczów, spójnych z główną bazą danych opisaną w `README-data_processing.md`.
    * Przypisywanie identyfikatorów sezonów na podstawie dat rozegrania spotkań.

2. **Wzbogacanie Danych poprzez Agregację i Obliczenia:**
    * Sumowanie statystyk indywidualnych zawodników dla każdego meczu (np. łączna liczba strzałów celnych, kluczowych podań w drużynie).
    * Wyodrębnianie i oznaczanie meczów rozgrywanych w ramach różnych rozgrywek (np. liga hiszpańska, puchary europejskie).

3. **Tworzenie Specjalistycznych Baz Danych:**
    * Budowa bazy danych wszystkich piłkarzy i trenerów Realu Madryt z okresu 2020-2025.
    * Generowanie szczegółowych zestawień dotyczących ocen i minut spędzonych na boisku, z rozróżnieniem na mecze w rozgrywkach krajowych i europejskich.

Kiedy już cele skryptu zostały opisane, przejdźmy do opisu każdego z plików.

## Opis skryptów - opis techniczny

### 1. Konsolidacja i Porządkowanie Danych

Proces ten obejmuje łączenie różnorodnych danych (indywidualnych, drużynowych, ocenowych), standaryzację nazw oraz nadawanie spójnych identyfikatorów meczów i sezonów.

* **Główny orkiestrator łączenia i standaryzacji:**  

  `RM_data_integration_pipeline.py` (`Klasa RM_merge_and_edit`): Centralny punkt integracji danych z różnych źródeł. Odpowiada za scalanie danych indywidualnych (wczytywanych przez `RM_players_analyzer.py`), drużynowych oraz ocenowych. Wykorzystuje moduł `data_processing` do standaryzacji nazw drużyn i dopasowywania danych na podstawie dat oraz identyfikatorów.

* **Przetwarzanie danych indywidualnych zawodników:**  

  `RM_players_analyzer.py` (`Klasa RealMadridPlayersAnalyzer`): Koncentruje się na wczytywaniu, czyszczeniu i wstępnym łączeniu danych dotyczących poszczególnych zawodników Realu Madryt, w tym ich statystyk i ocen. Odpowiada również za przypisywanie sezonów na podstawie dat.  
  `RM_old_data.py` (`Klasa RM_old_Data`): Zajmuje się wczytywaniem i przygotowaniem starszych, historycznych danych indywidualnych zawodników, w tym standaryzacją nazw drużyn.

* **Weryfikacja i nadawanie ID:**  
  `check_id_in_files.py`: Zawiera funkcje do sprawdzania spójności `match_id` między kluczowymi plikami oraz potencjalnie do nadawania identyfikatorów.

* **Standaryzacja w kontekście PPM:**  

  `table_actuall_PPM.py` (`Klasa SeasonPPMCalculator`): Chociaż jego głównym celem jest obliczanie PPM, wykorzystuje `DataProcessor` do standaryzacji nazw drużyn w danych sezonowych.

## 2. Wzbogacanie Danych poprzez Agregację i Obliczenia

Ten etap polega na tworzeniu nowych informacji poprzez sumowanie statystyk indywidualnych na poziomie meczu oraz kategoryzację meczów według rozgrywek.

* **Agregacja statystyk indywidualnych do poziomu meczu:**  
  `RM_data_integration_pipeline.py` (`Klasa RM_merge_and_edit`): Kluczowa rola w sumowaniu indywidualnych statystyk zawodników (np. strzały, podania) dla każdego meczu, tworząc zagregowane dane drużynowe.

* **Kategoryzacja rozgrywek:**  
  `RM_players_analyzer.py` (`Klasa RealMadridPlayersAnalyzer`): Odpowiada za identyfikację i oznaczanie meczów przynależnych do różnych typów rozgrywek (np. liga, puchary europejskie) na podstawie dostępnych danych.

## 3. Tworzenie Specjalistycznych Baz Danych

Finalnym etapem jest generowanie dedykowanych zbiorów danych, takich jak kompletna baza piłkarzy i trenerów Realu Madryt oraz szczegółowe analizy ich występów.

* **Budowa bazy piłkarzy i trenerów:**  
  `RM_players_analyzer.py` (`Klasa RealMadridPlayersAnalyzer`): Tworzy profile zawodników, przypisując im ID i podstawowe informacje. Zapisuje przetworzone dane indywidualne.  
  `RM_data_integration_pipeline.py` (`Klasa RM_merge_and_edit`): Integruje dane dotyczące trenerów i zapisuje finalne, połączone dane meczowe, które pośrednio tworzą bazę występów.

* **Generowanie zestawień ocen i minut (z podziałem na rozgrywki):**  
  `RM_players_analyzer.py` (`Klasa RealMadridPlayersAnalyzer`): Oblicza średnie oceny oraz sumaryczny czas gry dla każdego zawodnika, z możliwością rozróżnienia na rozgrywki krajowe i europejskie. Wyniki te są zapisywane w dedykowanych plikach.  
  `RM_data_integration_pipeline.py` (`Klasa RM_merge_and_edit`): Agreguje te dane na poziomie meczu, dostarczając ogólny obraz w finalnym zbiorze danych.
