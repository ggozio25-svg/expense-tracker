"""
Script per popolare il database con dati demo
Utile per testing e demo dell'applicazione

ATTENZIONE: Questo script inserisce dati di esempio.
Usare solo su database di test!

Uso: python populate_demo_data.py
"""

from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import random

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

def clear_demo_data():
    """Pulisce tutti i dati (ATTENZIONE!)"""
    print("⚠️  ATTENZIONE: Questo eliminerà TUTTI i dati!")
    confirm = input("Sei sicuro? Scrivi 'DELETE ALL' per confermare: ")
    
    if confirm != 'DELETE ALL':
        print("Operazione annullata.")
        return False
    
    print("\nPulizia dati in corso...")
    
    try:
        supabase.table('chilometriche').delete().neq('id', 0).execute()
        supabase.table('spese').delete().neq('id', 0).execute()
        supabase.table('progetti').delete().neq('id', 0).execute()
        supabase.table('veicoli').delete().neq('id', 0).execute()
        supabase.table('clienti').delete().neq('id', 0).execute()
        
        print("✓ Dati puliti")
        return True
    except Exception as e:
        print(f"✗ Errore: {e}")
        return False

def populate_clienti():
    """Popola clienti demo"""
    print("\n📋 Popolamento clienti...")
    
    clienti = [
        {
            'nome': 'Acqua Minerale SpA',
            'codice': 'CLI001',
            'partita_iva': '12345678901',
            'email': 'info@acquaminerale.it',
            'telefono': '+39 030 1234567',
            'citta': 'Brescia',
            'provincia': 'BS'
        },
        {
            'nome': 'Detergenti Industriali SRL',
            'codice': 'CLI002',
            'partita_iva': '98765432109',
            'email': 'ordini@detergenti.it',
            'telefono': '+39 030 7654321',
            'citta': 'Bergamo',
            'provincia': 'BG'
        },
        {
            'nome': 'Chimica Pulita SRL',
            'codice': 'CLI003',
            'partita_iva': '11223344556',
            'email': 'info@chimicapulita.it',
            'telefono': '+39 030 9988776',
            'citta': 'Milano',
            'provincia': 'MI'
        }
    ]
    
    ids = []
    for cliente in clienti:
        result = supabase.table('clienti').insert(cliente).execute()
        ids.append(result.data[0]['id'])
        print(f"  ✓ {cliente['nome']}")
    
    return ids

def populate_progetti(cliente_ids):
    """Popola progetti demo"""
    print("\n📁 Popolamento progetti...")
    
    progetti = [
        {
            'cliente_id': cliente_ids[0],
            'codice': 'PRJ-2024-001',
            'nome': 'Manutenzione Linea Imbottigliamento 1',
            'data_inizio': '2024-01-01',
            'stato': 'attivo'
        },
        {
            'cliente_id': cliente_ids[1],
            'codice': 'PRJ-2024-002',
            'nome': 'Installazione Mixer Detergenti',
            'data_inizio': '2024-02-15',
            'stato': 'attivo'
        },
        {
            'cliente_id': cliente_ids[2],
            'codice': 'PRJ-2024-003',
            'nome': 'Upgrade Sistema PLC',
            'data_inizio': '2024-03-01',
            'stato': 'completato'
        }
    ]
    
    ids = []
    for progetto in progetti:
        result = supabase.table('progetti').insert(progetto).execute()
        ids.append(result.data[0]['id'])
        print(f"  ✓ {progetto['nome']}")
    
    return ids

def populate_veicoli():
    """Popola veicoli demo"""
    print("\n🚗 Popolamento veicoli...")
    
    veicoli = [
        {
            'targa': 'AB123CD',
            'tipo': 'Auto',
            'marca': 'Volkswagen',
            'modello': 'Golf',
            'anno': 2020,
            'tariffa_km_aci': 0.680,
            'usa_tariffa_custom': False
        },
        {
            'targa': 'EF456GH',
            'tipo': 'Furgone',
            'marca': 'Fiat',
            'modello': 'Ducato',
            'anno': 2019,
            'tariffa_km_aci': 0.850,
            'tariffa_km_custom': 0.900,
            'usa_tariffa_custom': True
        }
    ]
    
    ids = []
    for veicolo in veicoli:
        result = supabase.table('veicoli').insert(veicolo).execute()
        ids.append(result.data[0]['id'])
        print(f"  ✓ {veicolo['targa']} - {veicolo['marca']} {veicolo['modello']}")
    
    return ids

