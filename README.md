# Dashboard Analisi Taglie

Dashboard interattiva per l'analisi incrociata di Acquisti e Vendite, progettata per ottimizzare la gestione dello stock per taglia.

Costruita con [Streamlit](https://streamlit.io/), [Pandas](https://pandas.pydata.org/) e [Plotly](https://plotly.com/).

---

## Funzionalità

### Caricamento dati
- Seleziona un file Excel già presente nella cartella `Dati Excel/` (utile su [Streamlit Community Cloud](https://streamlit.io/cloud) con push su GitHub)
- Oppure carica un file manualmente dal computer
- Bottone **← Nuova Analisi** per cambiare file senza riavviare l'app

### Filtri dinamici
- **Linea** — filtro multiselect
- **Categoria** — filtro multiselect
- **Stagione** — filtro multiselect
- **Taglia** — filtro multiselect, ordinamento standard (taglie baby → bambini → adulti) + alfabetico per taglie non standard
- **Produttore** — filtro multiselect
- **Data** — filtri gerarchici anno → trimestre → mese → giorno

### KPI
- Totale Acquistato
- Totale Venduto
- Sell-Through % (percentuale venduto su acquistato)
- Numero di taglie attive analizzate

### Grafici
- **Andamento per Taglia (Barre)** — barre raggruppate acquisti/vendite per taglia
- **Trend Quantità (Linee)** — linea acquisti + linea vendute per taglia

### Matrice dati dettagliata
- Tabella interattiva con dati aggregati per Taglia e Stagione
- Colonne quantità arrotondate a interi
- Sell-Through % con formattazione condizionale (verde ≥ 70%, giallo 30–69%, rosso < 30%)

---

## Formato file richiesto

File **.xlsx** con due fogli:

| Foglio | Contenuto |
|--------|-----------|
| **VEND** | Vendite — deve contenere colonne: `Data Vendita`, `Linea`, `Categoria`, `Stagione`, `Taglia`, `Produttore`, `Quantità Venduta` |
| **ACQ** | Acquisti — deve contenere colonne: `Data Acquisto`, `Linea`, `Categoria`, `Stagione`, `Taglia`, `Produttore`, `Quantità Acquistata` |

---

## Installazione ed esecuzione locale

### Prerequisiti
- Python **3.10+**
- Git

### Passaggi

```bash
# 1. Clona il repository
git clone https://github.com/tuo-utente/tuo-repo.git
cd tuo-repo

# 2. Crea un ambiente virtuale
python -m venv venv

# 3. Attiva l'ambiente virtuale
#   Windows:
venv\Scripts\activate
#   macOS / Linux:
source venv/bin/activate

# 4. Installa le dipendenze
pip install -r requirements.txt

# 5. Metti i tuoi file Excel nella cartella Dati Excel/
# (creala se non esiste)

# 6. Avvia l'app
streamlit run dashboard.py
```

L'app si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`.

---

## Deploy su Streamlit Community Cloud

1. Push del repository su GitHub
2. Vai su [share.streamlit.io](https://share.streamlit.io/)
3. Clicca **Deploy an app**
4. Seleziona il repository, branch e imposta `dashboard.py` come entry point
5. Per caricare nuovi dati: aggiungi il file `.xlsx` in `Dati Excel/`, fai commit e push → Streamlit si redeploya automaticamente, il file sarà selezionabile dal dropdown

---

## Struttura del progetto

```
├── dashboard.py          # Entry point Streamlit (UI + layout)
├── data_engine.py        # Logica dati (caricamento, filtri, aggregazioni)
├── style.css             # Stile personalizzato (Inter font, bento-grid)
├── requirements.txt      # Dipendenze Python
├── Dati Excel/           # Cartella per i file Excel
│   └── Analisi Fitness Adidas Taglie.xlsx   # File di esempio
└── README.md
```

---

## Tecnologie

- **Streamlit** — interfaccia web interattiva
- **Pandas** — manipolazione e aggregazione dati
- **Plotly** — grafici interattivi
- **openpyxl** — lettura file Excel
