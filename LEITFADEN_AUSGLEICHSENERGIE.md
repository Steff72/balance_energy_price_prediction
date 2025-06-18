# Leitfaden zur Prognose positiver und negativer Ausgleichsenergiepreise in der Schweiz

Einleitung

Ausgleichsenergiepreise – oft auch Ungleichgewichts- oder Regelenergiepreise genannt – entstehen im Strommarkt, wenn Produktion und Verbrauch nicht exakt übereinstimmen. Swissgrid als Übertragungsnetzbetreiber bilanziert diese Abweichungen und weist positive Ausgleichsenergiepreise aus (wenn Strom ins Netz eingespeist werden musste) sowie negative Ausgleichsenergiepreise (wenn Überschüsse abgenommen werden mussten). Diese Preise sind äußerst volatil und können in Spitzenzeiten drastisch steigen oder fallen. Ein präzises Vorhersagemodell mit einem Horizont bis zu 5 Tagen würde Energieversorgern und Bilanzgruppen ermöglichen, Risiken zu steuern, Kosten zu senken und strategisch zwischen Intraday- und Ausgleichsmarkt zu entscheiden. Dieser Leitfaden skizziert den Aufbau eines solchen offenen Prognosemodells auf Basis frei verfügbarer Datenquellen und Open-Source-Werkzeuge – ohne Einsatz von Cloud-Diensten.

Wichtig ist, dass das Modell Unsicherheiten transparent macht. Statt nur Punktprognosen sollen Konfidenzintervalle oder Wahrscheinlichkeitsverteilungen aufgezeigt werden, um das Risiko besser abzubilden. Das Dokument gliedert sich in folgende Hauptthemen:
•Datenquellen (Swissgrid, ENTSO-E, MeteoSchweiz, Feiertage, Energiedashboard) und mögliche prädiktive Features,
•bestehende Ansätze und Open-Source-Projekte zur Preisprognose mit Unsicherheitsquantifizierung,
•geeignete Modellierungsansätze (von Gradient Boosted Trees über Prophet bis LSTM, Bayesian usw.) und deren Methoden zur Unsicherheitsabschätzung,
•Open-Source Tools und Frameworks für Datenaufbereitung, Feature Engineering, Modellierung und Visualisierung,
•Vorgehen zur Validierung, Steigerung der Modellinterpretierbarkeit und Präsentation der Ergebnisse (GitHub-Repository, wissenschaftliche Präsentation).

Datenquellen und Feature-Engineering

Für die Prognose stehen in der Schweiz mehrere öffentliche Datenquellen zur Verfügung. In Tabelle 1 sind die wichtigsten Quellen, deren Inhalte und mögliche Nutzungen skizziert:

Tabelle 1: Wichtige Datenquellen und potenzielle Features für das Prognosemodell

DatenquelleInhaltBeispiele relevanter MerkmaleZugriff / Tools
Swissgrid – AusgleichsenergieViertelstündliche positive und negative Ausgleichsenergiepreise (historisch). Publikation monatlich als Excel/XML-Dateien.Zielvariable: Preiszeitreihen (pos./neg.). Preis-Volatilität: Historische Schwankungsmaße (z.B. rolling Std.). Autoregressive Merkmale: Letzte n Preise (z.B. letzte 1–2 Tage als Inputs für AR-Modelle).Download der Monatsdateien (XLSX/XML) via Swissgrid-Website; Import z.B. mit Python (pandas.read_excel oder xml-Parser).
ENTSO-E Transparenz (CH)Netzlast (Verbrauch), Erzeugung nach Energieträgern (z.B. Wasserkraft, PV, Wind), Import/Export und evtl. Regelenergieeinsatz auf 15-Minuten- oder Stundenniveau.Last: Prognostizierte vs. reale Netzlast (Abweichungen = Prognosefehler). Erzeugung: Einspeisung von Solar/Wind vs. Prognose (Fehlerindikator für Ungleichgewichte). Import/Export: Netto-Importe als Indikator für Engpässe oder Überschüsse. Erzeugungsmix: Anteil volatiler Erneuerbarer (hoher Anteil = potenziell mehr Unsicherheit).ENTSO-E API (z.B. via Python-Bibliothek entsoe-py) oder CSV-Downloads vom ENTSO-E Transparenzportal. Daten in Pandas importieren und mit Zeitstempeln der Preise mergen.
MeteoSchweiz WetterdatenWetterhistorie und -vorhersage (z.B. Temperatur, Windgeschwindigkeit, Sonneneinstrahlung, Niederschlag) für Schweizer Regionen.Temperatur: Einfluss auf Stromnachfrage (Heizung/Kühlung). Windgeschwindigkeit: bestimmt Windstromerzeugung (Relevanz für Prognosefehler). Globalstrahlung / Bewölkung: beeinflusst PV-Leistung. Wetterextreme: Hinweis auf mögliche Ausreißer (z. B. Sturm -> plötzliche Wind-Überproduktion).MeteoSchweiz Open Data (evtl. über APIs wie COSMO-1/COSMO-2 Vorhersagedaten, oder via offene Dienste wie Open-Meteo). Nutzung z.B. mit requests oder speziellen Wetter-Bibliotheken; Daten als Zeitreihe aufbereiten.
Feiertagskalender CHOffizielle Feiertage (kantonal und national) und ggf. Schulferien.Feiertag/werktags: Dummy-Variable für Feiertage (Nachfrage deutlich geringer). Brückentag/Wochenende: Indikator für atypische Lastprofile (Montag nach Ostern etc.).Statische Listen (z.B. vom Bundesamt oder workalendar/holidays Python-Paket) zur automatischen Generierung von Feiertagsflags.
Energiedashboard Schweiz (BFE)Dashboard mit aktuellen Energiedaten (z.B. Tagesproduktion/-verbrauch, Speicherfüllstände, Marktpreisinformationen).Tagesaktuelle Indikatoren: z.B. Füllstand Pumpspeicher, aktuelle Importquote. Marktpreise DA/ID: Falls verfügbar, könnten Day-Ahead- oder Intraday-Preise als Merkmale dienen (Benchmark-Preisniveau).Webportal (BFE); möglicherweise JSON/CSV-APIs. Daten ggf. über requests laden. Alternativ: EPEX-Spot Day-Ahead-Preise aus Marktdatenquellen beziehen (für Modell in CHF oder EUR umgerechnet).

