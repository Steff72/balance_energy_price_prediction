# Ausgleichsenergiepreisprognose

Dieses Projekt untersucht die Vorhersage positiver und negativer Ausgleichsenergiepreise in der Schweiz. Es basiert ausschließlich auf frei verfügbaren Datenquellen und Open-Source-Tools.

## Inhalt des Repositories

- `LEITFADEN_AUSGLEICHSENERGIE.md` – Ausführliche Erläuterung der Datenquellen, möglicher Features und Modellierungsansätze.
- `ausgleichsenergiepreisprognose.ipynb` – Notebook mit einem ersten Demonstrationscode zum Datenbezug, einem einfachen Basismodell und integrierten Funktionen für zusätzliche Datenquellen. Die Zusatzdaten (Netzlast, Wetter und Feiertage) werden nun auch als Features im Modell genutzt.
- `fetch_additional_data.py` – Beispielskript zum Abruf weiterer Datenquellen (ENTSO-E, Wetter, Feiertage), die nun auch im Notebook verfügbar sind.
- `train_with_additional.py` – Minimalbeispiel, das diese Zusatzdaten zusammenführt und im Modell verwendet.

## Installation

Die benötigten Bibliotheken können mit pip installiert werden:

```bash
pip install pandas requests openpyxl scikit-learn entsoe-py holidays
```


## Nutzung

1. Klonen oder herunterladen des Repositories.
2. Das Notebook `ausgleichsenergiepreisprognose.ipynb` in einer lokalen Jupyter-Umgebung öffnen.
3. Die einzelnen Zellen nacheinander ausführen. Bei fehlender Internetverbindung werden Platzhalterdaten erzeugt.
4. Optional kann `fetch_additional_data.py` separat ausgeführt werden, um dieselben Datenquellen abzurufen und eine zusammengeführte CSV-Datei zu erzeugen.

Weitere Hinweise zu Datenquellen und Vorgehensweise finden sich im Leitfaden.

## Lizenz

Die Inhalte stehen unter der MIT-Lizenz (siehe `LICENSE`).
