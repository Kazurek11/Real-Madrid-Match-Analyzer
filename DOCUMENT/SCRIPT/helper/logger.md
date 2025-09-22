# Wprowadzenie do logowania

Logowanie to kluczowy element każdej profesjonalnej aplikacji, umożliwiający rejestrowanie zdarzeń, błędów i informacji o działaniu programu. Dobry system logowania pozwala na efektywne monitorowanie, diagnostykę i rozwiązywanie problemów występujących w oprogramowaniu.

## Poziomy logowania

Logger działa na zasadzie hierarchii komunikatów według ich ważności:

- **DEBUG** - szczegółowe informacje, przydatne głównie podczas rozwoju i debugowania  
- **INFO** - potwierdzenia normalnego działania aplikacji  
- **WARNING** - wskazania potencjalnych problemów, które nie wpływają na główne funkcjonalności  
- **ERROR** - błędy uniemożliwiające wykonanie konkretnych funkcji  
- **CRITICAL** - krytyczne problemy zagrażające działaniu całej aplikacji  

## Kluczowe komponenty loggera

- **Logger** - główny obiekt przyjmujący i przetwarzający komunikaty  
- **Handlery** - określają docelowe miejsca zapisu logów (pliki, konsola, sieć)  
- **Formattery** - definiują format i strukturę komunikatów  
- **Filtry** - umożliwiają selektywne zapisywanie komunikatów  

## Zalety profesjonalnego logowania

- **Diagnostyka błędów** - łatwiejsze wykrywanie i naprawianie problemów  
- **Monitorowanie wydajności** - śledzenie czasów wykonania operacji  
- **Rekonstrukcja zdarzeń** - możliwość odtworzenia sekwencji działań  
- **Bezpieczeństwo** - rejestracja prób nieautoryzowanego dostępu  
- **Analityka** - zbieranie danych o użytkowaniu aplikacji  

## Konfiguracja loggera

Efektywny logger powinien umożliwiać:

- **Wybór poziomu logowania** - filtrowanie komunikatów według ważności  
- **Elastyczne formatowanie** - określanie struktury zapisywanych informacji  
- **Wiele celów zapisu** - jednoczesny zapis do pliku i wyświetlanie w konsoli  
- **Rotację plików** - automatyczne zarządzanie wielkością i liczbą plików logów  

## Dobre praktyki logowania

- **Trafne komunikaty** - precyzyjne i kontekstowe informacje  
- **Odpowiedni poziom szczegółowości** - dopasowanie ilości szczegółów do celu  
- **Spójny format** - ujednolicony schemat dla wszystkich komunikatów  
- **Zawieranie kontekstu** - informacje o czasie, module i szczegółach operacji  
- **Ochrona danych wrażliwych** - niewykorzystywanie logów do przechowywania danych osobowych  

## Zastosowanie w projekcie analizy danych

W analizie danych logger jest szczególnie wartościowy do:

- **Śledzenia procesu ETL** - zapisywanie informacji o wczytywaniu i transformacji danych  
- **Walidacji danych** - rejestrowanie problemów z formatem lub zawartością danych  
- **Monitorowania złożonych obliczeń** - kontrola poprawności wykonywania algorytmów  
- **Debugowania skryptów** - identyfikacja problemów w kodzie przetwarzającym dane  
- **Dokumentowania przepływu pracy** - automatyczny zapis kolejnych kroków analizy  

Logger jest nie tylko narzędziem diagnostycznym, ale również integralną częścią architektury aplikacji, która wspiera jakość, niezawodność i bezpieczeństwo oprogramowania.

## Implementacja w projekcie Real Madrid

Nasz logger w projekcie analizy danych piłkarzy Real Madrid:

- **Zapisuje wszystkie operacje** - tworzenie pełnego śladu procesu analizy  
- **Monitoruje błędy wczytywania danych** - wykrywanie problemów z plikami Excel  
- **Rejestruje statystyki** - zapisywanie informacji o ilości rekordów i zakresach dat  
- **Zapewnia odporność na błędy** - kontynuowanie pracy nawet przy częściowych problemach  
- **Wyświetla kluczowe informacje** - natychmiastowe powiadamianie o istotnych zdarzeniach  

## Przykład użycia loggera

```python
import logging

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Przykładowe użycie
logger.debug("To jest komunikat debug")
logger.info("Informacja o działaniu programu")
logger.warning("Ostrzeżenie o potencjalnym problemie")
logger.error("Błąd w wykonaniu funkcji")
logger.critical("Krytyczny błąd aplikacji")

