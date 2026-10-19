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
5. Scegliere la modalità di generazione:
   - `Appuntamenti per capogruppo Delegato` per un PDF per ogni riga;
   - `Appuntamenti per capogruppo Volontario` per un PDF per ogni volontario con tutti i suoi appuntamenti.
6. Premere **Genera PDF**.

Nella cartella scelta vengono creati:

- nella modalità delegato, un file
  `Appuntamento-Referente-Gruppo-Codice-Gruppo-riga-N.pdf` per ogni riga non
  vuota del foglio;
- nella modalità volontario, un file `Volontario-Nome-Completo-...pdf` per ogni
  volontario distinto, con tutti i suoi appuntamenti;
- `Guida-uso.pdf`, con le istruzioni per l'operatore.

Ogni appuntamento del PDF volontario riporta codice gruppo principale,
eventuale gruppo unito, capogruppo delegato con telefono, Sala del Regno,
numero e auto degli ospiti, data, fascia e note. Non riporta i dati del
volontario assegnato all'altra fascia. Se più volontari sono nella stessa
fascia dello stesso appuntamento, il PDF di ciascuno indica anche gli altri
volontari presenti.

Non è necessario installare Python.

## Formato Excel previsto

Il primo foglio deve avere due righe di intestazione:

- prima riga: `Codice Gruppo`, `Referente Gruppo`, `Telefono Referente`,
  `Sala del Regno`, `N. Ospiti`, `Auto Ospiti`, seguiti dai blocchi data come
  `26/10 (Lunedì)`;
- seconda riga, per ogni data: `Mattina`, `Pomeriggio`, `UNIONI`.

Se un file contiene anche una colonna `NOTE` nel blocco giornaliero, il suo
contenuto viene ancora riportato nei PDF.

Le celle Mattina e Pomeriggio possono contenere un accompagnatore nel formato:

```text
NOME COMPLETO NUMERO_TELEFONO
```

Il numero di telefono deve essere l'ultimo elemento e deve contenere soltanto
cifre. Tutto il testo che lo precede viene considerato il nome completo, senza
tentare di separare nome e cognome.

Se più volontari condividono la stessa fascia, separarli esclusivamente con
un punto e virgola:

```text
ROSSI MARIO 0000000001; VERDI PAOLO 0000000002
```

In modalità volontario l'appuntamento viene inserito nel PDF di ciascuna
persona, senza creare un unico PDF con i nomi combinati. Il vecchio formato
`COGNOME, NOME: NUMERO_TELEFONO` e gli altri separatori non sono accettati.

La colonna `UNIONI` può essere vuota oppure contenere un solo codice in una
delle forme seguenti:

```text
UNITO0000001
(include UNITO0000001)
(aggregato UNITO0000001)
```

Il codice unito si applica sia alla Mattina sia al Pomeriggio di quel giorno e
viene mostrato, insieme al codice gruppo principale, nei PDF delegato e
volontario. `Telefono Referente` viene mostrato in entrambi i tipi di PDF.

Se il programma trova celle non valide, blocca la generazione e mostra tutti
gli errori insieme. Nella GUI i dettagli sono nel riquadro **Log elaborazione**;
da terminale vengono scritti su `stderr`. Ogni errore indica foglio, cella,
riga, giorno e campo, senza ripetere il contenuto sensibile della cella.

## Protezione dei dati

Tutti i file `.xlsx` sotto `assets/` sono esclusi da Git. Test e automazioni
usano esclusivamente dati sintetici creati in cartelle temporanee.

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

Per generare il flusso standard per delegati:

```bash
python main.py --input "/percorso/appuntamenti.xlsx" --output "/percorso/pdf" --mode delegato
```

Per generare invece il flusso per volontario:

```bash
python main.py --input "/percorso/appuntamenti.xlsx" --output "/percorso/pdf" --mode volontario
```

La modalità volontario considera uguali le occorrenze con lo stesso nome
completo e telefono, ignorando differenze di maiuscole e spazi.

Per generare soltanto la guida:

```bash
python main.py --guide-only "Guida-uso.pdf"
```

## Test

```bash
python -m pytest
```

La suite verifica parser, celle unite e header su due righe, formato dei
volontari, UNIONI, generazione e contenuto dei PDF, log degli errori, assenza
di output parziali, GUI, CLI e configurazione del pacchetto Windows.

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
