# Save this as upload_all_data.py in your backend folder
import asyncio
import requests
import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# ============================================
# CONFIGURATION - UPDATE THESE IF NEEDED
# ============================================
BACKEND_URL = "http://127.0.0.1:8000"
MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "carbon_tracker_db"  

MONTHLY_CSV_PATH = "feature 1/monthly_emissions_summary.csv"
AVERAGE_CSV_PATH = "feature 1/average_emissions.csv"

# ============================================
# 1. UPLOAD MONTHLY DATA (via API endpoint)
# ============================================
def upload_monthly_data():
    print("📊 Uploading monthly emissions data...")
    
    with open(MONTHLY_CSV_PATH, 'rb') as f:
        files = {'file': (MONTHLY_CSV_PATH, f, 'text/csv')}
        response = requests.post(
            f'{BACKEND_URL}/api/v1/emissions/upload/', 
            files=files
        )
    
    if response.status_code == 200:
        print(f"✅ Monthly data uploaded successfully!")
        print(f"   Response: {response.json()}")
    else:
        print(f"❌ Monthly upload failed: {response.status_code}")
        print(f"   Error: {response.text}")

# ============================================
# 2. UPLOAD AVERAGE DATA (directly to MongoDB)
# ============================================
async def upload_average_data():
    print("\n📈 Uploading average emissions data...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    
    # Read the average CSV
    df = pd.read_csv(AVERAGE_CSV_PATH)
    
    # Prepare document
    avg_doc = {
        "average_emissions_ppm": df.iloc[0].to_dict(),
        "ingested_at": datetime.utcnow()
    }
    
    # Clear and insert into overall_averages collection
    await db["overall_averages"].delete_many({})
    result = await db["overall_averages"].insert_one(avg_doc)
    
    print(f"✅ Average data uploaded successfully!")
    print(f"   Document ID: {result.inserted_id}")
    
    client.close()

# ============================================
# 3. VERIFY DATA
# ============================================
def verify_data():
    print("\n🔍 Verifying uploaded data...")
    
    # Check monthly data
    monthly_response = requests.get(f'{BACKEND_URL}/api/v1/emissions/monthly/')
    if monthly_response.status_code == 200:
        monthly_count = len(monthly_response.json())
        print(f"✅ Monthly data: {monthly_count} records found")
    else:
        print(f"❌ Monthly data check failed: {monthly_response.status_code}")
    
    # Check average data
    average_response = requests.get(f'{BACKEND_URL}/api/v1/emissions/average/')
    if average_response.status_code == 200:
        print(f"✅ Average data: Found")
    else:
        print(f"❌ Average data check failed: {average_response.status_code}")

# ============================================
# MAIN EXECUTION
# ============================================
async def main():
    print("🚀 Starting data upload process...\n")
    print("=" * 50)
    
    # Step 1: Upload monthly data via API
    upload_monthly_data()
    
    # Step 2: Upload average data to MongoDB
    await upload_average_data()
    
    # Step 3: Verify both datasets
    verify_data()
    
    print("\n" + "=" * 50)
    print("✨ Upload process complete!")
    print("\n📱 Your frontend should now display real data!")
    print(f"   Visit: {BACKEND_URL}/docs to verify")

if __name__ == "__main__":
    asyncio.run(main())