# Generatore PDF appuntamenti Roma 2026

Applicazione desktop che legge il foglio Excel degli appuntamenti e crea un PDF
chiaro e stampabile per ogni riga. È pensata per utenti Windows non tecnici, ma
offre anche una modalità da terminale per supporto tecnico e automazioni Linux.

## Download per Windows

Modo consigliato, anche per utenti non tecnici:

1. Aprire la pagina **Releases** del repository.
2. Nell'ultima versione scaricare `RomeCampaignPDF.exe`, `Guida-uso.pdf` e
   `SHA256SUMS.txt`.

Per verificare che l'eseguibile scaricato sia quello pubblicato, aprire
PowerShell nella cartella dei file ed eseguire:

```powershell
Get-FileHash .\RomeCampaignPDF.exe -Algorithm SHA256
```

Il valore visualizzato deve coincidere con quello riportato nella riga
`RomeCampaignPDF.exe` di `SHA256SUMS.txt`. Il controllo non sostituisce la
protezione antivirus, ma rileva download incompleti o modificati.

Alcuni antivirus possono segnalare falsi positivi sugli eseguibili Python
autocontenuti e non firmati. Questa build evita la compressione UPX per ridurre
le segnalazioni euristiche. Se il rilevamento persiste, non disattivare
l'antivirus: comunicare il nome della minaccia, la versione della release e il
produttore dell'antivirus al manutentore del progetto per l'analisi.

In alternativa, per uso tecnico, il pacchetto è disponibile come artifact
`RomeCampaignPDF-Windows` nella pagina della singola esecuzione riuscita della
workflow **Test e pacchetto Windows** (sezione *Artifacts*, in fondo alla run).

## Uso su Windows

1. Salvare `RomeCampaignPDF.exe` in una cartella.
2. Fare doppio clic su `RomeCampaignPDF.exe`. Se Windows mostra un avviso,
   verificare prima il checksum indicato sopra e usare il file solo se
   proviene dalla Release ufficiale.
3. Selezionare il file Excel degli appuntamenti.
4. Selezionare la cartella in cui salvare i documenti.
5. Premere **Genera PDF**.

Nella cartella scelta vengono creati:

- un file `Appuntamento-...pdf` per ogni riga non vuota del foglio;
- `Guida-uso.pdf`, con le istruzioni per l'operatore.

Non è necessario installare Python.

## Formato Excel previsto

Il primo foglio deve avere due righe di intestazione:

- prima riga: `Codice Gruppo`, `Referente Gruppo`, `Sala del Regno`,
  `N. Ospiti`, `Auto Ospiti`, seguiti dai blocchi data come
  `26/10 (Lunedì)`;
- seconda riga, per ogni data: `Mattina`, `Pomeriggio`, `NOTE`.

Le celle Mattina e Pomeriggio possono contenere un accompagnatore nel formato:

```text
COGNOME, NOME: NUMERO_TELEFONO
```

I dati parziali vengono conservati e mostrati senza inventare informazioni
mancanti. Righe con tutti e cinque i campi principali vuoti vengono ignorate.

## Protezione dei dati

Il file reale `assets/Abbinamenti DEF.xlsx` e tutti i file `.xlsx` sotto
`assets/` sono esclusi da Git. Test e automazioni usano esclusivamente dati
sintetici creati in cartelle temporanee.

Non allegare il foglio reale a issue, log o richieste di assistenza. Per
segnalare un problema è sufficiente comunicare il testo dell'errore senza
includere nominativi o numeri di telefono.

## Esecuzione tecnica su Linux

Richiede Python 3.11 o successivo e Tk disponibile nel sistema per la GUI.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --input "/percorso/appuntamenti.xlsx" --output "/percorso/pdf"
```

Per aprire la GUI:

```bash
python main.py
```

Per generare soltanto la guida:

```bash
python main.py --guide-only "Guida-uso.pdf"
```

## Test

```bash
python -m pytest
```

La suite verifica parser, celle unite e header su due righe, parsing degli
accompagnatori, generazione e contenuto dei PDF, gestione degli errori, assenza
di output parziali, CLI e configurazione del pacchetto Windows.

## Build Windows

La workflow `.github/workflows/build-windows.yml` viene eseguita su ogni push a
`main` e può essere avviata manualmente. La workflow:

1. esegue l'intera suite di test;
2. costruisce `RomeCampaignPDF.exe` con PyInstaller;
3. usa l'eseguibile per generare la guida come smoke test;
4. pubblica l'artifact `RomeCampaignPDF-Windows` con eseguibile, guida e README
   solo se tutto riesce.

Build manuale su Windows:

```powershell
python -m pip install -r requirements.txt
python -m pytest
pyinstaller --clean --noconfirm RomeCampaignPDF.spec
```

## Struttura

- `main.py`: entry point GUI/CLI;
- `src/excel_parser.py`: validazione e lettura Excel;
- `src/service.py`: flusso applicativo e pubblicazione atomica dei PDF;
- `src/pdf_generator.py`: layout appuntamenti e guida;
- `src/gui.py`: interfaccia desktop;
- `tests/`: test con sole fixture sintetiche.
