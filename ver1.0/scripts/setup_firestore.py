# scripts/setup_firestore.py
#!/usr/bin/env python3
"""
Setup Firestore collections and initial data
"""
from google.cloud import firestore
from datetime import datetime
import os

def setup_firestore():
    """Setup Firestore collections"""
    # Initialize Firestore
    db = firestore.Client()
    
    print("Setting up Firestore collections...")
    
    # Create collections
    collections = [
        'recommendation_feedback',
        'system_config',
        'performance_metrics',
        'market_snapshots'
    ]
    
    for collection_name in collections:
        # Add a dummy document to create collection
        doc_ref = db.collection(collection_name).document('_init')
        doc_ref.set({
            'created_at': datetime.now(),
            'purpose': 'Collection initialization'
        })
        print(f"✓ Created collection: {collection_name}")
    
    # Add default system configuration
    config_ref = db.collection('system_config').document('default')
    config_ref.set({
        'supertrend_period_1': 10,
        'supertrend_multiplier_1': 1.0,
        'supertrend_period_2': 10,
        'supertrend_multiplier_2': 3.0,
        'adx_threshold': 20,
        'vix_threshold': 25,
        'signal_cooldown_minutes': 30,
        'confidence_threshold': 0.6,
        'updated_at': datetime.now()
    })
    print("✓ Added default configuration")
    
    print("\nFirestore setup completed successfully!")

if __name__ == "__main__":
    # Set project ID if not already set
    if 'GOOGLE_CLOUD_PROJECT' not in os.environ:
        project_id = input("Enter your GCP Project ID: ")
        os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
    
    setup_firestore()