"""
Script per generare icone PWA placeholder
Esegui: python generate_icons.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, text='€', bg_color='#4472C4', text_color='white'):
    """Crea un'icona con testo centrato"""
    
    # Converti colore hex a RGB
    bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Crea immagine
    img = Image.new('RGB', (size, size), bg_rgb)
    draw = ImageDraw.Draw(img)
    
    # Prova a usare un font di sistema
    try:
        font_size = int(size * 0.6)
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
    except:
        # Fallback a font default
        font = ImageFont.load_default()
    
    # Calcola posizione centrata
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    position = ((size - text_width) / 2, (size - text_height) / 2 - bbox[1])
    
    # Disegna testo
    draw.text(position, text, fill=text_color, font=font)
    
    return img

def main():
    """Genera icone 192x192 e 512x512"""
    
    output_dir = 'static'
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generazione icone PWA...")
    
    # Genera 192x192
    icon_192 = create_icon(192, '€')
    icon_192.save(f'{output_dir}/icon-192.png')
    print("✓ Creata icon-192.png")
    
    # Genera 512x512
    icon_512 = create_icon(512, '€')
    icon_512.save(f'{output_dir}/icon-512.png')
    print("✓ Creata icon-512.png")
    
    print("\nIcone generate con successo in /static/")
    print("Nota: Queste sono icone placeholder. Per produzione usa icone professionali.")

if __name__ == '__main__':
    main()
