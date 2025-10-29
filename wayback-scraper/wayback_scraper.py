#!/usr/bin/env python3
"""
Scraper per recuperare contenuti da siti archiviati su Wayback Machine
Estrae testi, immagini e date da pagine WordPress archiviate
"""

import os
import re
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote
from datetime import datetime
from pathlib import Path
import time


class WaybackScraper:
    def __init__(self, base_url, output_dir="scraped_content"):
        """
        Inizializza lo scraper

        Args:
            base_url: URL della Wayback Machine (es. https://web.archive.org/web/20201229235150/https://biblioteca.archimedica.eu/old)
            output_dir: Directory dove salvare i contenuti
        """
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

        # Estrai timestamp e URL originale dalla URL Wayback
        match = re.search(r'web\.archive\.org/web/(\d+)/(.*)', base_url)
        if match:
            self.timestamp = match.group(1)
            self.original_url = match.group(2)
        else:
            self.timestamp = None
            self.original_url = base_url

        # Crea directory di output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "pages").mkdir(exist_ok=True)

        self.scraped_urls = set()
        self.articles = []

    def get_wayback_url(self, url):
        """Converte un URL normale in URL Wayback Machine"""
        if 'web.archive.org' in url:
            return url
        if self.timestamp:
            return f"https://web.archive.org/web/{self.timestamp}/{url}"
        return url

    def clean_wayback_url(self, url):
        """Rimuove il prefisso Wayback Machine per ottenere URL originale"""
        match = re.search(r'web\.archive\.org/web/\d+/(.*)', url)
        if match:
            return match.group(1)
        return url

    def fetch_page(self, url):
        """Scarica una pagina e ritorna BeautifulSoup object"""
        try:
            print(f"Scarico: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Errore nel scaricare {url}: {e}")
            return None

    def download_image(self, img_url, filename):
        """Scarica un'immagine"""
        try:
            # Converti in URL Wayback se necessario
            if 'web.archive.org' not in img_url:
                img_url = self.get_wayback_url(img_url)

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

    def extract_article_data(self, soup, url):
        """Estrae dati da un articolo WordPress"""
        article_data = {
            'url': self.clean_wayback_url(url),
            'title': '',
            'date': '',
            'content': '',
            'images': [],
            'scraped_at': datetime.now().isoformat()
        }

        # Estrai titolo
        title_tag = soup.find('h1') or soup.find('h2', class_=re.compile('title|entry-title'))
        if title_tag:
            article_data['title'] = title_tag.get_text(strip=True)

        # Estrai data (WordPress usa vari formati)
        date_selectors = [
            {'class': re.compile('date|time|published')},
            {'itemprop': 'datePublished'},
            {'class': 'entry-date'},
        ]

        for selector in date_selectors:
            date_tag = soup.find(['time', 'span', 'div'], selector)
            if date_tag:
                article_data['date'] = date_tag.get_text(strip=True)
                # Prova a estrarre datetime se presente
                if date_tag.get('datetime'):
                    article_data['date'] = date_tag['datetime']
                break

        # Estrai contenuto principale
        content_selectors = [
            {'class': re.compile('entry-content|post-content|article-content|content')},
            {'itemprop': 'articleBody'},
            {'id': re.compile('content|post-')},
        ]

        content_div = None
        for selector in content_selectors:
            content_div = soup.find(['div', 'article'], selector)
            if content_div:
                break

        if content_div:
            # Estrai testo pulito
            article_data['content'] = content_div.get_text(separator='\n', strip=True)

            # Estrai immagini
            for img in content_div.find_all('img'):
                img_src = img.get('src') or img.get('data-src')
                if img_src:
                    # Gestisci URL relativi
                    if not img_src.startswith('http'):
                        img_src = urljoin(self.original_url, img_src)

                    # Genera filename univoco
                    img_filename = os.path.basename(urlparse(img_src).path)
                    if not img_filename:
                        img_filename = f"image_{len(article_data['images'])}.jpg"

                    # Scarica immagine
                    img_path = self.download_image(img_src, img_filename)
                    if img_path:
                        article_data['images'].append({
                            'original_url': img_src,
                            'local_path': img_path,
                            'alt': img.get('alt', '')
                        })

        return article_data

    def find_article_links(self, soup):
        """Trova link ad articoli nella pagina"""
        links = []

        # Cerca link che potrebbero essere articoli
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Pulisci URL Wayback
            clean_href = self.clean_wayback_url(href)

            # Filtra link che sembrano articoli (non categorie, tag, etc)
            if any(x in clean_href for x in ['/20', '/articol', '/post', '/blog']):
                full_url = urljoin(self.base_url, href)
                if full_url not in self.scraped_urls:
                    links.append(full_url)

        return links

    def scrape_page(self, url):
        """Scrape una singola pagina"""
        if url in self.scraped_urls:
            return

        self.scraped_urls.add(url)
        soup = self.fetch_page(url)

        if not soup:
            return

        # Estrai dati articolo
        article_data = self.extract_article_data(soup, url)

        if article_data['title'] or article_data['content']:
            self.articles.append(article_data)

            # Salva anche come file individuale
            filename = re.sub(r'[^\w\-]', '_', article_data['title'][:50] or 'untitled')
            page_path = self.output_dir / "pages" / f"{filename}.json"

            with open(page_path, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)

            print(f"✓ Salvato: {article_data['title']}")

        # Trova altri articoli
        article_links = self.find_article_links(soup)
        print(f"Trovati {len(article_links)} nuovi link")

        return article_links

    def scrape_recursive(self, start_url, max_pages=100):
        """Scrape ricorsivo del sito"""
        to_scrape = [start_url]
        scraped_count = 0

        while to_scrape and scraped_count < max_pages:
            url = to_scrape.pop(0)

            new_links = self.scrape_page(url)
            if new_links:
                to_scrape.extend([l for l in new_links if l not in self.scraped_urls])

            scraped_count += 1
            time.sleep(1)  # Pausa per non sovraccaricare il server

        print(f"\nScraping completato: {scraped_count} pagine, {len(self.articles)} articoli")

    def save_summary(self):
        """Salva un riepilogo di tutti gli articoli"""
        summary = {
            'scraping_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'original_url': self.original_url,
            'total_articles': len(self.articles),
            'articles': self.articles
        }

        summary_path = self.output_dir / "summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Riepilogo salvato in: {summary_path}")

        # Crea anche un file markdown leggibile
        md_path = self.output_dir / "summary.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Contenuti recuperati da {self.original_url}\n\n")
            f.write(f"Scraping effettuato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Totale articoli: {len(self.articles)}\n\n")
            f.write("---\n\n")

            for i, article in enumerate(self.articles, 1):
                f.write(f"## {i}. {article['title']}\n\n")
                if article['date']:
                    f.write(f"**Data**: {article['date']}\n\n")
                f.write(f"**URL**: {article['url']}\n\n")
                if article['images']:
                    f.write(f"**Immagini**: {len(article['images'])}\n\n")
                f.write(f"{article['content'][:300]}...\n\n")
                f.write("---\n\n")

        print(f"✓ Riepilogo markdown salvato in: {md_path}")


def main():
    """Funzione principale"""
    # URL del sito su Wayback Machine (usando snapshot del 2019 che è più completo)
    wayback_url = "https://web.archive.org/web/20190428235901/http://biblioteca.archimedica.eu/old/"

    print("=" * 70)
    print("WAYBACK MACHINE SCRAPER")
    print("=" * 70)
    print(f"\nURL: {wayback_url}")
    print(f"Output directory: biblioteca/")
    print("\nAvvio scraping...\n")

    scraper = WaybackScraper(wayback_url, output_dir="biblioteca")

    # Scrape il sito
    scraper.scrape_recursive(wayback_url, max_pages=50)

    # Salva riepilogo
    scraper.save_summary()

    print("\n" + "=" * 70)
    print("COMPLETATO!")
    print("=" * 70)
    print(f"\nContenuti salvati in: {scraper.output_dir.absolute()}")
    print(f"- Pagine: {scraper.output_dir / 'pages'}")
    print(f"- Immagini: {scraper.output_dir / 'images'}")
    print(f"- Riepilogo: {scraper.output_dir / 'summary.json'}")
    print(f"- Riepilogo MD: {scraper.output_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
