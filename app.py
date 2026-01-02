from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
from google.cloud import vision
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import io
from PIL import Image
import base64
from decimal import Decimal
import json
from google_helper import get_vision_credentials

# Carica variabili ambiente
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 10485760))
CORS(app)

# Inizializza Supabase
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Inizializza Google Vision con credenziali
try:
    credentials = get_vision_credentials()
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
except ValueError as e:
    print(f"WARNING: Google Vision non configurato - OCR disabilitato: {e}")
    vision_client = None

# Helper function per conversione Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

app.json_encoder = DecimalEncoder

# ============= API CATEGORIE =============

@app.route('/api/categorie', methods=['GET'])
def get_categorie():
    try:
        response = supabase.table('categorie').select('*').eq('attiva', True).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categorie', methods=['POST'])
def create_categoria():
    try:
        data = request.json
        response = supabase.table('categorie').insert(data).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= API CLIENTI =============

@app.route('/api/clienti', methods=['GET'])
def get_clienti():
    try:
        response = supabase.table('clienti').select('*').eq('attivo', True).order('nome').execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clienti/<int:cliente_id>', methods=['GET'])
def get_cliente(cliente_id):
    try:
        response = supabase.table('clienti').select('*').eq('id', cliente_id).single().execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clienti', methods=['POST'])
def create_cliente():
    try:
        data = request.json
        response = supabase.table('clienti').insert(data).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clienti/<int:cliente_id>', methods=['PUT'])
def update_cliente(cliente_id):
    try:
        data = request.json
        response = supabase.table('clienti').update(data).eq('id', cliente_id).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clienti/<int:cliente_id>', methods=['DELETE'])
