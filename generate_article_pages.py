#!/usr/bin/env python3
"""
Generate individual HTML pages for each article
"""

import json
import os
from pathlib import Path
from datetime import datetime

def format_date(date_string):
    """Format date to Italian format"""
    try:
        date = datetime.strptime(date_string, '%a, %d %b %Y %H:%M:%S %z')
        return date.strftime('%d %B %Y')
    except:
        return date_string

def create_article_html(article):
    """Create HTML page for an article"""

    tags_html = ''
    if article['tags']:
        tags_html = '<div class="flex flex-wrap gap-2 mt-4">' + ' '.join([
            f'<span class="badge text-white">{tag}</span>'
            for tag in article['tags']
        ]) + '</div>'

    # Content is already cleaned by parse_wordpress_xml.py
    content = article['content']

    html = f'''<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - Biblioteca Archimedica</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="../css/style.css">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        'archi-pink': '#e91e63',
                        'archi-purple': '#9c27b0',
                        'archi-deep-purple': '#673ab7',
                        'archi-violet': '#7b2cbf',
                    }}
                }}
            }}
        }}
    </script>
</head>
<body class="min-h-screen bg-cover bg-center bg-fixed" style="background-image: url('../images/biblioteca-archimedica.jpg');">

    <!-- Overlay -->
    <div class="fixed inset-0 bg-gradient-to-br from-archi-purple/30 via-archi-deep-purple/20 to-archi-pink/30 backdrop-blur-sm"></div>

    <!-- Main Content -->
    <div class="relative z-10">

        <!-- Header -->
        <header class="container mx-auto px-4 py-8">
            <div class="glass-card rounded-3xl p-6">
                <nav class="flex items-center justify-between">
                    <a href="../index.html" class="flex items-center text-white hover:text-archi-pink transition">
                        <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
                        </svg>
                        Torna alla homepage
                    </a>
                    <img src="../images/logo-biblioteca-archimedica.png" alt="Logo" class="h-16">
                </nav>
            </div>
        </header>

        <!-- Article -->
        <article class="container mx-auto px-4 py-8">
            <div class="glass-card rounded-3xl p-8 md:p-12">

                <!-- Article Header -->
                <div class="mb-8">
                    <div class="flex flex-wrap items-center gap-2 mb-4">
                        <span class="badge badge-date text-white">{format_date(article['date'])}</span>
                    </div>

                    <h1 class="text-4xl md:text-5xl font-bold text-white mb-6">
                        {article['title']}
                    </h1>

                    <div class="flex items-center text-white/70">
                        <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                        </svg>
                        <span class="text-lg">di <strong>{article['author']}</strong></span>
                    </div>

                    {tags_html}
                </div>

                <!-- Article Content -->
                <div class="article-content text-white/90 prose prose-lg prose-invert max-w-none">
                    {content}
                </div>

                <!-- Article Footer -->
                <div class="mt-12 pt-8 border-t border-white/20">
                    <div class="flex flex-col md:flex-row justify-between items-center gap-4">
                        <div class="text-white/60 text-sm">
                            Pubblicato originariamente su <a href="{article['url']}" target="_blank" class="text-archi-pink hover:text-archi-purple">biblioteca.archimedix.net</a>
                        </div>
                        <a href="../index.html" class="glass-card-article px-6 py-3 rounded-xl text-white font-semibold hover:scale-105 transition">
                            ← Torna agli articoli
                        </a>
                    </div>
                </div>

            </div>
        </article>

        <!-- Footer -->
        <footer class="container mx-auto px-4 py-8">
            <div class="glass-card rounded-2xl p-6 text-center">
                <p class="text-white/80">
                    © 2006-2008 Biblioteca Archimedica - Second Life |
                    Curator: <span class="text-archi-pink">Archimedix Bulan</span>
                </p>
            </div>
        </footer>

    </div>

</body>
</html>
'''

    return html

def main():
    # Load articles
    with open('wordpress_posts.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)

    # Create articles directory
    articles_dir = Path('newsite/articles')
    articles_dir.mkdir(exist_ok=True)

    # Generate page for each article
    for article in articles:
        slug = article['slug'] if article['slug'] else article['id']
        filename = f"{slug}.html"
        filepath = articles_dir / filename

        html = create_article_html(article)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"Created: {filename}")

    print(f"\nGenerated {len(articles)} article pages in newsite/articles/")

if __name__ == '__main__':
    main()
