# Atyrau weather

Put this file here:

    atyrau_open-meteo_47.12N_51.92E_2025-01-01_2026-11-13.csv

It is the hourly ERA5 reanalysis from Open-Meteo for 47.12 N, 51.92 E (Atyrau), 1 Jan 2025 to 13 Nov 2026
(columns: time, temperature_2m, relative humidity, wind speed). It was downloaded to the Downloads folder.

`model/run_losses.py` looks for it here (and in the catalyst folder) and builds the hour counts from it.
If the file is missing, the script uses hour counts that were made from the same download, so the
results are the same; the CSV just lets anyone check them.