Feature Engineering: Aus den obigen Quellen lassen sich prädiktive Merkmale berechnen, die historische Muster und zukünftige Treiber der Ausgleichsenergiepreise abbilden:
•Zeitliche Merkmale: Viertelstunde innerhalb der Stunde, Stunde des Tages, Wochentag, Monat, Saisonalität. Solche Kalenderfeatures haben sich als wichtig erwiesen, da Verbrauch und Preise starken Tages- und Wochengängen folgen. Feiertage und Wochenenden sollten speziell gekennzeichnet werden, da sie oft atypische Lastverläufe verursachen (z.B. geringere Werktagsnachfrage an Feiertagen).
•Last und Erzeugung: Die Netzlast (Stromverbrauch) ist ein zentraler Treiber – unerwartete Nachfragespitzen oder -einbrüche führen zu Ungleichgewichten. Ebenso kritisch ist die Einspeisung erneuerbarer Energien (Wind, Solar): Prognosefehler bei Wind/PV wirken sich direkt auf den Ausgleichsbedarf aus. Ein bewährtes Feature ist z.B. die Abweichung zwischen Prognose und Ist-Erzeugung bei Wind (WindForecastError) und Solar – große Abweichungen hier deuten auf hohe Ausgleichsenergiepreise hin. Darüber hinaus kann der Erzeugungsmix (z.B. Anteil volatiler Quellen vs. steuerbarer Kraftwerke) die Verlässlichkeit der Gesamterzeugung anzeigen.
•Interconnector-Flüsse: Für die Schweiz als importabhängiges Land sind Import-/Exportflüsse relevant. Hohe Nettoimporte können auf einen engen inländischen Angebotsmix hinweisen, während hohe Nettoexporte evtl. Überschüsse und damit negative Ausgleichspreise begünstigen.
•Großhandelsmarktpreise: Auch wenn im Datensatz nicht explizit genannt, sind Day-Ahead (DA)- und Intraday-Preise wertvolle Indikatoren. Da Ausgleichsenergiepreise oft auf den zuletzt gehandelten Marktpreisen aufbauen (plus Auf-/Abschläge), kann der DA-Preis als Basislinie dienen.
•Historische Preismerkmale: Die Vergangenheit der Ausgleichspreise selbst bietet Prognosekraft. Lags der Zielgröße (z.B. Preis der letzten Viertelstunde, Stunde, oder Vortag zur gleichen Zeit) und gleitende Statistiken wie Mittelwert oder Volatilität der letzten 24 Stunden können Momentum-Effekte oder regime shifts abbilden. Im Notebook werden beispielhaft die Merkmale Stunde, Wochentag, Monat, Tag des Jahres sowie Lag- und 24h-Rolling-Features implementiert.
•Systemindikatoren und Operator-Aktionen: In einigen Ländern werden Indikatoren wie die prognostizierte Systemlänge (Überschuss oder Mangel) einbezogen. Für die Schweiz könnten ähnliche Daten hilfreich sein.

