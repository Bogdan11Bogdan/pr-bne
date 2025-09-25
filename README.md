# Aplikacja budzika

Prosta aplikacja konsolowa do zarządzania wieloma budzikami. Pozwala dodawać, usuwać,
wyświetlać oraz uruchamiać harmonogram budzików zapisanych w pliku JSON.

## Instalacja i uruchomienie

Aplikacja korzysta wyłącznie ze standardowej biblioteki Pythona. Aby sprawdzić
możliwości, uruchom polecenia z poziomu katalogu repozytorium:

```bash
python -m alarms.cli add 07:30 --label "Pobudka"
python -m alarms.cli add 21:00 --label "Przygotuj kolację" --days pon śro pia
python -m alarms.cli list
python -m alarms.cli preview
python -m alarms.cli run
```

Domyślnie dane zapisywane są w pliku `~/.alarms.json`. Można wskazać własną ścieżkę za
pomocą przełącznika `--storage` (np. podczas testowania).

## Harmonogram

Polecenie `run` uruchamia prosty harmonogram, który co pewien czas sprawdza najbliższe
budziki i wyświetla powiadomienie w terminalu. Aby zakończyć działanie programu,
naciśnij `Ctrl+C`.

## Testy

Do uruchomienia testów służy:

```bash
pytest
```
