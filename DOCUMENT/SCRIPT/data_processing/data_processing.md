# Opis aktualnych skryptów w folderze ***data_processing***

Cały folder data_processing służy do jak najwyzszej automatyzacji danych rywali Realu Madryt. W naszym projekcie chcemy końćowo zbierać dane o przeróżnich informacjach. Wszystkie te dane są składową podstaowych danych. Mając do dyspozycji nazwy druzyn oraz gole tych druzyn w poszczegolnych meczach i czas rozgyrwania spotkania jestesmy w stanie dojść do przeróznych informacji. takich jak punkty danej druzyny na mecz w czasie rzeczywistym, gole na mecz w sezonie strzelone dotychczas (do czasu jakieś daty )
wyniki spotkań. Ten moduł jest po to, żeby w sposób pełni automatyczny za pomoca jednego klikniecia uruchomienia konkrentego skryptu otrzymać informacje na temat kazdej z druzyn w odpowiednim czasie.
Z poczatku nasze dane dla przykładowego sezonu są w takim formacie:

| round | match_date | home_team         | away_team      | home_goals | away_goals | home_odds | draw_odds | away_odds |
|-------|------------|-------------------|---------------|------------|------------|-----------|-----------|-----------|
| 1     | 2020-09-12 | Cádiz CF          | CA Osasuna    | 0          | 2          | 3.09      | 2.87      | 2.68      |
| 1     | 2020-09-12 | Granada CF        | Athletic Club | 2          | 0          | 2.68      | 2.87      | 3.09      |
| 1     | 2020-09-12 | SD Eibar          | RC Celta      | 0          | 0          | 2.74      | 3.06      | 2.83      |
| 1     | 2020-09-13 | Villarreal CF     | SD Huesca     | 1          | 1          | 1.56      | 4.13      | 6.24      |
| 1     | 2020-09-13 | Valencia CF       | Levante UD    | 4          | 2          | 2.34      | 3.34      | 3.13      |
| 1     | 2020-09-13 | Deportivo Alaves  | Real Betis    | 0          | 1          | 3.36      | 3.09      | 2.35      |
| 1     | 2020-09-13 | Real Valladolid   | Real Sociedad | 1          | 1          | 3.09      | 2.88      | 2.66      |
| 1     | 2021-01-12 | Atletico Madrid   | Sevilla FC    | 2          | 0          | 2.12      | 3.04      | 4.11      |
| 1     | 2021-02-09 | Real Madrid CF    | Getafe CF     | 2          | 0          | 1.62      | 3.86      | 5.92      |
| 1     | 2021-02-24 | FC Barcelona      | Elche CF      | 3          | 0          | 1.15      | 8.62      | 18.7      |
| 2     | 2020-09-19 | RC Celta          | Valencia CF   | 2          | 1          | 2.22      | 3.34      | 3.4       |
| 2     | 2020-09-19 | Villarreal CF     | SD Eibar      | 2          | 1          | 1.67      | 3.78      | 5.58      |
| 2     | 2020-09-19 | Getafe CF         | CA Osasuna    | 1          | 0          | 2.03      | 3.04      | 4.45      |
| 2     | 2020-09-20 | Granada CF        | Deportivo Alaves | 2       | 1          | 2.27      | 2.87      | 3.91      |
| 2     | 2020-09-20 | Real Sociedad     | Real Madrid CF | 0        | 0          | 4.39      | 3.71      | 1.82      |
| 2     | 2020-09-20 | SD Huesca         | Cádiz CF      | 0          | 2          | 2.03      | 2.97      | 4.64      |
| 2     | 2020-09-20 | Real Betis        | Real Valladolid | 2        | 0          | 1.87      | 3.42      | 4.58      |
| 2     | 2021-01-06 | Athletic Club     | FC Barcelona  | 2          | 3          | 5.32      | 4.26      | 1.61      |
| 2     | 2021-02-17 | Levante UD        | Atletico Madrid | 1        | 1          | 4.76      | 3.43      | 1.84      |
| 2     | 2021-03-17 | Sevilla FC        | Elche CF      | 2          | 0          | 1.47      | 4.23      | 7.82      |
| 3     | 2020-09-26 | Elche CF          | Real Sociedad | 0          | 3          | 6.35      | 3.65      | 1.63      |
| 3     | 2020-09-26 | Deportivo Alaves  | Getafe CF     | 0          | 0          | 3.51      | 2.76      | 2.51      |

