# Biblioteca Archimedica - Nuovo Sito

Sito web moderno con design glassmorphism che presenta l'archivio storico della Biblioteca Archimedica di Second Life (2006-2008).

## Caratteristiche

- **Design Glassmorphism**: Effetti di vetro con colori rosa e viola energetico ispirati alla Biblioteca Archimedica originale
- **Responsive**: Ottimizzato per desktop, tablet e mobile
- **29 Articoli**: Tutti i contenuti recuperati dall'export WordPress
- **Tailwind CSS**: Styling moderno e performante
- **Animazioni Smooth**: Transizioni e effetti hover fluidi

## Struttura

```
newsite/
├── index.html              # Homepage con lista articoli
├── wordpress_posts.json    # Dati degli articoli
├── css/
│   └── style.css          # Stili glassmorphism personalizzati
├── js/
│   └── main.js            # Logica per caricare e visualizzare articoli
├── images/
│   ├── logo-biblioteca-archimedica.png
│   └── biblioteca-archimedica.jpg
└── articles/
    ├── 26.html
    ├── la-scoperta-del-metaverso-premiazione.html
    ├── economia-canaglia.html
    └── ... (29 articoli totali)
```

## Come Usare

### Sviluppo Locale

Apri semplicemente `index.html` in un browser moderno, oppure usa un server locale:

```bash
# Con Python 3
cd newsite
python3 -m http.server 8000

# Con Node.js (npx)
npx http-server newsite -p 8000
```

Poi apri http://localhost:8000 nel browser.

### Deploy

Il sito è completamente statico e può essere hostato su:
- GitHub Pages
- Netlify
- Vercel
- Qualsiasi hosting statico

## Design

### Colori

- **Rosa Archimedico**: `#e91e63`
- **Viola**: `#9c27b0`
- **Viola Profondo**: `#673ab7`
- **Viola Energetico**: `#7b2cbf`

### Effetti Glassmorphism

- Backdrop blur con saturazione
- Bordi semi-trasparenti
- Ombre colorate rosa/viola
- Transizioni smooth al hover

## Contenuti

I contenuti provengono dall'export WordPress originale (`bibliotecaarchimedica.wordpress.2016-03-26.xml`) e includono:

- 29 articoli pubblicati (2006-2008)
- Presentazioni di libri
- Eventi letterari
- Concorsi letterari
- Interviste
- Reportage dalla Biblioteca virtuale di Second Life

## Tecnologie

- HTML5
- CSS3 (Custom + Tailwind CSS via CDN)
- JavaScript vanilla (ES6+)
- Font system (sans-serif)

## Browser Supportati

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Opera (latest)

## Note

- Le immagini esterne negli articoli potrebbero non essere più disponibili (link originali)
- Alcuni caratteri speciali sono stati normalizzati da encoding UTF-8
- Il layout è ottimizzato per la leggibilità con effetti glassmorphism

## Crediti

**Biblioteca Archimedica** (2006-2008)
- Curator: Archimedix Bulan
- Piattaforma: Second Life
- Archivio preservato: 2025

## Licenza

Contenuti storici della Biblioteca Archimedica.
