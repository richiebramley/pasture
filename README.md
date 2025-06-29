# AgriTech Newsfeed

A comprehensive newsfeed application focused on agritech and dairy/beef farming content, with particular emphasis on virtual fencing, herd control, pasture management, and optimization technologies.

## Features

- **Automated Content Collection**: Daily scraping of multiple agritech news sources
- **Smart Content Filtering**: AI-powered relevance scoring for farming and agritech content
- **Focus Areas**:
  - Virtual fencing and electronic boundary management
  - Herd control and livestock monitoring
  - Pasture management and optimization
  - Agricultural technology innovations
- **Modern Web Interface**: Responsive design with real-time updates
- **Scheduled Updates**: Automatic daily updates at 7am CET
- **Search & Filter**: Advanced search capabilities and category filtering
- **Export Functionality**: Export articles in JSON or CSV format

## News Sources

The application monitors the following sources:
- AgFunder News
- Farm Journal
- Dairy Herd Management
- Beef Magazine
- Precision Ag
- AgriTech Tomorrow
- Farm Equipment
- Successful Farming

## Technology Stack

- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **Database**: SQLite
- **Content Scraping**: BeautifulSoup, Feedparser, Newspaper3k
- **Scheduling**: Schedule library
- **Frontend**: Bootstrap 5, JavaScript
- **Styling**: Custom CSS with modern design

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pasture
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   python -c "from database import NewsDatabase; db = NewsDatabase(); print('Database initialized')"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the web interface**
   Open your browser and navigate to `http://localhost:8080`

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
```

### Customizing News Sources

Edit `config.py` to add or modify news sources:

```python
NEWS_SOURCES = [
    {
        'name': 'Your News Source',
        'url': 'https://yoursource.com/feed',
        'category': 'agritech'
    }
]
```

### Adjusting Keywords

Modify the `KEYWORDS` dictionary in `config.py` to customize content filtering:

```python
KEYWORDS = {
    'virtual_fencing': ['virtual fence', 'electronic fence', 'GPS fence'],
    'herd_control': ['herd management', 'cattle tracking'],
    # Add more categories...
}
```

## Usage

### Web Interface

1. **Browse Articles**: View the latest articles on the homepage
2. **Filter by Category**: Use the category buttons to filter content
3. **Search**: Use the search bar to find specific topics
4. **Export**: Download articles in JSON or CSV format
5. **Manual Update**: Click "Update Now" to fetch new articles immediately

### API Endpoints

- `GET /api/articles` - Get articles with optional filters
- `GET /api/stats` - Get database statistics
- `POST /api/update` - Trigger manual newsfeed update

### Command Line

Run the scheduler independently:

```bash
python scheduler.py
```

## Scheduling

The application automatically updates at 7am CET daily. To modify the schedule:

1. Edit `config.py`
2. Change `SCHEDULE_TIME` to your preferred time
3. Restart the application

## Database Schema

### Articles Table
- `id`: Primary key
- `title`: Article title
- `description`: Article description/summary
- `content`: Full article content
- `url`: Article URL
- `source`: News source name
- `category`: Content category
- `published_date`: Publication date
- `relevance_score`: AI-calculated relevance score
- `keywords_matched`: JSON array of matched keywords
- `created_at`: Record creation timestamp

### Sources Table
- `id`: Primary key
- `name`: Source name
- `url`: RSS feed URL
- `category`: Source category
- `last_fetch`: Last fetch timestamp
- `status`: Source status (active/inactive)

### Fetch Log Table
- `id`: Primary key
- `source_name`: Source name
- `articles_found`: Number of articles found
- `articles_added`: Number of articles added
- `fetch_time`: Fetch timestamp
- `status`: Fetch status

## Content Filtering

The application uses a sophisticated content filtering system:

1. **Keyword Matching**: Searches for relevant keywords in titles and descriptions
2. **Category Weighting**: Different weights for different topic categories
3. **Relevance Scoring**: Calculates a relevance score (0-1) for each article
4. **Minimum Threshold**: Only articles above the minimum relevance score are included

## Troubleshooting

### Common Issues

1. **No articles appearing**
   - Check if the scheduler is running
   - Verify news source URLs are accessible
   - Run a manual update

2. **Scheduler not working**
   - Ensure the application is running continuously
   - Check timezone settings in `config.py`
   - Verify the schedule time format

3. **Database errors**
   - Delete `newsfeed.db` and restart the application
   - Check file permissions

### Logs

The application logs to the console. For production deployment, consider redirecting logs to files.

## Development

### Project Structure

```
pasture/
├── app.py                 # Flask web application
├── config.py             # Configuration settings
├── database.py           # Database operations
├── content_filter.py     # Content filtering logic
├── news_scraper.py       # Web scraping functionality
├── scheduler.py          # Scheduled updates
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   └── search.html
├── static/               # Static assets
│   ├── css/
│   └── js/
└── README.md
```

### Adding New Features

1. **New News Sources**: Add to `NEWS_SOURCES` in `config.py`
2. **New Categories**: Update `KEYWORDS` and category lists
3. **New Filters**: Modify `content_filter.py`
4. **UI Changes**: Edit templates in `templates/`

## Deployment

### Production Setup

1. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set up a reverse proxy** (nginx recommended)

3. **Use a process manager** (systemd, supervisor, etc.)

4. **Configure environment variables**:
   ```env
   FLASK_SECRET_KEY=your-production-secret-key
   FLASK_DEBUG=False
   ```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub

## Roadmap

- [ ] Email notifications for new articles
- [ ] RSS feed generation
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Integration with social media
- [ ] Machine learning improvements for content filtering 