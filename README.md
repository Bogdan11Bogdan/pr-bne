# Aplikacja budzika

Prosta aplikacja do zarządzania wieloma budzikami. Oprócz interfejsu konsolowego
zawiera także panel graficzny oparty na Tkinterze, który pozwala dodawać, usuwać,
aktywować i podglądać zaplanowane budziki zapisane w pliku JSON.

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

### Interfejs graficzny

Aby uruchomić panel graficzny (wymaga biblioteki Tkinter dostępnej w standardowej
dystrybucji Pythona), wystarczy:

```bash
python -m alarms
```

W oknie aplikacji znajdziesz listę istniejących budzików, formularz dodawania
nowych oraz przyciski do podglądu najbliższych powiadomień i uruchomienia
harmonogramu w tle.

Domyślnie dane zapisywane są w pliku `~/.alarms.json`. Jeśli chcesz wskazać
inną lokalizację pliku, użyj przełącznika `--storage` przed nazwą trybu, na
przykład:

```bash
python -m alarms --storage /ścieżka/do/pliku.json
```

### Tryb CLI z poziomu `python -m alarms`

Jeżeli wolisz pozostać przy wersji konsolowej, możesz uruchomić wszystkie
dotychczasowe komendy przez ten sam punkt wejścia:

```bash
python -m alarms cli add 07:30 --label "Pobudka"
python -m alarms cli list
python -m alarms cli preview
python -m alarms --storage /tmp/alarms.json cli run
```

## Harmonogram

Polecenie `run` uruchamia prosty harmonogram, który co pewien czas sprawdza najbliższe
budziki i wyświetla powiadomienie w terminalu. Aby zakończyć działanie programu,
naciśnij `Ctrl+C`.

## Testy

Do uruchomienia testów służy:

```bash
pytest
```
