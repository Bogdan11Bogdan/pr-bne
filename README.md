# Mini gra 3D (Three.js)

Prosta, przeglądarkowa gra 3D napisana w Three.js. Sterujesz neonową kostką, która zbiera lewitujące kryształki na futurystycznym placu. Liczy się wynik zdobyty w ciągu 60 sekund.

## Jak uruchomić

1. Otwórz plik `index.html` w przeglądarce (najlepiej przez prosty serwer plików, np. VS Code Live Server lub `python -m http.server`).
2. Aktywuj okno i steruj: `W/A/S/D` lub strzałki poruszają się po planie, `spacja` skacze.
3. Zbieraj kryształki, aby zwiększać wynik. Po upływie czasu możesz odświeżyć stronę i zagrać ponownie.

## Struktura

- `index.html` – warstwa UI oraz osadzenie płótna WebGL.
- `src/main.js` – logika gry, inicjalizacja sceny i pętla animacji Three.js.
