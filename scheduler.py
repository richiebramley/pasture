import schedule
import time
import threading
from datetime import datetime
import pytz
import config
from news_scraper import NewsScraper
from database import NewsDatabase
from content_filter import ContentFilter

class NewsfeedScheduler:
    def __init__(self):
        self.scraper = NewsScraper()
        self.database = NewsDatabase()
        self.content_filter = ContentFilter()
        self.timezone = config.TIMEZONE
        self.is_running = False
    
    def update_newsfeed(self):
        """Main function to update the newsfeed"""
        print(f"Starting newsfeed update at {datetime.now(self.timezone)}")
        
        try:
            # Scrape all sources
            print("Scraping news sources...")
            articles = self.scraper.scrape_all_sources()
            
            print(f"Found {len(articles)} articles from all sources")
            
            # Filter for relevant content
            print("Filtering for relevant content...")
            filtered_articles = self.content_filter.filter_articles(articles)
            
            print(f"Found {len(filtered_articles)} relevant articles")
            
            # Add articles to database
            added_count = 0
            for article in filtered_articles:
                if self.database.add_article(article):
                    added_count += 1
            
            print(f"Added {added_count} new articles to database")
            
            # Log the fetch operation
            self.database.log_fetch(
                source_name="all_sources",
                articles_found=len(articles),
                articles_added=added_count,
                status="success"
            )
            
            # Cleanup old articles
            self.database.cleanup_old_articles()
            
            print(f"Newsfeed update completed at {datetime.now(self.timezone)}")
            
        except Exception as e:
            print(f"Error during newsfeed update: {e}")
            self.database.log_fetch(
                source_name="all_sources",
                articles_found=0,
                articles_added=0,
                status=f"error: {str(e)}"
            )
    
    def schedule_daily_update(self):
        """Schedule the daily update at 7am CET"""
        schedule.every().day.at(config.SCHEDULE_TIME).timezone(self.timezone).do(self.update_newsfeed)
        print(f"Scheduled daily newsfeed update at {config.SCHEDULE_TIME} {self.timezone}")
    
    def run_scheduler(self):
        """Run the scheduler in a loop"""
        self.is_running = True
        print("Starting newsfeed scheduler...")
        
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def start_background_scheduler(self):
        """Start the scheduler in a background thread"""
        scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        print("Background scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        print("Scheduler stopped")
    
    def run_manual_update(self):
        """Run a manual update immediately"""
        print("Running manual newsfeed update...")
        self.update_newsfeed()
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        jobs = schedule.get_jobs()
        if jobs:
            return jobs[0].next_run
        return None
    
    def get_scheduler_status(self):
        """Get current scheduler status"""
        return {
            'is_running': self.is_running,
            'next_run': self.get_next_run_time(),
            'timezone': str(self.timezone),
            'schedule_time': config.SCHEDULE_TIME
        }

def main():
    """Main function to run the scheduler"""
    scheduler = NewsfeedScheduler()
    
    # Schedule daily updates
    scheduler.schedule_daily_update()
    
    # Run a manual update on startup
    print("Running initial newsfeed update...")
    scheduler.run_manual_update()
    
    # Start the scheduler
    scheduler.start_background_scheduler()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down scheduler...")
        scheduler.stop_scheduler()

if __name__ == "__main__":
    main() 