Datenvorbereitung: Die genannten Daten müssen zeitlich synchronisiert werden. Alle Quellen sollten auf das gemeinsame Zeitraster der Viertelstunden gebracht werden. Danach erfolgt das Merge zu einem gemeinsamen DataFrame mit Zeitstempelindex. Wichtig ist die saubere Trennung von Trainings- und Testzeiträumen, um Information Leakage zu vermeiden.

Aktuelle Ansätze und Open-Source-Projekte

Die Vorhersage von Ausgleichsenergiepreisen ist ein relativ neues Themenfeld. Einige akademische Arbeiten und Open-Source-Projekte bieten dennoch wertvolle Anhaltspunkte:
•Probabilistische Preisprognosen (Deutschland): Eine aktuelle Studie (2022) untersuchte die sehr kurzfristige Prognose der deutschen Ausgleichsenergiepreise 30 Minuten vor Lieferung. Dabei wurden probabilistische Methoden wie Lasso-Regressionsmodelle, GAMLSS und neuronale Netze eingesetzt.
•Imbalance Forecasting Framework (Irland): 2024 wurde ein Open-Source-Benchmark für den irischen Bilanzierungsmarkt veröffentlicht. Hier zeigte sich, dass robuste Lasso- oder Tree-basierte Modelle oft besser abschneiden als tiefe Netze.
•Ansätze in Belgien und UK: Dort wird teils eine zweistufige Herangehensweise verfolgt – zunächst die Wahrscheinlichkeit für Überschuss oder Mangel schätzen, dann darauf basierend die Preisverteilung ableiten.
•Open-Source-Implementierungen: Beispiele wie das GitHub-Repository zur Prognose des deutschen Ausgleichsenergiepreises demonstrieren die Machbarkeit mit offenen Werkzeugen (Scikit-Learn, TensorFlow, etc.).

Modellierungsansätze und Unsicherheitsquantifizierung

Für die Prognose stehen unterschiedliche Modellfamilien zur Verfügung. Wichtig ist, dass sie Unsicherheiten quantifizieren können. Möglichkeiten sind:
•Gradient-Boosted Trees (XGBoost, LightGBM) – können per Quantil-Regression oder Ensemble-Methoden Prognoseintervalle liefern.
•Random Forests – erweiterbar zu Quantil-Regression Forests, wodurch Konfidenzintervalle ableitbar sind.
•ARIMA/SARIMAX – klassische Zeitreihenmodelle, die analytisch oder per Simulation Unsicherheitsbänder bereitstellen.
•Additive Modelle (Prophet, GAMLSS) – insbesondere Prophet bietet direkt Bayesian-basierte Prognoseintervalle.
•Neuronale Netze (LSTM, TFT) – Unsicherheit z.B. per Monte-Carlo-Dropout oder Ensembles.
•Bayes’sche Modelle (PyMC3/PyMC, BART) – liefern durch Posterior-Sampling glaubwürdige Intervalle.

Werkzeuge und Frameworks

Zur Umsetzung des Vorhersagemodells können ausschließlich Open-Source-Tools genutzt werden:
•Datenaufbereitung mit Pandas, entsoe-py, requests, etc.
•Feature Engineering ggf. mit tsfresh oder Scikit-Learn-Pipelines.
•Modellierung mit Scikit-Learn, XGBoost/LightGBM, Prophet oder PyTorch/TensorFlow.
•Hyperparameter-Tuning mit Optuna oder ähnlichem.
•Evaluierung mittels MAE, RMSE sowie probabilistischen Metriken wie CRPS.
•Visualisierung der Ergebnisse mit Matplotlib oder Plotly und Interpretierbarkeit z.B. via SHAP.

Validierung, Interpretierbarkeit und Ergebnispräsentation

Die historischen Daten sollten in Trainings- und Testzeiträume aufgeteilt werden und idealerweise im Walk-Forward-Verfahren ausgewertet werden. Neben klassischen Fehlermetriken sollte geprüft werden, ob z.B. 90%-Intervalle auch zu 90% der tatsächlichen Preise passen (Coverage). Modelle sollten miteinander und gegen eine naive Baseline verglichen werden. Für die Interpretierbarkeit können SHAP-Werte oder Zerlegungen des Prophet-Modells herangezogen werden. Die Ergebnisse sollten in einem offenen GitHub-Repository dokumentiert werden – mit README, Quellcode und Beispielgrafiken.

Fazit

Dieser Leitfaden zeigt auf, wie ein offenes Prognosesystem für positive und negative Ausgleichsenergiepreise in der Schweiz aufgebaut werden kann. Durch die Kombination frei zugänglicher Datenquellen, transparenter Modellierung und klarer Kommunikation der Unsicherheiten lässt sich ein wertvolles Werkzeug für Marktteilnehmer schaffen und ein Beitrag zu mehr Effizienz im Strommarkt leisten.
