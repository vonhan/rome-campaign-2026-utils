# Rome Campaign 2026 Utils

Questo progetto genera un PDF per ogni appuntamento del piano di servizio della campagna a Roma 2026, partendo da un file Excel `.xlsx` e producendo documenti leggibili per personale non tecnico.

## Requisiti
- Python 3.11+
- `pip install -r requirements.txt`

## Eseguire in modalità GUI (Windows o Linux)
```bash
python main.py
```

## Eseguire in modalità CLI
```bash
python main.py --input "path/to/file.xlsx" --output "path/to/output"
```

## Distribuzione Windows
Per creare un eseguibile unico:
```bash
pyinstaller --onefile --windowed --name RomeCampaignPDF main.py
```

## Note
- Il file `assets/Abbinamenti DEF.xlsx` non viene versionato nel repository.
- Sono inclusi PDF sintetici di esempio nei test per verificare il comportamento senza usare dati reali.
