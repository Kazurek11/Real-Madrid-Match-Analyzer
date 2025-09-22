# Struktura Datasetu do Predykcji Wyników Meczów

> Dokument opisuje strukturę finalnego zestawu danych używanego do modelowania kursów bukmacherskich dla meczów Realu Madryt. Zawiera komplet pól, ich znaczenie oraz reguły uzupełniania braków.

---

## Spis treści
- [Struktura Datasetu do Predykcji Wyników Meczów](#struktura-datasetu-do-predykcji-wyników-meczów)
  - [Spis treści](#spis-treści)
  - [Wprowadzenie](#wprowadzenie)
  - [Struktura Danych](#struktura-danych)
    - [1. Informacje Podstawowe o Meczu](#1-informacje-podstawowe-o-meczu)
    - [2. Dane Zawodników Realu Madryt (dla 16 zawodników)](#2-dane-zawodników-realu-madryt-dla-16-zawodników)
    - [3. Statystyki Zespołowe i Trenera Realu Madryt](#3-statystyki-zespołowe-i-trenera-realu-madryt)
      - [Dane Trenera](#dane-trenera)
      - [Forma Zespołu](#forma-zespołu)
      - [Skuteczność vs Poziom Rywali](#skuteczność-vs-poziom-rywali)
    - [4. Statystyki Przeciwnika](#4-statystyki-przeciwnika)
      - [Forma Przeciwnika](#forma-przeciwnika)
      - [Skuteczność Przeciwnika vs Poziom Rywali](#skuteczność-przeciwnika-vs-poziom-rywali)
      - [Statystyki Sezonowe i Kursy](#statystyki-sezonowe-i-kursy)
    - [5. Statystyki Bezpośrednich Spotkań (H2H)](#5-statystyki-bezpośrednich-spotkań-h2h)
    - [6. Zmienna Docelowa (Target)](#6-zmienna-docelowa-target)
  - [Logika Tworzenia Zmiennych i Obsługa Brakujących Danych](#logika-tworzenia-zmiennych-i-obsługa-brakujących-danych)

---

## Wprowadzenie

Niniejszy dokument szczegółowo opisuje strukturę finalnego datasetu, stworzonego na potrzeby projektu predykcyjnego. Zestaw danych został zbudowany w oparciu o wielowymiarowe informacje, obejmujące zarówno podstawowe dane o meczach, szczegółowe statystyki zawodników, jak i zagregowane wskaźniki formy drużyny Realu Madryt, drużyny przeciwnej oraz historię bezpośrednich spotkań.

Celem jest przetestowanie tezy, że zaawansowane statystyki piłkarzy i drużyny z przeszłości korelują z prawdopodobieństwem wygrania meczu, co znajduje odzwierciedlenie w zmiennej docelowej – kursie bukmacherskim.

> Konwencje nazw zmiennych:
> - RM -> Real Madryt
> - OP -> Przeciwnik
> - H2H -> Historia bezpośrednich meczów
> - PPM -> Punkty na mecz
> - GPM -> Gole na mecz

<div style="page-break-before: always;"></div>

## Struktura Danych

Poniżej przedstawiono szczegółowy opis każdej zmiennej wchodzącej w skład datasetu, podzielony na logiczne kategorie.

### 1. Informacje Podstawowe o Meczu

Dane identyfikujące i kategoryzujące każde spotkanie.

| Nazwa Zmiennej | Opis | Przykład |
| :------------- | :--- | :--- |
| `MATCH_ID` | Unikalny identyfikator meczu. | `4` |
| `M_DATE` | Data rozegrania meczu. | `2020-12-30` |
| `SEASON` | Sezon rozgrywkowy. | `2023-24` |
| `IS_HOME` | Flaga wskazująca, czy Real Madryt grał u siebie. | `1` (tak), `0` (nie) |
| `OPP_ID` | Unikalny identyfikator drużyny przeciwnej. | `114` |

---

### 2. Dane Zawodników Realu Madryt (dla 16 zawodników)

Dla każdego z 16 zawodników kadry meczowej (oznaczonych jako `X` od 1 do 16) zebrano następujący zestaw danych.

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `RM_PX_X` | ID zawodnika Realu Madryt na umownej pozycji X. |
| `RM_PX_X_FSQ` | Czy zawodnik rozpoczął mecz w pierwszym składzie (1=tak, 0=nie). |
| `RM_PX_X_RT` | Czy zawodnik otrzymał ocenę pomeczową (1=tak, 0=nie). |
| `RM_PX_X_POS` | Pozycja nominalna zawodnika na boisku (np. GK, CB, ST). |
| `RM_PX_X_RT_M` | Ocena zawodnika w poprzednim rozegranym meczu. |
| `RM_PX_X_RT_PS` | Średnia ocen zawodnika w poprzednim sezonie. |
| `RM_PX_X_FORM5` | Średnia ocen zawodnika z jego ostatnich 5 występów. |
| `RM_PX_X_WINR` | Procent wygranych meczów, gdy zawodnik grał w pierwszym składzie. |
| `RM_PX_X_G90` | Średnia liczba goli na 90 minut w bieżącym sezonie. |
| `RM_PX_X_A90` | Średnia liczba asyst na 90 minut w bieżącym sezonie. |
| `RM_PX_X_KP90` | Średnia liczba kluczowych podań na 90 minut w bieżącym sezonie. |

<div style="page-break-before: always;"></div>

### 3. Statystyki Zespołowe i Trenera Realu Madryt

Dane opisujące ogólną formę drużyny, trenera oraz skuteczność w starciach z rywalami o różnym poziomie sportowym.

#### Dane Trenera

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `RM_C_ID` | ID trenera Realu Madryt. |
| `RM_C_RT_PS` | Średnia ocen trenera w poprzednim sezonie. |
| `RM_C_FORM5` | Średnia ocen trenera z ostatnich 5 meczów. |

#### Forma Zespołu

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `RM_G_SCO_L5` | Średnia liczba goli zdobytych przez Real w ostatnich 5 meczach. |
| `RM_G_CON_L5` | Średnia liczba goli straconych przez Real w ostatnich 5 meczach. |
| `RM_GDIF_L5` | Średnia różnica bramek Realu w ostatnich 5 meczach. |
| `RM_PPM_L5` | Średnia liczba punktów na mecz zdobytych przez Real w ostatnich 5 meczach. |
| `RM_PPM_SEA` | Średnia liczba punktów na mecz zdobytych przez Real w bieżącym sezonie. |
| `RM_OPP_POS_L5` | Średnia pozycja ligowa rywali Realu z ostatnich 5 meczów. |

#### Skuteczność vs Poziom Rywali

*(na podstawie PPM z poprzedniego sezonu)*

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `RM_PPM_VS_TOP` | Średnia punktów na mecz Realu vs drużyny TOP (>1.9 PPM). |
| `RM_GPM_VS_TOP` | Średnia goli na mecz Realu vs drużyny TOP (>1.9 PPM). |
| `RM_PPM_VS_MID` | Średnia punktów na mecz Realu vs drużyny średnie (1.2-1.9 PPM). |
| `RM_GPM_VS_MID` | Średnia goli na mecz Realu vs drużyny średnie (1.2-1.9 PPM). |
| `RM_PPM_VS_LOW` | Średnia punktów na mecz Realu vs drużyny słabe (<1.2 PPM). |
| `RM_GPM_VS_LOW` | Średnia goli na mecz Realu vs drużyny słabe (<1.2 PPM). |

<div style="page-break-before: always;"></div>


### 4. Statystyki Przeciwnika

Zestaw danych analogiczny do statystyk Realu Madryt, pozwalający na ocenę formy i siły rywala.

#### Forma Przeciwnika

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `OP_G_SCO_L5` | Średnia liczba goli zdobytych przez przeciwnika w ostatnich 5 meczach. |
| `OP_G_CON_L5` | Średnia liczba goli straconych przez przeciwnika w ostatnich 5 meczach. |
| `OP_GDIF_L5` | Średnia różnica bramek przeciwnika w ostatnich 5 meczach. |
| `OP_PPM_L5` | Średnia liczba punktów na mecz przeciwnika w ostatnich 5 meczach. |
| `OP_PPM_SEA` | Średnia liczba punktów na mecz przeciwnika w bieżącym sezonie. |
| `OP_OPP_PPM_L5` | Średnia punktów na mecz rywali, z którymi grał przeciwnik w ost. 5 meczach. |

#### Skuteczność Przeciwnika vs Poziom Rywali

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `OP_PPM_VS_TOP` | Średnia punktów na mecz przeciwnika vs drużyny TOP (>1.9 PPM) w dotychczasowym i poprzednim sezonie |
| `OP_GPM_VS_TOP` | Średnia goli na mecz przeciwnika vs drużyny TOP (>1.9 PPM) w dotychczasowym i poprzednim sezonie |
| `OP_PPM_VS_MID` | Średnia punktów na mecz przeciwnika vs drużyny średnie (1.2-1.9 PPM) w dotychczasowym i poprzednim sezonie |
| `OP_GPM_VS_MID` | Średnia goli na mecz przeciwnika vs drużyny średnie (1.2-1.9 PPM) w dotychczasowym i poprzednim sezonie |
| `OP_PPM_VS_LOW` | Średnia punktów na mecz przeciwnika vs drużyny słabe (<1.2 PPM) w dotychczasowym i poprzednim sezonie |
| `OP_GPM_VS_LOW` | Średnia goli na mecz przeciwnika vs drużyny słabe (<1.2 PPM) w dotychczasowym i poprzednim sezonie |

#### Statystyki Sezonowe i Kursy

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `OP_G_SCO_ALL` | Łączna liczba goli strzelonych przez rywala w sezonie. |
| `OP_G_CON_ALL` | Łączna liczba goli straconych przez rywala w sezonie. |
| `OP_G_SCO_G_CON_RAT` | Stosunek goli strzelonych do straconych przez rywala w sezonie. |
| `OP_ODD_W_L5` | Średni kurs bukmacherski na wygraną przeciwnika z ostatnich 5 meczów. |
| `OP_ODD_L_L5` | Średni kurs bukmacherski na porażkę przeciwnika z ostatnich 5 meczów. |

<div style="page-break-before: always;"></div>


### 5. Statystyki Bezpośrednich Spotkań (H2H)

Dane historyczne dotyczące rywalizacji pomiędzy Realem Madryt a danym przeciwnikiem.

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `H2H_RM_W_L5` | Procent wygranych Realu Madryt w ostatnich 5 bezpośrednich meczach. |
| `H2H_RM_GDIF_L5` | Bilans bramkowy Realu w ostatnich 5 bezpośrednich meczach. |
| `H2H_PPM_L5` | Średnia punktów na mecz Realu w ostatnich 5 bezpośrednich meczach. |
| `H2H_PPM` | Średnia punktów na mecz Realu we wszystkich historycznych meczach H2H. |
| `H2H_EXISTS` | Flaga wskazująca, czy istnieją wcześniejsze mecze H2H (1=tak, 0=nie). |

---

### 6. Zmienna Docelowa (Target)

Kluczowa zmienna, którą model będzie starał się przewidzieć.

> `RM_ODD_W` jest jedyną zmienną docelową (target), na której uczone są modele predykcyjne.

| Nazwa Zmiennej | Opis |
| :------------- | :--- |
| `RM_ODD_W` | **(TARGET)** Kurs bukmacherski na zwycięstwo Realu Madryt. |

---

## Logika Tworzenia Zmiennych i Obsługa Brakujących Danych

Istotnym wyzwaniem przy tworzeniu datasetu była obsługa przypadków brzegowych, takich jak debiut zawodnika w drużynie lub pierwszy sezon w analizowanej bazie danych.

> Reguły uzupełniania braków mają charakter techniczny i służą zapewnieniu spójności kolumn w całym zbiorze danych.

* **Statystyki boiskowe (Gole, Asysty, Kluczowe Podania)**: W przypadku zawodników bez historii w poprzednim sezonie, puste wartości zostały uzupełnione **średnią wartością dla danej pozycji** z poprzedniego sezonu. Takie podejście uwzględnia specyfikę gry na różnych pozycjach (np. napastnik vs obrońca).
* **Oceny ogólne (Ratingi)**: W przypadku braku średniej oceny zawodnika z poprzedniego sezonu (pochodzącej z ocen redakcji *RealMadryt.pl*), zastosowano **ogólną średnią ocen wszystkich zawodników** z poprzedniego sezonu, bez podziału na pozycje. Założono, że ocena subiektywna jest mniej skorelowana z pozycją niż twarde statystyki.
* **Oceny rywali (Punkty, gole na mecz)**: W przypadku rozegrania spotakania RM z beniaminkiem jego statystyki zostały uzupełnione na podstawie danych o spadkowiczach z poprzedniego sezonu. Założono, że poziom drużyn wchodzących z LaLiga 2 jest zbliżony do spadkowiczów.

> Zastosowane procedury imputacji i walidacji danych zapewniają brak wartości NaN/null w zbiorze. Każda komórka w każdej kolumnie ma zdefiniowaną, spójnie typowaną wartość, a każdy mecz stanowi kompletny rekord gotowy do trenowania i ewaluacji modeli bez dodatkowego czyszczenia.
>
--- 