Mamy informacje tylko o podstawowych statystykach w formie raportu z kazdego meczu.
Naszym celem w realizacji tego modułu było ujednolicenie danych, nadanie im unikatowych ideksów do pracy, nadanie im dodatkowych cech ktore wynikały pośrednio z poprzednich danych oraz na końcu złączenie ich w jeden końcowy dataset ktory bedzie zawierał wszystkie spotkania tworząć w pełni komplementarne podłoże do dalszej pracy.

---

## Ujednolicenie danych

Modułem ktory zajmuje się tym zadaniem jest ***data_processor*** ktory:

- **standaryzuje nazwy druznyn**  
  Druzyny moga przyjmować wiele nazw. Na FC Barcelone (Pełna nazwa) mozna powiedzieć Barcelona, Barca, FC Barca idp. Podobnie jest z każdą druzyną, aby nasze datasety były odporne na bazy danych z róznych źrodeł i uniknąć powielanych błedów nazw mamy funkcje ktora zmienia we wszystkich folderach zawierająch odpowienie kolumny (takie jak home_team, away_team, gospodarz, gość idp) nazwe druzny na tę odpowiednia - JEDYNA

  przykład:

  ``` python
  'Real Madrid CF': ['Real Madrid', 'Real Madryt', 'Real Madrid CF', 'Madrid'],
  'FC Barcelona': ['Barcelona', 'FC Barcelona', 'Barca', 'Barça'],
  'Atletico Madrid': ["Atlético Madryt",'Atletico Madrid', 'Atlético Madrid', 'Atletico', 'Atlético','Atl. Madrid'],
  'Athletic Club': ['Athletic Bilbao', 'Athletic Club', 'Athletic','Ath Bilbao']
  ```

nadaje unikatowe indeksy - Każda z drużyn pojawiająca się w naszych bazach danych ma swój unikatowy indeks. Służy to temu, aby porównując, przetwarzać lub uzupełniając dane, działać na liczbach, które są łatwiej rozróżnić od nazw (np. Atletico i Athletic).

przykład:

```python
team_id,team_name
1,Real Madrid CF
101,Athletic Club
102,Atletico Madrid
103,FC Barcelona
104,RC Celta
105,RCD Espanyol
106,Getafe CF
```

## Nadanie nowych danych

### `result`, `score` – Wynik meczu

To również **podstawowe dane**, które muszą powstać, aby mogły powstać bardziej zaawansowane, takie jak np. **PPM**.  

- Kolumna **`score`** oznacza wynik, np. `1:2`.
- Kolumna **`result`** oznacza zwycięzcę na podstawie miejsca rozgrywania meczu:
  - **H** – wygrana gospodarza,
  - **D** – remis,
  - **A** – wygrana gościa.

---

### **PPM – Punkty na mecz**

Za utworzenie kolumn **`PPM_H`** (Punkty na mecz Gospodarza – *Points per match home team*) oraz **`PPM_A`** (Punkty na mecz Gościa – *Points per match away team*) odpowiada skrypt `table_actuall_PPM`, który przetwarza dane **mecz po meczu** z rozdzieleniem na sezony.  
Sezon traktujemy jako **reset** – z jego końcem wszystko rozpoczyna się od nowa.  
Drużyna w czasie pomiędzy sezonami mogła się znacząco wzmocnić lub osłabić, więc aby nadać temu kształt albo to zbadać (porównując PPM z dwóch różnych sezonów), zaczynamy wtedy liczyć punkty na mecz od nowa.

---

### **Fair odds – uczciwe kursy**

Każdy kurs podawany przez bukmachera jest **obciążony marżą bukmacherską**.  
Co to właściwie znaczy?  
Każdy kurs na dane zdarzenie możemy łatwo przekalkulować na prawdopodobieństwo tego zdarzenia korzystając ze wzoru:  
**1/p**, gdzie *p* to kurs.

