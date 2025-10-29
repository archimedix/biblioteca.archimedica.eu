#!/usr/bin/env python3
"""
Scraper per estrarre contenuti da feed RSS archiviati su Wayback Machine
Specifico per la Biblioteca Archimedica
"""

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import html


class RSSFeedScraper:
    def __init__(self, feed_url, output_dir="biblioteca"):
        self.feed_url = feed_url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        # Crea directory di output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "articles").mkdir(exist_ok=True)

        self.articles = []

    def fetch_feed(self):
        """Scarica il feed RSS"""
        try:
            print(f"Scarico feed: {self.feed_url}")
            response = self.session.get(self.feed_url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'xml')
        except Exception as e:
            print(f"Errore nel scaricare il feed: {e}")
            return None

    def download_image(self, img_url, filename):
        """Scarica un'immagine"""
        try:
            print(f"  Scarico immagine: {filename}")
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()

            img_path = self.output_dir / "images" / filename
            with open(img_path, 'wb') as f:
                f.write(response.content)

            return str(img_path)
        except Exception as e:
            print(f"  Errore nel scaricare immagine {img_url}: {e}")
            return None

    def extract_and_download_images(self, content_html):
        """Estrae e scarica immagini dal contenuto HTML"""
        images = []
        soup = BeautifulSoup(content_html, 'html.parser')

        for img in soup.find_all('img'):
            img_src = img.get('src')
            if img_src:
                # Pulisce URL Wayback Machine se presente
                img_src = re.sub(r'https?://web\.archive\.org/web/\d+/', '', img_src)

                # Genera filename univoco
                parsed_url = urlparse(img_src)
                img_filename = os.path.basename(parsed_url.path)

                if not img_filename or img_filename == '':
                    img_filename = f"image_{len(images)}.jpg"

                # Scarica immagine
                img_path = self.download_image(img_src, img_filename)
                if img_path:
                    images.append({
                        'original_url': img_src,
                        'local_path': img_path,
                        'alt': img.get('alt', '')
                    })
                    # Aggiorna il src nell'HTML per puntare al file locale
                    img['src'] = img_path

        return images, str(soup)

    def clean_html(self, html_content):
        """Pulisce l'HTML da elementi indesiderati"""
        if not html_content:
            return ""

        # Decodifica entità HTML
        html_content = html.unescape(html_content)

        # Rimuove prefissi Wayback Machine
        html_content = re.sub(r'https?://web\.archive\.org/web/\d+/', '', html_content)

        return html_content

    def parse_article(self, item):
        """Parse un singolo articolo dal feed"""
        article = {
            'title': '',
            'url': '',
            'date': '',
            'author': '',
            'categories': [],
            'content_html': '',
            'content_text': '',
            'images': [],
            'scraped_at': datetime.now().isoformat()
        }

        # Titolo
        title_tag = item.find('title')
        if title_tag:
            article['title'] = title_tag.get_text(strip=True)

        # URL
        link_tag = item.find('link')
        if link_tag:
            article['url'] = link_tag.get_text(strip=True)

        # Data
        pubdate_tag = item.find('pubDate')
        if pubdate_tag:
            article['date'] = pubdate_tag.get_text(strip=True)

        # Autore
        creator_tag = item.find('dc:creator')
        if creator_tag:
            article['author'] = creator_tag.get_text(strip=True)

        # Categorie
        for cat_tag in item.find_all('category'):
            article['categories'].append(cat_tag.get_text(strip=True))

        # Contenuto
        content_tag = item.find('content:encoded')
        if content_tag:
            raw_html = content_tag.get_text()
            article['content_html'] = self.clean_html(raw_html)

            # Estrai e scarica immagini
            article['images'], article['content_html'] = self.extract_and_download_images(article['content_html'])

            # Estrai testo pulito
            soup = BeautifulSoup(article['content_html'], 'html.parser')
            article['content_text'] = soup.get_text(separator='\n', strip=True)

        return article

    def parse_feed(self, soup):
        """Parse tutti gli articoli dal feed"""
        items = soup.find_all('item')
        print(f"\nTrovati {len(items)} articoli nel feed\n")

        for i, item in enumerate(items, 1):
            print(f"[{i}/{len(items)}] Processo articolo...")
            article = self.parse_article(item)

            if article['title']:
                self.articles.append(article)

                # Salva articolo individuale
                filename = re.sub(r'[^\w\-]', '_', article['title'][:50])
                article_path = self.output_dir / "articles" / f"{filename}.json"

                with open(article_path, 'w', encoding='utf-8') as f:
                    json.dump(article, f, ensure_ascii=False, indent=2)

                # Salva anche versione HTML
                html_path = self.output_dir / "articles" / f"{filename}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(f"<h1>{article['title']}</h1>\n")
                    f.write(f"<p><strong>Data:</strong> {article['date']}</p>\n")
                    f.write(f"<p><strong>Autore:</strong> {article['author']}</p>\n")
                    f.write(f"<hr>\n{article['content_html']}")

                print(f"✓ Salvato: {article['title']}")

        return self.articles

    def save_summary(self):
        """Salva riepilogo completo"""
        summary = {
            'scraping_date': datetime.now().isoformat(),
            'feed_url': self.feed_url,
            'total_articles': len(self.articles),
            'articles': self.articles
        }

        # JSON
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Riepilogo JSON salvato in: {summary_path}")

        # Markdown
        md_path = self.output_dir / "summary.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("# Biblioteca Archimedica - Contenuti Recuperati\n\n")
            f.write(f"Scraping effettuato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Totale articoli: {len(self.articles)}\n\n")
            f.write("---\n\n")

            for i, article in enumerate(self.articles, 1):
                f.write(f"## {i}. {article['title']}\n\n")
                f.write(f"**Data**: {article['date']}\n\n")
                f.write(f"**Autore**: {article['author']}\n\n")
                f.write(f"**URL**: {article['url']}\n\n")

                if article['categories']:
                    f.write(f"**Categorie**: {', '.join(article['categories'])}\n\n")

                if article['images']:
                    f.write(f"**Immagini**: {len(article['images'])}\n\n")

                # Anteprima contenuto
                preview = article['content_text'][:500]
                f.write(f"{preview}...\n\n")
                f.write("---\n\n")

        print(f"✓ Riepilogo Markdown salvato in: {md_path}")

        # HTML completo
        html_path = self.output_dir / "index.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write("<!DOCTYPE html>\n<html lang='it'>\n<head>\n")
            f.write("<meta charset='UTF-8'>\n")
            f.write("<title>Biblioteca Archimedica - Archivio</title>\n")
            f.write("<style>\n")
            f.write("body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }\n")
            f.write("article { margin-bottom: 40px; padding-bottom: 20px; border-bottom: 1px solid #ccc; }\n")
            f.write("img { max-width: 100%; height: auto; }\n")
            f.write("</style>\n")
            f.write("</head>\n<body>\n")
            f.write("<h1>Biblioteca Archimedica - Archivio Completo</h1>\n")
            f.write(f"<p>Recuperato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>\n")
            f.write(f"<p><strong>Totale articoli: {len(self.articles)}</strong></p>\n")
            f.write("<hr>\n")

            for article in self.articles:
                f.write("<article>\n")
                f.write(f"<h2>{article['title']}</h2>\n")
                f.write(f"<p><strong>Data:</strong> {article['date']} | <strong>Autore:</strong> {article['author']}</p>\n")
                f.write(f"{article['content_html']}\n")
                f.write("</article>\n")

            f.write("</body>\n</html>\n")

        print(f"✓ Archivio HTML completo salvato in: {html_path}")


def main():
    # URL del feed RSS archiviato
    feed_url = "https://web.archive.org/web/20190221002126/http://biblioteca.archimedica.eu/old/feed/"

    print("=" * 70)
    print("RSS FEED SCRAPER - BIBLIOTECA ARCHIMEDICA")
    print("=" * 70)
    print(f"\nFeed URL: {feed_url}")
    print(f"Output directory: biblioteca/\n")

    scraper = RSSFeedScraper(feed_url, output_dir="biblioteca")

    # Scarica e parse feed
    soup = scraper.fetch_feed()
    if soup:
        scraper.parse_feed(soup)
        scraper.save_summary()

    print("\n" + "=" * 70)
    print("COMPLETATO!")
    print("=" * 70)
    print(f"\nContenuti salvati in: {scraper.output_dir.absolute()}")
    print(f"- Articoli JSON: {scraper.output_dir / 'articles'}")
    print(f"- Articoli HTML: {scraper.output_dir / 'articles'}")
    print(f"- Immagini: {scraper.output_dir / 'images'}")
    print(f"- Riepilogo: {scraper.output_dir / 'summary.json'}")
    print(f"- Archivio completo: {scraper.output_dir / 'index.html'}")


if __name__ == "__main__":
    main()