def populate_spese(cliente_ids, progetto_ids):
    """Popola spese demo"""
    print("\n💶 Popolamento spese...")
    
    # Ottieni ID categorie
    categorie = supabase.table('categorie').select('id, nome').execute()
    cat_map = {cat['nome']: cat['id'] for cat in categorie.data}
    
    oggi = datetime.now()
    spese = []
    
    # Genera 30 spese negli ultimi 90 giorni
    for i in range(30):
        giorni_fa = random.randint(0, 90)
        data = (oggi - timedelta(days=giorni_fa)).strftime('%Y-%m-%d')
        
        # Scegli categoria random
        categoria_nome = random.choice(list(cat_map.keys()))
        
        # Importi realistici per categoria
        importi = {
            'Pedaggi': (5, 30),
            'Ristoranti': (15, 60),
            'Alberghi': (80, 150),
            'Carburante': (40, 90),
            'Materiali': (50, 500),
            'Interventi': (100, 1000),
            'Altre Spese': (10, 100)
        }
        
        min_importo, max_importo = importi.get(categoria_nome, (10, 100))
        importo = round(random.uniform(min_importo, max_importo), 2)
        
        # 60% delle spese sono addebitabili
        addebitabile = random.random() < 0.6
        
        spesa = {
            'data_spesa': data,
            'categoria_id': cat_map[categoria_nome],
            'importo': importo,
            'descrizione': f'{categoria_nome} - {data}',
            'addebitabile': addebitabile
        }
        
        # 70% delle spese hanno cliente/progetto
        if random.random() < 0.7:
            spesa['cliente_id'] = random.choice(cliente_ids)
            spesa['progetto_id'] = random.choice(progetto_ids)
        
        # Alcuni con fornitore
        if random.random() < 0.5:
            spesa['fornitore'] = f'Fornitore {random.randint(1, 10)}'
        
        spese.append(spesa)
    
    for spesa in spese:
        supabase.table('spese').insert(spesa).execute()
    
    print(f"  ✓ Inserite {len(spese)} spese")

def populate_chilometriche(veicolo_ids, cliente_ids, progetto_ids):
    """Popola chilometriche demo"""
    print("\n🚗 Popolamento chilometriche...")
    
    luoghi = [
        ('Gussago', 'Brescia'),
        ('Brescia', 'Milano'),
        ('Milano', 'Bergamo'),
        ('Bergamo', 'Brescia'),
        ('Gussago', 'Verona'),
        ('Brescia', 'Mantova')
    ]
    
    oggi = datetime.now()
    viaggi = []
    
    # Genera 20 viaggi negli ultimi 60 giorni
    for i in range(20):
        giorni_fa = random.randint(0, 60)
        data = (oggi - timedelta(days=giorni_fa)).strftime('%Y-%m-%d')
        
        veicolo = random.choice(veicolo_ids)
        partenza, arrivo = random.choice(luoghi)
        km = round(random.uniform(20, 200), 1)
        
        # Ottieni tariffa veicolo
        veicolo_data = supabase.table('veicoli').select('*').eq('id', veicolo).single().execute()
        tariffa = float(veicolo_data.data['tariffa_km_custom']) if veicolo_data.data['usa_tariffa_custom'] \
                  else float(veicolo_data.data['tariffa_km_aci'])
        
        rimborso = round(km * tariffa, 2)
        
        viaggio = {
            'data_viaggio': data,
            'veicolo_id': veicolo,
            'partenza': partenza,
            'arrivo': arrivo,
            'km_percorsi': km,
            'tariffa_applicata': tariffa,
            'rimborso_calcolato': rimborso,
            'addebitabile': random.random() < 0.7
        }
        
        # 80% ha cliente/progetto
        if random.random() < 0.8:
            viaggio['cliente_id'] = random.choice(cliente_ids)
            viaggio['progetto_id'] = random.choice(progetto_ids)
        
        viaggi.append(viaggio)
    
    for viaggio in viaggi:
        supabase.table('chilometriche').insert(viaggio).execute()
    
    print(f"  ✓ Inseriti {len(viaggi)} viaggi")

def main():
    print("="*60)
    print("EXPENSE TRACKER - Popolamento Dati Demo")
    print("="*60)
    
    choice = input("\n1. Popola dati demo (mantiene dati esistenti)\n2. Pulisci TUTTO e popola dati demo\n3. Annulla\n\nScegli (1/2/3): ")
    
    if choice == '3':
        print("Operazione annullata.")
        return
    
    if choice == '2':
        if not clear_demo_data():
            return
    
    print("\n🚀 Inizio popolamento...")
    
    try:
        cliente_ids = populate_clienti()
        progetto_ids = populate_progetti(cliente_ids)
        veicolo_ids = populate_veicoli()
        populate_spese(cliente_ids, progetto_ids)
        populate_chilometriche(veicolo_ids, cliente_ids, progetto_ids)
        
        print("\n" + "="*60)
        print("✅ COMPLETATO!")
        print("="*60)
        print(f"\nClienti:         {len(cliente_ids)}")
        print(f"Progetti:        {len(progetto_ids)}")
        print(f"Veicoli:         {len(veicolo_ids)}")
        print(f"Spese:           ~30")
        print(f"Chilometriche:   ~20")
        print("\nPuoi ora aprire l'applicazione e vedere i dati demo!")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        print("Verifica le credenziali Supabase nel file .env")

if __name__ == '__main__':
    main()