def delete_cliente(cliente_id):
    try:
        response = supabase.table('clienti').update({'attivo': False}).eq('id', cliente_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= API PROGETTI =============

@app.route('/api/progetti', methods=['GET'])
def get_progetti():
    try:
        cliente_id = request.args.get('cliente_id')
        query = supabase.table('progetti').select('*, clienti(nome)')
        
        if cliente_id:
            query = query.eq('cliente_id', cliente_id)
        
        response = query.order('created_at', desc=True).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progetti', methods=['POST'])
def create_progetto():
    try:
        data = request.json
        response = supabase.table('progetti').insert(data).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progetti/<int:progetto_id>', methods=['PUT'])
def update_progetto(progetto_id):
    try:
        data = request.json
        response = supabase.table('progetti').update(data).eq('id', progetto_id).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= API VEICOLI =============

@app.route('/api/veicoli', methods=['GET'])
def get_veicoli():
    try:
        response = supabase.table('veicoli').select('*').eq('attivo', True).order('targa').execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/veicoli', methods=['POST'])
def create_veicolo():
    try:
        data = request.json
        response = supabase.table('veicoli').insert(data).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/veicoli/<int:veicolo_id>', methods=['PUT'])
def update_veicolo(veicolo_id):
    try:
        data = request.json
        response = supabase.table('veicoli').update(data).eq('id', veicolo_id).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= API SPESE =============

@app.route('/api/spese', methods=['GET'])
def get_spese():
    try:
        # Filtri
        data_inizio = request.args.get('data_inizio')
        data_fine = request.args.get('data_fine')
        cliente_id = request.args.get('cliente_id')
        progetto_id = request.args.get('progetto_id')
        categoria_id = request.args.get('categoria_id')
        addebitabile = request.args.get('addebitabile')
        
        query = supabase.table('spese').select('''
            *,
            categorie(nome, colore),
            clienti(nome),
            progetti(nome, codice)
        ''')
        
        if data_inizio:
            query = query.gte('data_spesa', data_inizio)
        if data_fine:
            query = query.lte('data_spesa', data_fine)
        if cliente_id:
            query = query.eq('cliente_id', cliente_id)
        if progetto_id:
            query = query.eq('progetto_id', progetto_id)
        if categoria_id:
            query = query.eq('categoria_id', categoria_id)
        if addebitabile is not None:
            query = query.eq('addebitabile', addebitabile == 'true')
        
        response = query.order('data_spesa', desc=True).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/spese', methods=['POST'])
def create_spesa():
    try:
        data = request.json
        
        # Validazione
        if 'data_spesa' not in data or 'importo' not in data or 'descrizione' not in data:
            return jsonify({'success': False, 'error': 'Campi obbligatori mancanti'}), 400
        
        response = supabase.table('spese').insert(data).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/spese/<int:spesa_id>', methods=['PUT'])
def update_spesa(spesa_id):
    try:
        data = request.json
        response = supabase.table('spese').update(data).eq('id', spesa_id).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/spese/<int:spesa_id>', methods=['DELETE'])
def delete_spesa(spesa_id):
    try:
        response = supabase.table('spese').delete().eq('id', spesa_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= OCR E UPLOAD IMMAGINI =============

@app.route('/api/upload-ricevuta', methods=['POST'])
def upload_ricevuta():
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'Nessuna immagine fornita'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nome file vuoto'}), 400
        
        # Leggi l'immagine
        image_bytes = file.read()
        
        # Upload su Supabase Storage
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ricevute/{timestamp}_{file.filename}"
        
        storage_response = supabase.storage.from_('expenses').upload(
            filename,
            image_bytes,
            {'content-type': file.content_type}
        )
        
        # Ottieni URL pubblico
        image_url = supabase.storage.from_('expenses').get_public_url(filename)
        
        # Esegui OCR con Google Vision (se disponibile)
        ocr_data = {}
        if vision_client is not None:
            image = vision.Image(content=image_bytes)
            response = vision_client.text_detection(image=image)
            texts = response.text_annotations
            
            if texts:
                full_text = texts[0].description
                ocr_data['full_text'] = full_text
                
                # Estrazione intelligente dati
                ocr_data.update(extract_receipt_data(full_text))
        else:
            ocr_data['warning'] = 'OCR non disponibile - Google Vision non configurato'
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'ocr_data': ocr_data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def extract_receipt_data(text):
    """Estrae dati strutturati dal testo OCR"""
    import re
    
    data = {}
    
    # Cerca importo totale (pattern comuni)
    importo_patterns = [
        r'TOTALE[:\s]+€?\s*(\d+[,\.]\d{2})',
        r'TOTAL[E]?[:\s]+€?\s*(\d+[,\.]\d{2})',
        r'EUR[:\s]+(\d+[,\.]\d{2})',
        r'€\s*(\d+[,\.]\d{2})'
    ]
    
    for pattern in importo_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            importo_str = match.group(1).replace(',', '.')
            data['importo'] = float(importo_str)
            break
    
    # Cerca data
    date_patterns = [
        r'(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})',
        r'(\d{2}[/\-\.]\d{2}[/\-\.]\d{2})'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            data['data'] = match.group(1)
            break
    
    # Cerca P.IVA
    piva_match = re.search(r'P\.?\s*IVA[:\s]+(\d{11})', text, re.IGNORECASE)
    if piva_match:
        data['partita_iva'] = piva_match.group(1)
    
    return data

# ============= API CHILOMETRICHE =============

@app.route('/api/chilometriche', methods=['GET'])
def get_chilometriche():
    try:
        data_inizio = request.args.get('data_inizio')
        data_fine = request.args.get('data_fine')
        veicolo_id = request.args.get('veicolo_id')
        cliente_id = request.args.get('cliente_id')
        
        query = supabase.table('chilometriche').select('''
            *,
            veicoli(targa, marca, modello),
            clienti(nome),
            progetti(nome, codice)
        ''')
        
        if data_inizio:
            query = query.gte('data_viaggio', data_inizio)
        if data_fine:
            query = query.lte('data_viaggio', data_fine)
        if veicolo_id:
            query = query.eq('veicolo_id', veicolo_id)
        if cliente_id:
            query = query.eq('cliente_id', cliente_id)
        
        response = query.order('data_viaggio', desc=True).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chilometriche', methods=['POST'])
def create_chilometrica():
    try:
        data = request.json
        
        # Calcola rimborso se non fornito
        if 'rimborso_calcolato' not in data:
            km = float(data['km_percorsi'])
            tariffa = float(data['tariffa_applicata'])
            data['rimborso_calcolato'] = round(km * tariffa, 2)
        
        response = supabase.table('chilometriche').insert(data).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chilometriche/<int:chilo_id>', methods=['PUT'])
def update_chilometrica(chilo_id):
    try:
        data = request.json
        
        # Ricalcola rimborso se modificati km o tariffa
        if 'km_percorsi' in data or 'tariffa_applicata' in data:
            current = supabase.table('chilometriche').select('*').eq('id', chilo_id).single().execute()
            km = float(data.get('km_percorsi', current.data['km_percorsi']))
            tariffa = float(data.get('tariffa_applicata', current.data['tariffa_applicata']))
            data['rimborso_calcolato'] = round(km * tariffa, 2)
        
        response = supabase.table('chilometriche').update(data).eq('id', chilo_id).execute()
        return jsonify({'success': True, 'data': response.data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chilometriche/<int:chilo_id>', methods=['DELETE'])
def delete_chilometrica(chilo_id):
    try:
        response = supabase.table('chilometriche').delete().eq('id', chilo_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= REPORT E STATISTICHE =============

@app.route('/api/stats/dashboard', methods=['GET'])
def get_dashboard_stats():
    try:
        # Periodo corrente (mese corrente)
        oggi = datetime.now()
        inizio_mese = oggi.replace(day=1).strftime('%Y-%m-%d')
        fine_mese = (oggi.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        fine_mese = fine_mese.strftime('%Y-%m-%d')
        
        # Totale spese mese corrente
        spese_mese = supabase.table('spese')\
            .select('importo')\
            .gte('data_spesa', inizio_mese)\
            .lte('data_spesa', fine_mese)\
            .execute()
        
        totale_spese = sum(float(s['importo']) for s in spese_mese.data)
        
        # Spese addebitabili non ancora addebitate
        spese_addebitabili = supabase.table('spese')\
            .select('importo')\
            .eq('addebitabile', True)\
            .eq('addebitata', False)\
            .execute()
        
        totale_addebitabili = sum(float(s['importo']) for s in spese_addebitabili.data)
        
        # Km totali mese
        km_mese = supabase.table('chilometriche')\
            .select('km_percorsi, rimborso_calcolato')\
            .gte('data_viaggio', inizio_mese)\
            .lte('data_viaggio', fine_mese)\
            .execute()
        
        totale_km = sum(float(k['km_percorsi']) for k in km_mese.data)
        totale_rimborsi_km = sum(float(k['rimborso_calcolato']) for k in km_mese.data)
        
        # Spese per categoria (mese corrente)
        spese_categoria = supabase.table('spese')\
            .select('categoria_id, importo, categorie(nome, colore)')\
            .gte('data_spesa', inizio_mese)\
            .lte('data_spesa', fine_mese)\
            .execute()
        
        categorie_totali = {}
        for spesa in spese_categoria.data:
            cat_nome = spesa['categorie']['nome'] if spesa.get('categorie') else 'Non categorizzata'
            cat_colore = spesa['categorie']['colore'] if spesa.get('categorie') else '#6B7280'
            
            if cat_nome not in categorie_totali:
                categorie_totali[cat_nome] = {'totale': 0, 'colore': cat_colore}
            categorie_totali[cat_nome]['totale'] += float(spesa['importo'])
        
        return jsonify({
            'success': True,
            'data': {
                'totale_spese_mese': totale_spese,
                'totale_addebitabili': totale_addebitabili,
                'totale_km_mese': totale_km,
                'totale_rimborsi_km': totale_rimborsi_km,
                'num_spese_mese': len(spese_mese.data),
                'num_viaggi_mese': len(km_mese.data),
                'spese_per_categoria': categorie_totali
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats/mensili', methods=['GET'])
def get_stats_mensili():
    try:
        anno = request.args.get('anno', datetime.now().year)
        
        stats = []
        for mese in range(1, 13):
            inizio = f"{anno}-{mese:02d}-01"
            fine = (datetime(int(anno), mese, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            fine = fine.strftime('%Y-%m-%d')
            
            spese = supabase.table('spese')\
                .select('importo')\
                .gte('data_spesa', inizio)\
                .lte('data_spesa', fine)\
                .execute()
            
            km = supabase.table('chilometriche')\
                .select('km_percorsi, rimborso_calcolato')\
                .gte('data_viaggio', inizio)\
                .lte('data_viaggio', fine)\
                .execute()
            
            stats.append({
                'mese': mese,
                'totale_spese': sum(float(s['importo']) for s in spese.data),
                'totale_km': sum(float(k['km_percorsi']) for k in km.data),
                'totale_rimborsi': sum(float(k['rimborso_calcolato']) for k in km.data)
            })
        
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= EXPORT =============

@app.route('/api/export/excel', methods=['POST'])
def export_excel():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        
        data = request.json
        tipo = data.get('tipo', 'spese')  # spese o chilometriche
        filtri = data.get('filtri', {})
        
        wb = Workbook()
        ws = wb.active
        
        if tipo == 'spese':
            ws.title = "Spese"
            
            # Header
            headers = ['Data', 'Categoria', 'Cliente', 'Progetto', 'Descrizione', 
                      'Fornitore', 'Importo €', 'Addebitabile', 'Note']
            ws.append(headers)
            
            # Stile header
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            # Dati
            spese_response = supabase.table('spese').select('''
                *,
                categorie(nome),
                clienti(nome),
                progetti(nome)
            ''').execute()
            
            for spesa in spese_response.data:
                ws.append([
                    spesa['data_spesa'],
                    spesa['categorie']['nome'] if spesa.get('categorie') else '',
                    spesa['clienti']['nome'] if spesa.get('clienti') else '',
                    spesa['progetti']['nome'] if spesa.get('progetti') else '',
                    spesa['descrizione'],
                    spesa.get('fornitore', ''),
                    float(spesa['importo']),
                    'Sì' if spesa['addebitabile'] else 'No',
                    spesa.get('note', '')
                ])
        
        else:  # chilometriche
            ws.title = "Chilometriche"
            
            headers = ['Data', 'Veicolo', 'Cliente', 'Progetto', 'Partenza', 
                      'Arrivo', 'Km', 'Tariffa €/km', 'Rimborso €', 'Addebitabile']
            ws.append(headers)
            
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")
            
            km_response = supabase.table('chilometriche').select('''
                *,
                veicoli(targa),
                clienti(nome),
                progetti(nome)
            ''').execute()
            
            for km in km_response.data:
                ws.append([
                    km['data_viaggio'],
                    km['veicoli']['targa'] if km.get('veicoli') else '',
                    km['clienti']['nome'] if km.get('clienti') else '',
                    km['progetti']['nome'] if km.get('progetti') else '',
                    km['partenza'],
                    km['arrivo'],
                    float(km['km_percorsi']),
                    float(km['tariffa_applicata']),
                    float(km['rimborso_calcolato']),
                    'Sì' if km['addebitabile'] else 'No'
                ])
        
        # Salva in memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= HEALTH CHECK =============

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