Kiedy weźmiemy wszystkie kursy na dane zdarzenie (kurs na zwycięstwo gospodarza, remis, zwycięstwo gościa), powinniśmy dostać liczbę **1** (czyli 100% – suma wszystkich prawdopodobieństw).  
Jak się okazuje, nigdy nie otrzymamy 100%. To dlatego, że w takim przypadku kurs byłby zbyt niekorzystny dla bukmachera.  
**Bukmacher wylicza swoją własną, indywidualną marżę na kursie.**

Najlepiej widać to na przykładzie zdarzeń bez faworyta (prawdopodobieństwo każdego z zawodników powinno być równe).  
Gdy weźmiemy przypadek dwóch osób, które mają na wygranie czegoś po 50% szans, bukmacher wyceniając takie zdarzenie da kurs 1.9 na każdego z nich, a z naszego wzoru wynikałoby, że kurs ten powinien wynosić 2.0.

Wcześniej wspomniałem, że każdy kurs jest **indywidualny**, więc nie jesteśmy w stanie przewidzieć, na jakiego z rywali została nałożona konkretna marża.  
W moim skrypcie traktuję ją jako **proporcjonalną** (nie mylić z równą) dla każdego z przypadków (kursu na zwycięstwo, remis, porażkę – np. gospodarza).  
Wykonuję taką operację, żeby kursy wskazywały pośrednio na prawdopodobieństwo danego zdarzenia, wynikiem czego każdy kurs z dopiskiem `_fair` jest proporcjonalnie dostosowany do kursu bukmachera.

> **Jest to istotne, ponieważ gdy chcemy przewidywać prawdopodobieństwo wyniku względem kursu, to powinien być on odmarżowany.**

---

### **`match_id` – unikatowy identyfikator**

- `match_id` to **unikatowy identyfikator każdego meczu** w naszej bazie.
- Tam, gdzie występuje drużyna o `id=1` (Real Madryt), to ID są z zakresu **1–N**, gdzie N to liczba meczów Realu.
- Tam, gdzie nie ma `id=1` na pozycji `home_team_id` oraz `away_team_id`, indeksy zaczynają się od **1000–K–N**, gdzie K to wszystkie mecze.
- Przy meczach Realu często unikatowym ID mogłaby być data meczu, bo niemożliwe jest rozegranie dwóch spotkań podczas jednego dnia, ale przy liczbie meczów rywali byłoby to niepoprawne, ponieważ w jednym dniu może być rozgrywana nawet cała kolejka spotkań.

---

### **`home_team_id`, `away_team_id` – unikatowe indeksy drużyn**

Opisane w punkcie powyżej.

---

Dzięki temu skryptowi mamy **kompletny plik ze wszystkimi meczami LaLiga** z odpowiednimi indeksami oraz wyodrębniony DataFrame z meczami Realu do dalszej edycji.  
Będziemy bazować na tym pliku, mając pewność, że mecze są również w pliku `all_matches.csv`.

---

## **Weryfikacja danych**

Trudno weryfikować dane mecz po meczu, lecz można z danych z każdego sezonu utworzyć **tabelę końcową**, którą można porównać z tabelą dostępną w internecie.  
Na podstawie danych z tabeli jesteśmy w stanie spojrzeć na:

- liczbę kolejek (końcowo każda drużyna powinna mieć ich 38, jeżeli sezon dobiegł końca),
- liczbę punktów,
- różne dane dotyczące goli każdej z drużyn.

Porównując to z danymi aktualnymi, jesteśmy w stanie szybko zlokalizować ewentualne błędy lub utwierdzić się w przekonaniu, że nasze dane są prawdziwe i przejść do dalszego etapu projektu.

---

## **Połączenie i integracja danych**

Kiedy już dane są w pełni uzupełnione, zapisujemy je w **jednym wspólnym pliku**, który reprezentuje WSZYSTKIE mecze, na których będziemy potem działać.  
Specjalnie wyselekcjonowane są mecze Realu, które zwraca skrypt `get_RM_matches.py`.
