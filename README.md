Leitfaden zur Prognose positiver und negativer Ausgleichsenergiepreise in der Schweiz

Einleitung

Ausgleichsenergiepreise entstehen im Strommarkt, wenn Produktion und Verbrauch nicht exakt übereinstimmen. Swissgrid bilanziert diese Abweichungen und weist positive und negative Ausgleichsenergiepreise aus. Diese Preise sind volatil und können stark schwanken. Ein präzises Vorhersagemodell mit einem Horizont bis zu 5 Tagen ermöglicht Energieversorgern, Risiken zu steuern und strategisch zu planen. Dieser Leitfaden beschreibt die Entwicklung eines offenen Prognosemodells auf Basis öffentlich verfügbarer Datenquellen und Open-Source-Werkzeugen, ohne Cloud-Dienste.

Ziel ist ein Modell, das Unsicherheiten transparent macht: statt nur Punktprognosen sollen Konfidenzintervalle oder Wahrscheinlichkeitsverteilungen ausgewiesen werden.

Datenquellen und Feature-Engineering

Tabelle 1: Wichtige Datenquellen und potenzielle Features

Datenquelle	Inhalt	Relevante Merkmale	Zugriff
Swissgrid	Viertelstündliche positive/negative Ausgleichsenergiepreise	Zielvariable, historische Volatilität, Lags	Excel/XML-Downloads
ENTSO-E	Netzlast, Erzeugung, Import/Export	Prognosefehler, Erzeugungsmix, Systembilanz	entsoe-py, CSV
MeteoSchweiz	Wetterdaten	Temperatur, Wind, Solarstrahlung	MeteoSchweiz API/Open-Meteo
Feiertage Schweiz	Offizielle Feiertage	Feiertags-Dummy, Brückentage	holidays-Paket, Onlinekalender
Energiedashboard CH	Tagesdaten zu Produktion, Verbrauch, Speicher	Speicherfüllstand, Marktpreise	Webportal/API (evtl. JSON)

Weitere Features
	•	Zeitliche Merkmale: Stunde, Wochentag, Feiertag
	•	Erzeugungsprognosefehler: Ist - Prognose bei Wind und Solar
	•	Import/Export-Salden als Knappheitsindikator
	•	Historische Preis-Features: Lag-Werte, rollierende Volatilität

Bestehende Projekte und Studien
	•	Deutschland (2022): Probabilistische Modelle wie Lasso, GAMLSS und neuronale Netze zur kurzfristigen Preisprognose (30min). Punktprognosen nicht deutlich besser als Intraday-Preis, aber deutlich bessere Konfidenzintervalle.
	•	Irland (2024): Vergleich von ARX, XGBoost, LSTM; LEAR (Lasso Estimated AR) bestes Modell. Open-Source verfügbar.
	•	Belgien/UK: Klassifikation des Systemzustands (lang/kurz) und darauf aufbauende Preisverteilung. Kombiniert Klassifikation mit Regression.
	•	GitHub-Projekte: Repos zur Prognose von Ausgleichsenergie in DE mit Keras, XGBoost, GRU, LSTM.

Modellierungsansätze und Unsicherheitsabschätzung

Tabelle 2: Modellübersicht

Modell	Beschreibung	Unsicherheitsabschätzung
Gradient Boosted Trees (XGBoost, LightGBM)	Hohe Genauigkeit, Feature-Importanz	Quantile-Loss, NGBoost, Bootstraps
Random Forest	Robust, einfach	Quantile Forest, Jackknife+
ARIMA/SARIMAX	Transparent, für starke Autokorrelation	analytische Intervalle, Residuen-Bootstrap
Prophet	Additives Modell mit Feiertagseffekten	Bayesian Sampling der Komponenten
GAMLSS	Modelliert örtliche & skalierte Parameter	Verteilung als Funktion der Regressoren
LSTM/TFT	Sequenzmodell, nichtlinear	Monte Carlo Dropout, Ensembles, Verteilungsoutput
Bayesian Regression/BART	Modelliert Posterior-Unsicherheit direkt	Credible Intervals, MCMC Sampling

Tools & Frameworks (Open Source)
	•	Daten: pandas, entsoe-py, requests, xml, holidays
	•	Feature Engineering: scikit-learn, tsfresh, Featuretools
	•	Modelle: xgboost, lightgbm, statsmodels, prophet, PyMC, pytorch-forecasting
	•	Evaluierung: scikit-learn, properscoring, sktime, scipy
	•	Visualisierung: matplotlib, seaborn, plotly, SHAP, Bokeh

Validierung, Interpretierbarkeit und Präsentation

Validierung
	•	Walk-forward Cross-Validation
	•	MAE, RMSE, MAPE, CRPS, Coverage von Intervallen
	•	Vergleich mit Benchmarks (z.B. Day-Ahead-Preis)

Interpretierbarkeit
	•	Feature Importance, SHAP-Werte
	•	PDP/ICE-Plots
	•	Zerlegung (z.B. bei Prophet: Trend, Saisonalität)

GitHub-Präsentation
	•	Struktur: README, Jupyter-Notebooks, requirements.txt
	•	Visualisierung von Forecast vs. Ist inkl. Intervalle
	•	Lizenz: z.B. MIT oder Apache 2.0

Wissenschaftliche Präsentation
	•	Motivation & Marktmechanismus
	•	Daten, Modell, Resultate, Unsicherheiten
	•	Fallstudien mit hoher/niedriger Modellgenauigkeit
	•	Fazit: Modell zeigt Unsicherheit an, liefert robuste Vorhersagen

Fazit

Dieser Leitfaden stellt eine komplette Grundlage zur Entwicklung eines Vorhersagemodells für Ausgleichsenergiepreise in der Schweiz bereit. Ziel ist nicht nur eine präzise Prognose, sondern die transparente Darstellung von Unsicherheit. Mittels öffentlicher Daten und Open-Source-Werkzeugen kann ein reproduzierbares, dokumentiertes System entstehen, das sowohl für Netzbetreiber als auch Marktteilnehmer echten Mehrwert bietet.