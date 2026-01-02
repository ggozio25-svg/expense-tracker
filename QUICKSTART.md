# 🚀 Quick Start - Expense Tracker

Guida rapida per partire in 5 minuti!

## ⚡ Setup Veloce (Locale)

### 1. Installa dipendenze
```bash
cd expense_tracker
pip install -r requirements.txt
```

### 2. Setup Supabase (3 minuti)

1. Vai su https://supabase.com e crea account
2. Crea nuovo progetto (nome: expense-tracker)
3. Aspetta che si inizializzi
4. Vai su **SQL Editor** > **New Query**
5. Copia e incolla TUTTO il contenuto di `database/schema.sql`
6. Premi **Run**
7. Vai su **Storage** > **New Bucket** > Nome: `expenses` > **Public bucket**: ✓
8. Vai su **Settings** > **API**
9. Copia:
   - Project URL
   - anon public key

### 3. Setup Google Vision (2 minuti)

1. Vai su https://console.cloud.google.com
2. Crea nuovo progetto o seleziona esistente
3. Vai su **APIs & Services** > **Library**
4. Cerca "Cloud Vision API" > **Enable**
5. Vai su **Credentials** > **Create Credentials** > **Service Account**
6. Nome: expense-tracker > **Create**
7. Salta permessi > **Done**
8. Clicca sul service account creato > **Keys** > **Add Key** > **JSON**
9. Salva il file scaricato come `google-credentials.json` nella root del progetto

### 4. Configura .env

```bash
cp .env.example .env
nano .env  # o usa il tuo editor preferito
```

Modifica con i tuoi valori:
```env
SUPABASE_URL=https://tuoprogetto.supabase.co
SUPABASE_KEY=eyJhbGc...tuakey
SUPABASE_SERVICE_KEY=eyJhbGc...tuaservicekey
GOOGLE_APPLICATION_CREDENTIALS=./google-credentials.json
FLASK_SECRET_KEY=chiave-segreta-random-qui
```

### 5. Avvia!

```bash
python app.py
```

Apri browser: `http://localhost:5000/static/index.html`

## ✅ Verifica Funzionamento

1. **Dashboard**: Vedi 4 card con statistiche (tutte a 0)
2. **Clienti**: Crea un cliente di test
3. **Veicoli**: Aggiungi un veicolo (es: tua auto)
4. **Spese**: Crea una spesa
5. **Chilometriche**: Aggiungi un viaggio
6. **Dashboard**: Verifica aggiornamento statistiche

## 🐛 Problemi Comuni

### "Connection refused"
- Verifica che Supabase URL sia corretto
- Controlla connessione internet

### "Google Vision error"
- Verifica che API sia abilitata
- Controlla che file JSON credenziali sia nella root
- Verifica path in GOOGLE_APPLICATION_CREDENTIALS

### "Tabelle non trovate"
- Esegui di nuovo `schema.sql` in Supabase SQL Editor
- Verifica che tutte le query siano eseguite con successo

### "PWA non si installa"
- Usa Chrome/Edge su Android
- In locale HTTP va bene, in produzione serve HTTPS
- Verifica che manifest.json sia accessibile

## 📱 Test su Smartphone

1. Assicurati che PC e smartphone siano sulla stessa rete WiFi
2. Trova IP del PC: 
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` o `ip addr`
3. Sul telefono apri: `http://IP_DEL_PC:5000/static/index.html`
4. Esempio: `http://192.168.1.100:5000/static/index.html`

## 🌐 Deploy Veloce su Render

### Opzione 1: Auto Deploy da GitHub

1. Pusha codice su GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tuousername/expense-tracker.git
   git push -u origin main
   ```

2. Su Render.com:
   - New > Web Service
   - Connect GitHub repo
   - Name: expense-tracker
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
   - Instance: Free

3. Aggiungi Environment Variables (copia da .env)

4. Deploy! (3-5 minuti)

### Opzione 2: Deploy Manuale

```bash
# Installa Render CLI
npm install -g @render/cli

# Login
render login

# Deploy
render deploy
```

## 🎯 Prossimi Passi

Dopo il setup base:

1. **Personalizza categorie**: Aggiungi/modifica categorie in base alle tue esigenze
2. **Importa clienti**: Crea i tuoi clienti reali
3. **Configura veicoli**: Aggiungi i tuoi veicoli con tariffe corrette
4. **Testa OCR**: Fai una foto a una ricevuta vera e verifica estrazione dati
5. **Export**: Prova export Excel per commercialista
6. **Icone Custom**: Sostituisci icone placeholder con design professionale

## 💡 Tips

- **Backup database**: Export da Supabase > Database > Backups (automatico giornaliero)
- **Limiti gratuiti**:
  - Supabase: 500MB database, 1GB storage, 2GB bandwidth/mese
  - Google Vision: 1000 richieste/mese
  - Render: 750h/mese, sleep dopo 15min inattività
- **Costi stimati** oltre free tier:
  - Supabase Pro: $25/mese (8GB database, 100GB storage)
  - Google Vision: ~$1.50/1000 immagini aggiuntive
  - Render: $7/mese (no sleep, 1GB RAM)

## 🆘 Supporto

Problemi? Controlla:
1. Logs dell'applicazione nella console
2. Browser DevTools > Console per errori frontend
3. Supabase Dashboard > Database > Logs
4. README.md completo per dettagli

---

**Tempo setup totale stimato**: 10-15 minuti  
**Tempo primo deploy**: 20-30 minuti
