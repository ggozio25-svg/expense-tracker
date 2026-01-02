# Guida Generazione Icone PWA

## Icone Necessarie

L'applicazione richiede 2 icone per funzionare come PWA:

- `icon-192.png` (192x192 pixel)
- `icon-512.png` (512x512 pixel)

## Come Generarle

### Opzione 1: Tool Online (Consigliata)

1. Vai su https://realfavicongenerator.net/
2. Carica un'immagine (minimo 512x512)
3. Configura le opzioni
4. Scarica il pacchetto
5. Rinomina i file in `icon-192.png` e `icon-512.png`
6. Posiziona in `/static/`

### Opzione 2: Photoshop/GIMP

1. Crea un nuovo documento 512x512 pixel
2. Disegna il logo/icona (usa margini di sicurezza 10%)
3. Esporta come PNG: `icon-512.png`
4. Ridimensiona a 192x192
5. Esporta come PNG: `icon-192.png`
6. Posiziona in `/static/`

### Opzione 3: ImageMagick (CLI)

```bash
# Da un'immagine sorgente
convert logo.png -resize 512x512 static/icon-512.png
convert logo.png -resize 192x192 static/icon-192.png
```

### Opzione 4: Python (PIL)

```python
from PIL import Image

# Carica immagine originale
img = Image.open('logo.png')

# Crea 512x512
img_512 = img.resize((512, 512), Image.LANCZOS)
img_512.save('static/icon-512.png')

# Crea 192x192
img_192 = img.resize((192, 192), Image.LANCZOS)
img_192.save('static/icon-192.png')
```

## Specifiche Design

- **Formato**: PNG con trasparenza
- **Background**: Preferibilmente trasparente o colore solido
- **Safe Area**: 80% centrale per il contenuto principale
- **Stile**: Semplice, riconoscibile, professionale
- **Colori**: Allineati al tema app (#4472C4 blu principale)

## Suggerimenti Design

Per un'app di gestione spese, considera:

- Icona calcolatrice stilizzata
- Euro symbol (€) con decorazioni
- Portafoglio/wallet
- Grafico/chart minimale
- Scontrino stilizzato

### Emoji come Placeholder Temporaneo

Se vuoi partire subito puoi usare emoji come icone temporanee:

```python
from PIL import Image, ImageDraw, ImageFont

def create_emoji_icon(size, emoji, bg_color='#4472C4'):
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Font grande per emoji
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size // 2)
    
    # Centra emoji
    bbox = draw.textbbox((0, 0), emoji, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((size-w)/2, (size-h)/2), emoji, font=font, fill='white')
    
    return img

# Genera icone
icon_512 = create_emoji_icon(512, '💰')
icon_512.save('static/icon-512.png')

icon_192 = create_emoji_icon(192, '💰')
icon_192.save('static/icon-192.png')
```

## Verifica

Dopo aver generato le icone:

1. Controlla che siano nelle dimensioni corrette:
   ```bash
   file static/icon-*.png
   ```

2. Testa il manifest:
   - Apri DevTools > Application > Manifest
   - Verifica che le icone siano caricate correttamente

3. Testa installazione PWA su dispositivo mobile

## Note

- Le icone devono essere in `/static/` per essere servite
- Il manifest.json le referenzia con path relativi
- Android usa principalmente 192x192
- iOS/Desktop preferiscono 512x512
