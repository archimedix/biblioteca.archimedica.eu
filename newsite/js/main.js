// Load articles data
let articlesData = [];

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Truncate text
function truncateText(text, maxLength) {
    // Remove HTML tags
    const stripped = text.replace(/<[^>]+>/g, '');
    if (stripped.length <= maxLength) return stripped;
    return stripped.substr(0, maxLength) + '...';
}

// Create article card HTML
function createArticleCard(article, index) {
    const excerpt = truncateText(article.content, 200);

    return `
        <article class="glass-card-article rounded-2xl p-6 hover:cursor-pointer"
                 onclick="navigateToArticle('${article.slug}')">
            <div class="flex flex-col md:flex-row gap-6">
                <div class="flex-1">
                    <div class="flex flex-wrap items-center gap-2 mb-3">
                        <span class="badge badge-date text-white">${formatDate(article.date)}</span>
                    </div>
                    <h3 class="text-2xl font-bold text-white mb-3 hover:text-archi-pink transition">
                        ${article.title}
                    </h3>
                    <p class="text-white/80 mb-4 leading-relaxed">
                        ${excerpt}
                    </p>
                    <div class="flex items-center text-white/60 text-sm">
                        <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                        </svg>
                        ${article.author}
                    </div>
                </div>
                <div class="flex items-center">
                    <svg class="w-6 h-6 text-archi-pink" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                    </svg>
                </div>
            </div>
        </article>
    `;
}

// Navigate to article page
function navigateToArticle(slug) {
    window.location.href = `articles/${slug}.html`;
}

// Load and display articles
async function loadArticles() {
    try {
        const response = await fetch('../wordpress_posts.json');
        articlesData = await response.json();

        const articlesList = document.getElementById('articles-list');

        if (articlesData.length === 0) {
            articlesList.innerHTML = `
                <div class="text-center text-white/60 py-8">
                    <p>Nessun articolo trovato.</p>
                </div>
            `;
            return;
        }

        // Display all articles
        articlesList.innerHTML = articlesData
            .map((article, index) => createArticleCard(article, index))
            .join('');

    } catch (error) {
        console.error('Error loading articles:', error);
        document.getElementById('articles-list').innerHTML = `
            <div class="text-center text-white/80 py-8">
                <p>Errore nel caricamento degli articoli.</p>
            </div>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadArticles();
});

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
