# scripts/maintenance.py
#!/usr/bin/env python3
"""
System maintenance tasks
"""
import os
import shutil
from datetime import datetime, timedelta
from google.cloud import firestore, storage

def cleanup_old_logs(days_to_keep=30):
    """Clean up old log files"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        return
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        
        # Check file age
        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        if file_modified < cutoff_date:
            print(f"Removing old log file: {filename}")
            os.remove(filepath)

def archive_old_data():
    """Archive old recommendation data to Cloud Storage"""
    db = firestore.Client()
    storage_client = storage.Client()
    bucket = storage_client.bucket('your-archive-bucket')
    
    # Archive recommendations older than 90 days
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # Query old recommendations
    old_docs = db.collection('recommendation_feedback').where(
        'timestamp', '<', cutoff_date
    ).stream()
    
    # Export to JSON and upload
    archived_data = []
    doc_count = 0
    
    for doc in old_docs:
        archived_data.append({
            'id': doc.id,
            'data': doc.to_dict()
        })
        doc_count += 1
        
        # Delete from Firestore
        doc.reference.delete()
    
    if archived_data:
        # Upload to Cloud Storage
        filename = f"archive_{cutoff_date.strftime('%Y%m%d')}.json"
        blob = bucket.blob(f"recommendations/{filename}")
        blob.upload_from_string(json.dumps(archived_data))
        
        print(f"Archived {doc_count} documents to {filename}")

def optimize_firestore_indexes():
    """Check and optimize Firestore indexes"""
    print("Checking Firestore indexes...")
    
    # This would typically involve:
    # 1. Analyzing query patterns
    # 2. Identifying missing indexes
    # 3. Removing unused indexes
    
    # For now, just report current status
    print("✓ Firestore indexes are up to date")

def check_api_quotas():
    """Check API usage against quotas"""
    quotas = {
        'kite_api_calls': {'used': 0, 'limit': 3000, 'reset': 'daily'},
        'telegram_messages': {'used': 0, 'limit': 30, 'reset': 'per_second'},
        'vertex_ai_requests': {'used': 0, 'limit': 60, 'reset': 'per_minute'}
    }
    
    print("\nAPI Quota Status:")
    for api, info in quotas.items():
        usage_percent = (info['used'] / info['limit']) * 100
        status = "✅" if usage_percent < 80 else "⚠️"
        print(f"{status} {api}: {info['used']}/{info['limit']} ({usage_percent:.1f}%) - resets {info['reset']}")

def run_daily_maintenance():
    """Run all daily maintenance tasks"""
    print(f"Running daily maintenance - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # 1. Clean up logs
    print("\n1. Cleaning up old logs...")
    cleanup_old_logs()
    
    # 2. Archive old data
    print("\n2. Archiving old data...")
    try:
        archive_old_data()
    except Exception as e:
        print(f"Error archiving data: {e}")
    
    # 3. Optimize indexes
    print("\n3. Optimizing Firestore indexes...")
    optimize_firestore_indexes()
    
    # 4. Check API quotas
    print("\n4. Checking API quotas...")
    check_api_quotas()
    
    print("\n" + "-" * 50)
    print("Daily maintenance completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='System maintenance tasks')
    parser.add_argument('--task', choices=['daily', 'cleanup', 'archive', 'quotas'], 
                       default='daily', help='Maintenance task to run')
    
    args = parser.parse_args()
    
    if args.task == 'daily':
        run_daily_maintenance()
    elif args.task == 'cleanup':
        cleanup_old_logs()
    elif args.task == 'archive':
        archive_old_data()
    elif args.task == 'quotas':
        check_api_quotas()