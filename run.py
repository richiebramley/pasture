#!/usr/bin/env python3
"""
AgriTech Newsfeed Runner
Simple script to start the newsfeed application
"""

import os
import sys
from app import app

if __name__ == '__main__':
    print("🌱 Starting AgriTech Newsfeed...")
    print("📰 Focus: Virtual fencing, herd control, pasture management")
    print("⏰ Updates: Daily at 7am CET")
    
    # Set default environment variables if not set
    if not os.environ.get('FLASK_SECRET_KEY'):
        os.environ['FLASK_SECRET_KEY'] = 'dev-secret-key-change-in-production'
    
    # Get port from environment (Railway sets PORT)
    port = int(os.environ.get('PORT', 8080))
    
    # Set debug mode based on environment
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🌐 Web interface: http://localhost:{port}")
    print("=" * 50)
    
    try:
        app.run(debug=debug, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AgriTech Newsfeed...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1) 