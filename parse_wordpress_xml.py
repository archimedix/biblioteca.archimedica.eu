#!/usr/bin/env python3
"""
Parse WordPress XML export and generate JSON data for the new site
"""

import xml.etree.ElementTree as ET
import json
from datetime import datetime
import html
from fix_encoding import fix_encoding

# WordPress XML namespaces
namespaces = {
    'content': 'http://purl.org/rss/1.0/modules/content/',
    'wp': 'http://wordpress.org/export/1.2/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'excerpt': 'http://wordpress.org/export/1.2/excerpt/'
}

def parse_wordpress_xml(xml_file):
    """Parse WordPress XML export and extract posts"""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    posts = []

    # Find all items in the channel
    for item in root.findall('.//item'):
        # Get post type
        post_type = item.find('wp:post_type', namespaces)
        if post_type is None or post_type.text != 'post':
            continue

        # Get post status
        status = item.find('wp:status', namespaces)
        if status is None or status.text != 'publish':
            continue

        # Extract post data
        post = {}

        # Basic fields
        title_elem = item.find('title')
        title_raw = title_elem.text if title_elem is not None and title_elem.text else 'Untitled'
        post['title'] = fix_encoding(title_raw)

        link_elem = item.find('link')
        post['url'] = link_elem.text if link_elem is not None else ''

        pubdate_elem = item.find('pubDate')
        post['date'] = pubdate_elem.text if pubdate_elem is not None else ''

        creator_elem = item.find('dc:creator', namespaces)
        author_raw = creator_elem.text if creator_elem is not None else 'Unknown'
        post['author'] = fix_encoding(author_raw)

        # Content
        content_elem = item.find('content:encoded', namespaces)
        content_raw = content_elem.text if content_elem is not None and content_elem.text else ''
        post['content'] = fix_encoding(content_raw)

        # Excerpt
        excerpt_elem = item.find('excerpt:encoded', namespaces)
        excerpt_raw = excerpt_elem.text if excerpt_elem is not None and excerpt_elem.text else ''
        post['excerpt'] = fix_encoding(excerpt_raw)

        # Post name (slug)
        post_name = item.find('wp:post_name', namespaces)
        post['slug'] = post_name.text if post_name is not None and post_name.text else ''

        # Post ID
        post_id = item.find('wp:post_id', namespaces)
        post['id'] = post_id.text if post_id is not None else ''

        # Categories
        categories = []
        for category in item.findall('category[@domain="category"]'):
            if category.text:
                categories.append(fix_encoding(category.text))
        post['categories'] = categories

        # Tags
        tags = []
        for tag in item.findall('category[@domain="post_tag"]'):
            if tag.text:
                tags.append(fix_encoding(tag.text))
        post['tags'] = tags

        posts.append(post)

    # Sort by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)

    return posts

if __name__ == '__main__':
    xml_file = 'bibliotecaarchimedica.wordpress.2016-03-26.xml'
    posts = parse_wordpress_xml(xml_file)

    # Save to JSON
    with open('wordpress_posts.json', 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(posts)} published posts")
    print("\nPosts:")
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title']} ({post['date']})")
