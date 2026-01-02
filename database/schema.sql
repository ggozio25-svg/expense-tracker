-- Schema Database per Expense Tracker
-- Database: PostgreSQL (Supabase)

-- Tabella Categorie Spese
CREATE TABLE categorie (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    descrizione TEXT,
    colore VARCHAR(7) DEFAULT '#6B7280',
    attiva BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserimento categorie predefinite
INSERT INTO categorie (nome, descrizione, colore) VALUES
    ('Pedaggi', 'Spese per pedaggi autostradali', '#3B82F6'),
    ('Chilometriche', 'Rimborsi chilometrici', '#10B981'),
    ('Interventi', 'Manutenzioni e interventi tecnici', '#F59E0B'),
    ('Ristoranti', 'Vitto e pasti', '#EF4444'),
    ('Alberghi', 'Pernottamenti e alloggi', '#8B5CF6'),
    ('Carburante', 'Rifornimenti carburante', '#EC4899'),
    ('Materiali', 'Materiali e ricambi', '#14B8A6'),
    ('Altre Spese', 'Spese varie', '#6B7280');

-- Tabella Clienti
CREATE TABLE clienti (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    codice VARCHAR(50) UNIQUE,
    indirizzo TEXT,
    citta VARCHAR(100),
    cap VARCHAR(10),
    provincia VARCHAR(2),
    partita_iva VARCHAR(20),
    codice_fiscale VARCHAR(16),
    email VARCHAR(100),
    telefono VARCHAR(20),
    note TEXT,
    attivo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Progetti/Commesse
CREATE TABLE progetti (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE CASCADE,
    codice VARCHAR(50) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descrizione TEXT,
    data_inizio DATE,
    data_fine DATE,
    budget DECIMAL(10,2),
    stato VARCHAR(20) DEFAULT 'attivo' CHECK (stato IN ('attivo', 'completato', 'sospeso', 'annullato')),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Veicoli
CREATE TABLE veicoli (
    id SERIAL PRIMARY KEY,
    targa VARCHAR(20) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL, -- Auto, Moto, Furgone, etc
    marca VARCHAR(50),
    modello VARCHAR(50),
    anno INTEGER,
    tariff_km_aci DECIMAL(5,3) DEFAULT 0.680, -- Tariffa ACI standard
    tariffa_km_custom DECIMAL(5,3), -- Tariffa personalizzata
    usa_tariffa_custom BOOLEAN DEFAULT false,
    note TEXT,
    attivo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Spese
CREATE TABLE spese (
    id SERIAL PRIMARY KEY,
    data_spesa DATE NOT NULL,
    categoria_id INTEGER REFERENCES categorie(id) ON DELETE SET NULL,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE SET NULL,
    progetto_id INTEGER REFERENCES progetti(id) ON DELETE SET NULL,
    importo DECIMAL(10,2) NOT NULL,
    descrizione TEXT NOT NULL,
    fornitore VARCHAR(200),
    numero_documento VARCHAR(50),
    addebitabile BOOLEAN DEFAULT false,
    addebitata BOOLEAN DEFAULT false, -- Flag per tracciare se già fatturata
    note TEXT,
    immagine_url TEXT, -- URL immagine ricevuta su Supabase Storage
    ocr_data JSONB, -- Dati estratti dall'OCR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella Chilometriche
CREATE TABLE chilometriche (
    id SERIAL PRIMARY KEY,
    data_viaggio DATE NOT NULL,
    veicolo_id INTEGER REFERENCES veicoli(id) ON DELETE SET NULL,
    cliente_id INTEGER REFERENCES clienti(id) ON DELETE SET NULL,
    progetto_id INTEGER REFERENCES progetti(id) ON DELETE SET NULL,
    partenza VARCHAR(200) NOT NULL,
    arrivo VARCHAR(200) NOT NULL,
    km_percorsi DECIMAL(8,2) NOT NULL,
    tariffa_applicata DECIMAL(5,3) NOT NULL,
    rimborso_calcolato DECIMAL(10,2) NOT NULL,
    addebitabile BOOLEAN DEFAULT false,
    addebitata BOOLEAN DEFAULT false,
    descrizione TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indici per performance
CREATE INDEX idx_spese_data ON spese(data_spesa);
CREATE INDEX idx_spese_cliente ON spese(cliente_id);
CREATE INDEX idx_spese_progetto ON spese(progetto_id);
CREATE INDEX idx_spese_categoria ON spese(categoria_id);
CREATE INDEX idx_spese_addebitabile ON spese(addebitabile);
CREATE INDEX idx_chilometriche_data ON chilometriche(data_viaggio);
CREATE INDEX idx_chilometriche_veicolo ON chilometriche(veicolo_id);
CREATE INDEX idx_chilometriche_cliente ON chilometriche(cliente_id);
CREATE INDEX idx_progetti_cliente ON progetti(cliente_id);

-- Funzione per aggiornare updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per aggiornare automaticamente updated_at
CREATE TRIGGER update_clienti_updated_at BEFORE UPDATE ON clienti
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_progetti_updated_at BEFORE UPDATE ON progetti
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_spese_updated_at BEFORE UPDATE ON spese
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chilometriche_updated_at BEFORE UPDATE ON chilometriche
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View per report spese per cliente
CREATE VIEW v_spese_cliente AS
SELECT 
    c.id as cliente_id,
    c.nome as cliente_nome,
    cat.nome as categoria,
    p.nome as progetto,
    s.data_spesa,
    s.importo,
    s.descrizione,
    s.addebitabile,
    s.addebitata,
    s.fornitore
FROM spese s
LEFT JOIN clienti c ON s.cliente_id = c.id
LEFT JOIN categorie cat ON s.categoria_id = cat.id
LEFT JOIN progetti p ON s.progetto_id = p.id;

-- View per totali mensili
CREATE VIEW v_totali_mensili AS
SELECT 
    EXTRACT(YEAR FROM data_spesa) as anno,
    EXTRACT(MONTH FROM data_spesa) as mese,
    cat.nome as categoria,
    COUNT(*) as num_spese,
    SUM(importo) as totale,
    SUM(CASE WHEN addebitabile THEN importo ELSE 0 END) as totale_addebitabile
FROM spese s
LEFT JOIN categorie cat ON s.categoria_id = cat.id
GROUP BY anno, mese, cat.nome;

-- View per km totali per veicolo
CREATE VIEW v_km_veicolo AS
SELECT 
    v.targa,
    v.marca,
    v.modello,
    EXTRACT(YEAR FROM ch.data_viaggio) as anno,
    EXTRACT(MONTH FROM ch.data_viaggio) as mese,
    COUNT(*) as num_viaggi,
    SUM(ch.km_percorsi) as km_totali,
    SUM(ch.rimborso_calcolato) as rimborso_totale
FROM chilometriche ch
JOIN veicoli v ON ch.veicolo_id = v.id
GROUP BY v.targa, v.marca, v.modello, anno, mese;
