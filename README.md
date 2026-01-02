# Expense Tracker - Gestione Note Spese e Chilometriche

Applicazione web PWA completa per la gestione di note spese, chilometriche, clienti e progetti.

## 🚀 Caratteristiche

- 📸 **Scansione ricevute** con OCR automatico (Google Vision API)
- 💶 **Gestione spese** con categorizzazione e flag addebitabili
- 🚗 **Chilometriche** con calcolo rimborsi automatico (tariffe ACI/custom)
- 👥 **Gestione clienti e progetti**
- 📊 **Dashboard** con statistiche e grafici
- 📥 **Export Excel/PDF** per commercialista
- 📱 **PWA** - funziona su PC e installabile come app su Android
- 🔄 **Funzionalità offline** (service worker)

## 📋 Prerequisiti

- Python 3.9+
- Account Supabase (gratuito - https://supabase.com)
- Account Google Cloud con Vision API abilitata (1000 richieste/mese gratis)
- (Opzionale) Account Render/Railway per deploy

## ⚙️ Setup Locale

### 1. Clona repository e installa dipendenze

```bash
cd expense_tracker
pip install -r requirements.txt
```

### 2. Configura Supabase

1. Crea un nuovo progetto su https://supabase.com
2. Nel SQL Editor, esegui tutto il contenuto di `database/schema.sql`
3. Vai su Settings > API e copia:
   - Project URL
   - anon/public key
   - service_role key

4. Vai su Storage e crea un bucket chiamato `expenses` (pubblico)

### 3. Configura Google Cloud Vision API

1. Vai su https://console.cloud.google.com
2. Crea un nuovo progetto
3. Abilita "Cloud Vision API"
4. Vai su "Credentials" > "Create Credentials" > "Service Account"
5. Scarica il file JSON delle credenziali
6. Salva il file come `google-credentials.json` nella root del progetto

### 4. Configura variabili ambiente

Crea un file `.env` copiando `.env.example`:

```bash
cp .env.example .env
```

Modifica `.env` con i tuoi valori:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
FLASK_SECRET_KEY=genera-una-chiave-random-qui
```

### 5. Avvia applicazione

```bash
python app.py
```

L'applicazione sarà disponibile su `http://localhost:5000`

Apri il browser e vai su `http://localhost:5000/static/index.html`

## 📱 Installazione come App su Android

1. Apri l'applicazione nel browser Chrome su Android
2. Tocca il menu (3 puntini) > "Installa app" o "Aggiungi a schermata Home"
3. Segui le istruzioni per installare
4. L'app apparirà nel drawer come app nativa

## 🌐 Deploy su Render (Gratuito)

### 1. Prepara repository GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tuousername/expense-tracker.git
git push -u origin main
```

### 2. Crea Web Service su Render

1. Vai su https://render.com e registrati
2. Dashboard > New > Web Service
3. Connetti il tuo repository GitHub
4. Configura:
   - **Name**: expense-tracker
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free

### 3. Aggiungi variabili ambiente

In "Environment" aggiungi tutte le variabili dal tuo `.env`:

```
SUPABASE_URL=...
SUPABASE_KEY=...
SUPABASE_SERVICE_KEY=...
FLASK_SECRET_KEY=...
```

Per Google Credentials, copia il contenuto del file JSON in una variabile:
```
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

E modifica `app.py` per usare le credenziali da variabile ambiente invece che da file.

### 4. Deploy

Render farà automaticamente il deploy. L'app sarà disponibile su:
`https://expense-tracker.onrender.com`

## 📊 Struttura Database

### Tabelle Principali

- **categorie**: Categorie spese (Pedaggi, Ristoranti, etc)
- **clienti**: Anagrafica clienti
- **progetti**: Progetti/commesse per cliente
- **veicoli**: Veicoli per chilometriche
- **spese**: Registrazione spese con OCR e immagini
- **chilometriche**: Viaggi con calcolo rimborsi

### Relazioni

```
clienti
  └── progetti
      ├── spese
      └── chilometriche

categorie
  └── spese

veicoli
  └── chilometriche
```

## 🎯 Utilizzo

### Dashboard
- Visualizza statistiche mese corrente
- Grafici spese per categoria
- Ultime spese inserite

### Spese
1. Click "➕ Nuova Spesa"
2. (Opzionale) Scansiona ricevuta per compilazione automatica
3. Compila campi: data, importo, categoria, descrizione
4. Seleziona cliente/progetto se addebitabile
5. Spunta "Addebitabile al cliente" se necessario
6. Salva

### Chilometriche
1. Click "➕ Nuovo Viaggio"
2. Seleziona veicolo (tariffa compilata automaticamente)
3. Inserisci partenza, arrivo, km
4. Rimborso calcolato automaticamente
5. Seleziona cliente se addebitabile
6. Salva

### Report
- Filtra per periodo e cliente
- Export Excel per commercialista
- Include spese addebitabili e chilometriche

## 🔧 Personalizzazione

### Aggiungere nuove categorie

Via interfaccia o SQL:
```sql
INSERT INTO categorie (nome, descrizione, colore) 
VALUES ('Formazione', 'Corsi e formazione', '#9C27B0');
```

### Modificare tariffe ACI

Modifica veicolo e aggiorna `tariffa_km_aci` oppure imposta `tariffa_km_custom`.

### Temi colori

Modifica `static/styles.css`:
```css
:root {
    --primary-color: #4472C4;  /* Cambia questo */
    ...
}
```

## 🐛 Troubleshooting

### OCR non funziona
- Verifica che Google Vision API sia abilitata
- Controlla che le credenziali siano corrette
- Verifica quota gratuita non esaurita (1000 richieste/mese)

### Database connection error
- Verifica URL e KEY Supabase corrette
- Controlla che lo schema SQL sia stato eseguito
- Verifica connessione internet

### PWA non si installa
- Serve HTTPS (in locale va bene HTTP)
- Manifest.json deve essere accessibile
- Service worker deve registrarsi correttamente

### Export Excel non funziona
- Verifica che openpyxl sia installato
- Controlla permessi scrittura

## 📝 TODO / Future Features

- [ ] Notifiche push per scadenze
- [ ] Multi-utente con autenticazione
- [ ] App nativa Android/iOS
- [ ] Sincronizzazione automatica Dropbox
- [ ] Riconoscimento categorie automatico con AI
- [ ] Report PDF personalizzati
- [ ] Dashboard mobile ottimizzata
- [ ] Dark mode
- [ ] Backup automatico database

## 📄 Licenza

Progetto personale - Uso libero

## 🤝 Supporto

Per problemi o domande, apri una Issue su GitHub.

---

**Versione**: 1.0.0  
**Autore**: GB  
**Data**: Gennaio 2026
