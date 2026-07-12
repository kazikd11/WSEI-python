# Sprawozdanie — Zestaw Zaliczeniowy AAP

**Autor:** Kazimierz Dąbrowski
**Data:** lipiec 2026

---

## Lab 1 — Dekoratory (`@retry` + `@cache_to_disk`)

Zaimplementowałem dwa dekoratory:

- `@retry` z exponential backoff — przy każdej nieudanej próbie czas czekania rośnie wykładniczo (`delay * backoff^próba`). Dzięki temu nie zalewamy serwera requestami.
- `@cache_to_disk` — hashuje argumenty funkcji przez MD5 i zapisuje wynik jako JSON. Drugie wywołanie z tymi samymi argumentami zwraca z pliku, bez wykonywania ciała funkcji.

**Obserwacja:** Przy 5 próbach i P(błąd) = 0.5, teoretyczna szansa sukcesu to `1 - 0.5^5 = 96.875%`. W eksperymencie na 100 wywołaniach (seed 42) wyszło blisko tej wartości — kilka porażek na 100, co zgadza się z teorią. Kluczowe jest to, że cache działa niezależnie od retry — nawet jeśli funkcja musiała się powtórzyć 4 razy, wynik jest cache'owany normalnie.

## Lab 2 — Współbieżność (multiprocessing)

Porównałem trzy podejścia do liczenia sentymentu lexicon-based na 5000 recenzjach:

| Metoda | Wynik |
|--------|-------|
| Sekwencyjnie | baseline |
| ThreadPool (16) | porównywalny czas — GIL blokuje |
| multiprocessing | najszybszy dla CPU-bound |

Żeby `multiprocessing.Pool` mógł zserializować funkcję, musiałem ją wyciągnąć do osobnego modułu (`sentiment_worker.py`). W notebooku importuję ją dynamicznie. ThreadPool nie daje przyspieszenia bo to zadanie CPU-bound i GIL blokuje wykonanie równoległe — wątki i tak czekają na siebie nawzajem.

## Lab 3 — Testowanie (pytest)

Napisałem klasę `Tokenizer` ze strip_html, lowercase i min_length, plus testy w pytest:

- Fixture `tokenizer` z domyślnymi ustawieniami
- Fixture `imdb_sample` ładująca 20 recenzji z JSON
- `@pytest.mark.parametrize` z 6 przypadkami (pusty string, sam HTML, mieszane case, interpunkcja, polskie znaki, zwykły tekst)
- Test `@pytest.mark.xfail` dla regex z emailem — tokenizer traktuje `@` jako separator (oczekiwane)

**Obserwacja:** Średnio na jedną recenzję imdb przypada sporo unikalnych tokenów (wynik w notebooku), co potwierdza bogactwo słownikowe recenzji filmowych.

## Lab 4 — Bazy danych (SQL vs JSON w SQLite)

Porównałem dwa schematy dla tych samych 2000 recenzji:

1. **Klasyczny SQL** — kolumny `text`, `label`, `word_count`, `char_count`
2. **JSON column** — jeden `doc TEXT` z zagnieżdżoną strukturą (`stats`, `tags`)

Zapytania NoSQL-owe przez `json_extract()` działają poprawnie, ale schemat JSON zajmuje więcej miejsca na dysku (bo tekst recenzji jest zapisany razem z metadanymi w jednym polu + narzut formatowania JSON). Dla tego konkretnego problemu klasyczny SQL jest lepszy — mamy stałą strukturę i potrzebujemy agregacji. JSON miałby sens gdyby schemat recenzji się zmieniał między źródłami.

## Lab 5 — PySpark (Window functions)

Użyłem window functions do:

1. Rankingu recenzji po długości w obrębie klasy (`dense_rank`)
2. Wyznaczenia top 3 najdłuższych per klasa
3. Obliczenia odchylenia od średniej klasowej
4. Moving average długości w oknie 20 ostatnich recenzji

Wykres moving average (`_workspace/moving_avg_word_count.png`) pokazuje, że obie klasy mają zbliżoną średnią długość recenzji — nie ma dużej różnicy między pozytywnymi a negatywnymi jeśli chodzi o liczbę słów. To ciekawe, bo mogłoby się wydawać że negatywne recenzje będą krótsze (ludzie krótko piszą gdy coś im się nie podoba), ale dane tego nie potwierdzają.

## Lab 6 — Data Quality

Zbudowałem mini-framework z klasami `DataContract` i `DataValidator`:

- `DataContract` przechowuje listę reguł (name, callable, severity)
- `DataValidator` iteruje po regułach i generuje raport JSON z timestampem
- Reguły o severity `error` rzucają wyjątek (fail fast)

Zdefiniowałem 8 reguł: dataset_not_empty, text_not_null, labels_binary, word_count_positive, char_count_positive, duplicates_below_1pct, class_balance_above_0_9, html_ratio_below_0_8.

Raport (`_workspace/data_quality_report.json`) zawiera podsumowanie ile reguł przeszło/nie przeszło. Reguła o HTML jest ustawiona jako `info` — nie blokuje pipeline'u, ale informuje że dane wymagają czyszczenia przed treningiem modelu.
