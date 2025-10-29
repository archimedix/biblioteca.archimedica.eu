# Wayback Machine Scraper

Script Python per recuperare contenuti da siti archiviati su Wayback Machine.

## Caratteristiche

- Scarica testi, immagini e metadati da pagine archiviate
- Gestisce automaticamente gli URL della Wayback Machine
- Naviga ricorsivamente tra le pagine del sito
- Estrae date di pubblicazione quando disponibili
- Salva tutto in modo organizzato (JSON + Markdown)
- Scarica le immagini localmente

## Installazione

```bash
# Installa le dipendenze
pip3 install -r requirements.txt
```

## Utilizzo Base

```bash
# Esegui lo script (già configurato per il tuo sito)
python3 wayback_scraper.py
```

Lo script scaricherà i contenuti da:
```
https://web.archive.org/web/20201229235150/https://biblioteca.archimedica.eu/old
```

## Personalizzazione

Per scaricare da un altro URL della Wayback Machine, modifica la funzione `main()` in `wayback_scraper.py`:

```python
def main():
    wayback_url = "https://web.archive.org/web/TIMESTAMP/URL_ORIGINALE"
    scraper = WaybackScraper(wayback_url, output_dir="scraped_content")
    scraper.scrape_recursive(wayback_url, max_pages=50)  # Modifica max_pages se necessario
    scraper.save_summary()
```

### Parametri Configurabili

- `max_pages`: Numero massimo di pagine da scaricare (default: 50)
- `output_dir`: Directory dove salvare i contenuti (default: "scraped_content")
- `timeout`: Timeout per le richieste HTTP (default: 30 secondi)

## Output

Lo script crea la seguente struttura:

```
scraped_content/
├── images/              # Tutte le immagini scaricate
│   ├── image1.jpg
│   ├── image2.png
│   └── ...
├── pages/               # File JSON per ogni articolo
│   ├── articolo_1.json
│   ├── articolo_2.json
│   └── ...
├── summary.json         # Riepilogo completo in JSON
└── summary.md           # Riepilogo leggibile in Markdown
```

### Formato Dati

Ogni articolo viene salvato con:

```json
{
  "url": "URL originale dell'articolo",
  "title": "Titolo dell'articolo",
  "date": "Data di pubblicazione",
  "content": "Contenuto testuale completo",
  "images": [
    {
      "original_url": "URL originale immagine",
      "local_path": "percorso/locale/immagine.jpg",
      "alt": "Testo alternativo"
    }
  ],
  "scraped_at": "2025-10-29T..."
}
```

## Uso Programmatico

Puoi usare la classe `WaybackScraper` nel tuo codice:

```python
from wayback_scraper import WaybackScraper

scraper = WaybackScraper(
    base_url="https://web.archive.org/web/20201229235150/https://esempio.com",
    output_dir="mio_output"
)

# Scrape singola pagina
scraper.scrape_page("https://web.archive.org/web/.../pagina.html")

# Scrape ricorsivo
scraper.scrape_recursive(scraper.base_url, max_pages=100)

# Salva riepilogo
scraper.save_summary()

# Accedi ai dati
for article in scraper.articles:
    print(article['title'])
```

## Note

- Lo script fa una pausa di 1 secondo tra una richiesta e l'altra per non sovraccaricare i server
- Alcuni contenuti potrebbero non essere disponibili se non sono stati archiviati
- Il parsing è ottimizzato per WordPress ma funziona con la maggior parte dei CMS

## Troubleshooting

### Timeout Errors
Se ricevi errori di timeout, aumenta il valore in `wayback_scraper.py`:
```python
response = self.session.get(url, timeout=60)  # aumenta a 60 secondi
```

### Troppe Pagine
Se lo scraping è troppo lento, riduci `max_pages` o limita la ricorsione.
