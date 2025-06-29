from flask import Flask, render_template, request, jsonify, redirect, url_for
import datetime
import pytz
from database import NewsDatabase
from content_filter import ContentFilter
from scheduler import NewsfeedScheduler
import config

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET_KEY

# Initialize components
db = NewsDatabase()
content_filter = ContentFilter()
scheduler = NewsfeedScheduler()

@app.route('/')
def index():
    """Main newsfeed page"""
    # Get filter parameters
    category = request.args.get('category', 'all')
    days = int(request.args.get('days', 30))  # Extended from 7 to 30 days
    limit = int(request.args.get('limit', 12))  # Reduced limit for better pagination
    page = int(request.args.get('page', 1))
    relevance = float(request.args.get('relevance', 0.8))
    
    # Calculate offset for pagination
    offset = (page - 1) * limit
    
    # Get articles with pagination
    if category == 'all':
        articles = db.get_articles(limit=limit, days_back=days, offset=offset, min_relevance=relevance)
    else:
        articles = db.get_articles(limit=limit, category=category, days_back=days, offset=offset, min_relevance=relevance)
    
    # Get total count for pagination
    total_articles = db.get_articles_count(category=category if category != 'all' else None, days_back=days)
    total_pages = (total_articles + limit - 1) // limit
    
    # Get statistics
    stats = db.get_stats()
    
    # Get scheduler status
    scheduler_status = scheduler.get_scheduler_status()
    
    return render_template('index.html', 
                         articles=articles, 
                         stats=stats,
                         scheduler_status=scheduler_status,
                         current_category=category,
                         current_days=days,
                         current_page=page,
                         total_pages=total_pages,
                         total_articles=total_articles,
                         current_relevance=relevance,
                         datetime=datetime)

@app.route('/api/articles')
def api_articles():
    """API endpoint for articles"""
    category = request.args.get('category')
    days = int(request.args.get('days', 30))  # Extended from 7 to 30 days
    limit = int(request.args.get('limit', 12))
    page = int(request.args.get('page', 1))
    offset = (page - 1) * limit
    
    if category and category != 'all':
        articles = db.get_articles(limit=limit, category=category, days_back=days, offset=offset)
    else:
        articles = db.get_articles(limit=limit, days_back=days, offset=offset)
    
    return jsonify(articles)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = db.get_stats()
    return jsonify(stats)

@app.route('/api/update', methods=['POST'])
def manual_update():
    """Trigger a manual newsfeed update"""
    try:
        scheduler.run_manual_update()
        return jsonify({'status': 'success', 'message': 'Newsfeed updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/search')
def search():
    """Search articles by keywords"""
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('index'))
    
    # Search in database
    articles = db.get_articles_by_keywords([query], limit=50)
    stats = db.get_stats()
    scheduler_status = scheduler.get_scheduler_status()
    
    return render_template(
        'search.html',
        articles=articles,
        query=query,
        stats=stats,
        scheduler_status=scheduler_status
    )

@app.route('/category/<category>')
def category(category):
    """Filter articles by category"""
    articles = db.get_articles(category=category, limit=50)
    stats = db.get_stats()
    
    return render_template('category.html', 
                         articles=articles, 
                         category=category,
                         stats=stats)

@app.route('/article/<int:article_id>')
def article_detail(article_id):
    """Show detailed article view"""
    # This would need to be implemented in the database class
    # For now, redirect to the original URL
    return redirect(url_for('index'))

@app.template_filter('format_date')
def format_date(date_string):
    """Format date for display"""
    try:
        dt = datetime.datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%H:%M %d/%m/%Y')
    except Exception:
        return date_string

@app.template_filter('truncate')
def truncate(text, length=200):
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length] + '...'

@app.context_processor
def inject_categories():
    """Inject categories into all templates"""
    return {
        'categories': [
            {'id': 'all', 'name': 'All Articles'},
            {'id': 'virtual_fencing', 'name': 'Virtual Fencing'},
            {'id': 'herd_control', 'name': 'Herd Control'},
            {'id': 'pasture_management', 'name': 'Pasture Management'},
            {'id': 'agritech', 'name': 'AgriTech'},
            {'id': 'dairy', 'name': 'Dairy'},
            {'id': 'beef', 'name': 'Beef'},
            {'id': 'equipment', 'name': 'Equipment'},
            {'id': 'technology', 'name': 'Technology'},
            {'id': 'general', 'name': 'General Farming'}
        ]
    }

if __name__ == '__main__':
    # Start the scheduler in background
    scheduler.schedule_daily_update()
    scheduler.start_background_scheduler()
    
    # Run the Flask app
    app.run(debug=config.FLASK_DEBUG, host='0.0.0.0', port=8080) 