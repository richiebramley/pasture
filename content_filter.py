import re
from typing import List, Dict, Tuple
from collections import Counter
import config

class ContentFilter:
    def __init__(self):
        self.keywords = config.KEYWORDS
        self.min_relevance_score = config.MIN_RELEVANCE_SCORE
    
    def calculate_relevance_score(self, title: str, description: str, content: str = "") -> Tuple[float, List[str]]:
        """
        Calculate relevance score based on keyword matches
        Returns: (score, matched_keywords)
        """
        text = f"{title} {description} {content}".lower()
        matched_keywords = []
        total_score = 0.0
        
        # Weight different keyword categories
        category_weights = {
            'virtual_fencing': 1.5,  # Higher weight for virtual fencing
            'herd_control': 1.3,     # High weight for herd control
            'pasture_management': 1.3, # High weight for pasture management
            'agritech': 1.0,         # Standard weight for general agritech
            'general_farming': 0.8    # Lower weight but still relevant
        }
        
        for category, keywords in self.keywords.items():
            category_score = 0.0
            category_matches = []
            
            for keyword in keywords:
                # Count keyword occurrences
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, text))
                
                if matches > 0:
                    category_matches.append(keyword)
                    # Weight by frequency and position (title gets higher weight)
                    title_matches = len(re.findall(pattern, title.lower()))
                    desc_matches = len(re.findall(pattern, description.lower()))
                    
                    # Title matches are worth more
                    category_score += (title_matches * 3 + desc_matches * 2 + matches) * 0.1
            
            if category_score > 0:
                # Apply category weight
                weighted_score = category_score * category_weights.get(category, 1.0)
                total_score += weighted_score
                matched_keywords.extend(category_matches)
        
        # Normalize score to 0-1 range
        normalized_score = min(total_score, 1.0)
        
        return normalized_score, matched_keywords
    
    def is_relevant(self, title: str, description: str, content: str = "") -> bool:
        """Check if content is relevant based on minimum score threshold"""
        score, _ = self.calculate_relevance_score(title, description, content)
        return score >= self.min_relevance_score
    
    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles based on relevance"""
        filtered_articles = []
        
        for article in articles:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            if self.is_relevant(title, description, content):
                score, matched_keywords = self.calculate_relevance_score(title, description, content)
                article['relevance_score'] = score
                article['keywords_matched'] = matched_keywords
                filtered_articles.append(article)
        
        # Sort by relevance score (highest first)
        filtered_articles.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return filtered_articles
    
    def get_keyword_summary(self, articles: List[Dict]) -> Dict:
        """Generate a summary of keyword matches across articles"""
        keyword_counts = Counter()
        category_counts = Counter()
        
        for article in articles:
            keywords = article.get('keywords_matched', [])
            for keyword in keywords:
                keyword_counts[keyword] += 1
            
            # Count by category
            for category, category_keywords in self.keywords.items():
                if any(kw in keywords for kw in category_keywords):
                    category_counts[category] += 1
        
        return {
            'top_keywords': dict(keyword_counts.most_common(10)),
            'category_distribution': dict(category_counts),
            'total_articles': len(articles)
        }
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract potential company names, product names, and technologies"""
        # Simple entity extraction - can be enhanced with NER
        entities = []
        
        # Look for capitalized phrases (potential company/product names)
        capitalized_pattern = r'\b[A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Technologies|Systems|Solutions)\b'
        entities.extend(re.findall(capitalized_pattern, text))
        
        # Look for technology terms
        tech_terms = [
            'GPS', 'IoT', 'AI', 'ML', 'sensor', 'drone', 'satellite',
            'blockchain', 'automation', 'robotics', 'precision'
        ]
        
        for term in tech_terms:
            if term.lower() in text.lower():
                entities.append(term)
        
        return list(set(entities))
    
    def categorize_article(self, title: str, description: str) -> str:
        """Categorize article based on content"""
        text = f"{title} {description}".lower()
        
        # Define category patterns
        categories = {
            'virtual_fencing': ['virtual fence', 'electronic fence', 'gps fence', 'geofencing'],
            'herd_control': ['herd management', 'cattle tracking', 'livestock monitoring'],
            'pasture_management': ['pasture', 'grazing', 'forage', 'grass management'],
            'dairy': ['dairy', 'milk', 'cow', 'milking'],
            'beef': ['beef', 'cattle', 'ranching'],
            'equipment': ['tractor', 'equipment', 'machinery', 'implement'],
            'technology': ['technology', 'digital', 'smart', 'automation'],
            'general': ['farming', 'agriculture', 'farm']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general' 