import os
from datetime import datetime
import pytz

# News sources focused on agritech and farming
NEWS_SOURCES = [
    {
        'name': 'AgFunder News',
        'url': 'https://agfundernews.com/feed',
        'category': 'agritech'
    },
    {
        'name': 'Farm Journal',
        'url': 'https://www.farmjournal.com/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'Dairy Herd Management',
        'url': 'https://www.dairyherd.com/rss.xml',
        'category': 'dairy'
    },
    {
        'name': 'Beef Magazine',
        'url': 'https://www.beefmagazine.com/rss.xml',
        'category': 'beef'
    },
    {
        'name': 'Precision Ag',
        'url': 'https://www.precisionag.com/rss.xml',
        'category': 'precision_agriculture'
    },
    {
        'name': 'AgriTech Tomorrow',
        'url': 'https://www.agritechtomorrow.com/rss.xml',
        'category': 'agritech'
    },
    {
        'name': 'Farm Equipment',
        'url': 'https://www.farm-equipment.com/rss.xml',
        'category': 'equipment'
    },
    {
        'name': 'Successful Farming',
        'url': 'https://www.agriculture.com/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'Modern Farmer',
        'url': 'https://modernfarmer.com/feed/',
        'category': 'farming'
    },
    {
        'name': 'Farm Progress',
        'url': 'https://www.farmprogress.com/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'AgWeb',
        'url': 'https://www.agweb.com/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'Progressive Farmer',
        'url': 'https://www.dtnpf.com/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'NZ Farmer',
        'url': 'https://www.stuff.co.nz/business/farming/rss',
        'category': 'farming'
    },
    {
        'name': 'Farmers Weekly NZ',
        'url': 'https://www.farmersweekly.co.nz/feed/',
        'category': 'farming'
    },
    {
        'name': 'Rural News Group',
        'url': 'https://www.ruralnewsgroup.co.nz/rss',
        'category': 'farming'
    },
    {
        'name': 'Dairy News NZ',
        'url': 'https://www.dairynews.co.nz/rss',
        'category': 'dairy'
    },
    {
        'name': 'The Land (Australia)',
        'url': 'https://www.theland.com.au/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'ABC Rural (Australia)',
        'url': 'https://www.abc.net.au/news/rural/rss.xml',
        'category': 'farming'
    },
    {
        'name': 'Farmers Guardian (UK)',
        'url': 'https://www.fginsight.com/rss/news',
        'category': 'farming'
    },
    {
        'name': 'AgriLand (Ireland)',
        'url': 'https://www.agriland.ie/farming-news/feed/',
        'category': 'farming'
    }
]

# Keywords for content filtering
KEYWORDS = {
    'virtual_fencing': [
        'virtual fence', 'virtual fencing', 'electronic fence', 'smart fence',
        'GPS fence', 'digital fence', 'collision avoidance', 'geofencing',
        'boundary management', 'fence-free', 'wireless fence'
    ],
    'herd_control': [
        'herd management', 'cattle tracking', 'livestock monitoring',
        'animal tracking', 'herd behavior', 'cattle control', 'livestock control',
        'animal management', 'herd optimization', 'cattle monitoring'
    ],
    'pasture_management': [
        'pasture management', 'grazing management', 'forage management',
        'grass management', 'pasture optimization', 'rotational grazing',
        'intensive grazing', 'pasture rotation', 'grassland management',
        'forage optimization', 'pasture health', 'soil health'
    ],
    'agritech': [
        'agritech', 'agricultural technology', 'precision agriculture',
        'smart farming', 'digital agriculture', 'farm technology',
        'agricultural innovation', 'farming technology', 'agtech'
    ],
    'general_farming': [
        'farming', 'agriculture', 'farm', 'farmer', 'crop', 'livestock',
        'dairy', 'beef', 'cattle', 'sheep', 'poultry', 'swine', 'pig',
        'tractor', 'equipment', 'harvest', 'planting', 'irrigation',
        'fertilizer', 'pesticide', 'organic', 'sustainable', 'regenerative'
    ]
}

# Database configuration
DATABASE_PATH = 'newsfeed.db'

# Scheduler configuration
SCHEDULE_TIME = '07:00'  # 7am CET
TIMEZONE = pytz.timezone('Europe/Paris')

# Flask configuration
FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'your-secret-key-here')
FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Content filtering settings
MIN_RELEVANCE_SCORE = 0.2
MAX_ARTICLES_PER_UPDATE = 100
DAYS_TO_KEEP_ARTICLES = 60 