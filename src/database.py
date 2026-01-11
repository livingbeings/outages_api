import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "outages_db")

class Database:
    client: AsyncIOMotorClient = None
    db = None

    def connect(self):
        """Connecting database"""
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        logging.info(f"Connected to MongoDB at {MONGO_URL}, database: {DB_NAME}")

    def close(self):
        """Closing database"""
        if self.client:
            self.client.close()
            logging.info("Closed MongoDB connection")

db = Database()

def get_database():
    return db.db
