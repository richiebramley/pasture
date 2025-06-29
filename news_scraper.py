import feedparser
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime, timezone
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import newspaper
from newspaper import Article
import config
from content_filter import ContentFilter

class NewsScraper:
    def __init__(self):
        self.sources = config.NEWS_SOURCES
        self.content_filter = ContentFilter()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_rss_feed(self, source: Dict) -> List[Dict]:
        """Fetch articles from an RSS feed"""
        articles = []
        
        try:
            print(f"Fetching RSS feed: {source['name']} - {source['url']}")
            
            # Parse RSS feed
            feed = feedparser.parse(source['url'])
            
            if feed.bozo:
                print(f"Warning: RSS feed parsing issues for {source['name']}")
            
            for entry in feed.entries:
                try:
                    # Extract article data
                    published_date = self._parse_date(entry.get('published', ''))
                    article = {
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'source': source['name'],
                        'category': source['category'],
                        'published_date': published_date,
                        'content': '',
                        'image_url': ''
                    }
                    
                    # Skip if no title or URL
                    if not article['title'] or not article['url']:
                        continue
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"Error processing RSS entry from {source['name']}: {e}")
                    continue
            
            print(f"Found {len(articles)} articles from {source['name']}")
            
        except Exception as e:
            print(f"Error fetching RSS feed {source['name']}: {e}")
        
        return articles
    
    def fetch_web_content(self, article: Dict) -> Dict:
        """Fetch full content from article URL and extract top image"""
        try:
            if not article.get('url'):
                return article
            
            # Use newspaper3k to extract content
            news_article = Article(article['url'])
            news_article.download()
            news_article.parse()
            
            # Update article with extracted content
            article['content'] = news_article.text[:2000]  # Limit content length
            
            # Extract additional metadata
            if news_article.meta_description:
                article['description'] = news_article.meta_description
            # Only set published_date from web scrape if RSS did not provide it
            if (not article.get('published_date')) or (not article['published_date'].strip()):
                if news_article.publish_date:
                    article['published_date'] = news_article.publish_date.isoformat()
            if news_article.top_image:
                article['image_url'] = news_article.top_image
            else:
                article['image_url'] = ''
            
            # Add delay to be respectful to servers
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching content from {article.get('url', 'unknown')}: {e}")
        
        return article
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all configured news sources"""
        all_articles = []
        
        for source in self.sources:
            try:
                # Fetch RSS feed
                articles = self.fetch_rss_feed(source)
                
                # Fetch full content for relevant articles
                relevant_articles = []
                for article in articles:
                    # Quick relevance check before fetching full content
                    if self.content_filter.is_relevant(article['title'], article['description']):
                        # Fetch full content
                        full_article = self.fetch_web_content(article)
                        relevant_articles.append(full_article)
                
                all_articles.extend(relevant_articles)
                
                # Add delay between sources
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing source {source['name']}: {e}")
                continue
        
        return all_articles
    
    def _parse_date(self, date_string: str) -> str:
        """Parse various date formats"""
        if not date_string:
            return datetime.now().isoformat()
        
        try:
            # Try to parse with feedparser
            parsed = feedparser._parse_date(date_string)
            if parsed:
                return datetime(*parsed[:6]).isoformat()
        except:
            pass
        
        # Fallback to current time
        return datetime.now().isoformat()
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible"""
        try:
            response = self.session.head(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def get_source_status(self) -> Dict:
        """Check status of all news sources"""
        status = {}
        
        for source in self.sources:
            try:
                is_valid = self.validate_url(source['url'])
                status[source['name']] = {
                    'url': source['url'],
                    'category': source['category'],
                    'status': 'active' if is_valid else 'inactive',
                    'last_check': datetime.now().isoformat()
                }
            except Exception as e:
                status[source['name']] = {
                    'url': source['url'],
                    'category': source['category'],
                    'status': 'error',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        return status

class AlternativeScraper:
    """Alternative scraper for sources that don't have RSS feeds"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_agfunder(self) -> List[Dict]:
        """Scrape AgFunder News website"""
        articles = []
        
        try:
            url = "https://agfundernews.com/category/agtech"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links
            article_links = soup.find_all('a', href=True)
            
            for link in article_links[:20]:  # Limit to first 20 articles
                href = link.get('href')
                if href and '/20' in href and 'agfundernews.com' in href:
                    try:
                        # Fetch individual article
                        article_response = self.session.get(href, timeout=10)
                        article_soup = BeautifulSoup(article_response.content, 'html.parser')
                        
                        title_elem = article_soup.find('h1')
                        title = title_elem.get_text().strip() if title_elem else ''
                        
                        content_elem = article_soup.find('div', class_='entry-content')
                        content = content_elem.get_text().strip() if content_elem else ''
                        
                        # Try to extract publish date from meta tag or leave blank
                        pub_date = ''
                        meta_date = article_soup.find('meta', {'property': 'article:published_time'})
                        if meta_date and isinstance(meta_date, Tag) and meta_date.get('content'):
                            pub_date = meta_date.get('content')
                        
                        if title and content:
                            articles.append({
                                'title': title,
                                'description': content[:200] + '...',
                                'content': content,
                                'url': href,
                                'source': 'AgFunder News',
                                'category': 'agritech',
                                'published_date': pub_date,
                                'image_url': ''
                            })
                        
                        time.sleep(1)  # Be respectful
                        
                    except Exception as e:
                        print(f"Error scraping article {href}: {e}")
                        continue
            
        except Exception as e:
            print(f"Error scraping AgFunder: {e}")
        
        return articles 