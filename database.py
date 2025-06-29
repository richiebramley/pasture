import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config

class NewsDatabase:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    content TEXT,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT,
                    published_date TEXT,
                    relevance_score REAL DEFAULT 0.0,
                    keywords_matched TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create sources table to track RSS sources
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    category TEXT,
                    last_fetch TIMESTAMP,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Create fetch_log table to track update history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fetch_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    articles_found INTEGER,
                    articles_added INTEGER,
                    fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
            ''')
            
            conn.commit()
    
    def add_article(self, article_data: Dict) -> bool:
        """Add a new article to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR IGNORE INTO articles 
                    (title, description, content, url, source, category, 
                     published_date, relevance_score, keywords_matched)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_data.get('title', ''),
                    article_data.get('description', ''),
                    article_data.get('content', ''),
                    article_data.get('url', ''),
                    article_data.get('source', ''),
                    article_data.get('category', ''),
                    article_data.get('published_date', ''),
                    article_data.get('relevance_score', 0.0),
                    json.dumps(article_data.get('keywords_matched', []))
                ))
                
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error adding article: {e}")
            return False
    
    def get_articles_count(self, category: Optional[str] = None, days_back: int = 7) -> int:
        """Get total count of articles for pagination"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT COUNT(*) FROM articles 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days_back)
                
                params = []
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                
                cursor.execute(query, params)
                count = cursor.fetchone()[0]
                
                return count
        except Exception as e:
            print(f"Error getting articles count: {e}")
            return 0
    
    def get_articles(self, limit: int = 50, category: Optional[str] = None, 
                    days_back: int = 7, offset: int = 0, min_relevance: float = 0.0) -> List[Dict]:
        """Retrieve articles from the database with pagination support and sorting by published_date DESC"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM articles 
                    WHERE created_at >= datetime('now', '-{} days')
                '''.format(days_back)
                
                params = []
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                if min_relevance > 0.0:
                    query += ' AND relevance_score >= ?'
                    params.append(min_relevance)
                
                query += ' ORDER BY published_date DESC, relevance_score DESC, created_at DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                articles = []
                for row in rows:
                    article = dict(row)
                    # Parse keywords_matched from JSON
                    if article['keywords_matched']:
                        article['keywords_matched'] = json.loads(article['keywords_matched'])
                    else:
                        article['keywords_matched'] = []
                    articles.append(article)
                
                return articles
        except Exception as e:
            print(f"Error retrieving articles: {e}")
            return []
    
    def get_articles_by_keywords(self, keywords: List[str], limit: int = 50) -> List[Dict]:
        """Retrieve articles that match specific keywords"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Create a pattern for keyword matching
                keyword_pattern = '%' + '%'.join(keywords) + '%'
                
                cursor.execute('''
                    SELECT * FROM articles 
                    WHERE (title LIKE ? OR description LIKE ? OR content LIKE ?)
                    ORDER BY relevance_score DESC, created_at DESC 
                    LIMIT ?
                ''', (keyword_pattern, keyword_pattern, keyword_pattern, limit))
                
                rows = cursor.fetchall()
                
                articles = []
                for row in rows:
                    article = dict(row)
                    if article['keywords_matched']:
                        article['keywords_matched'] = json.loads(article['keywords_matched'])
                    else:
                        article['keywords_matched'] = []
                    articles.append(article)
                
                return articles
        except Exception as e:
            print(f"Error retrieving articles by keywords: {e}")
            return []
    
    def log_fetch(self, source_name: str, articles_found: int, 
                  articles_added: int, status: str = 'success'):
        """Log a fetch operation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO fetch_log 
                    (source_name, articles_found, articles_added, status)
                    VALUES (?, ?, ?, ?)
                ''', (source_name, articles_found, articles_added, status))
                
                conn.commit()
        except Exception as e:
            print(f"Error logging fetch: {e}")
    
    def cleanup_old_articles(self, days: int = config.DAYS_TO_KEEP_ARTICLES):
        """Remove articles older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM articles 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                print(f"Cleaned up {deleted_count} old articles")
                return deleted_count
        except Exception as e:
            print(f"Error cleaning up old articles: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total articles
                cursor.execute('SELECT COUNT(*) FROM articles')
                total_articles = cursor.fetchone()[0]
                
                # Articles by category
                cursor.execute('''
                    SELECT category, COUNT(*) as count 
                    FROM articles 
                    GROUP BY category
                ''')
                articles_by_category = dict(cursor.fetchall())
                
                # Recent articles (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM articles 
                    WHERE created_at >= datetime('now', '-1 day')
                ''')
                recent_articles = cursor.fetchone()[0]
                
                # Average relevance score
                cursor.execute('SELECT AVG(relevance_score) FROM articles')
                avg_relevance = cursor.fetchone()[0] or 0.0
                
                return {
                    'total_articles': total_articles,
                    'articles_by_category': articles_by_category,
                    'recent_articles': recent_articles,
                    'avg_relevance_score': round(avg_relevance, 2)
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {} 