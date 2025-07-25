from pymongo import MongoClient
from pymongo.errors import BulkWriteError
from settings.settings import logging
from settings.settings import (
    MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLLECTION
)

class MongoDBInserter:
    def __init__(self):
        self.server = None
        self.client = None
        self.collection = None

    def connect(self):
        try:
            self.client = MongoClient(f"mongodb://{MONGO_HOST}:{MONGO_PORT}/")
            self.collection = self.client[MONGO_DB][MONGO_COLLECTION]
            self.collection.create_index("vecID", unique=True)
        except Exception as e:
            logging.error(f"MongoDB Connection error: {e}")
            raise

    def insert_document_list(self, docs, page_num=None):
        if self.collection is None:
            self.connect()
        inserted_count = 0
        duplicate_count = 0
        other_error_count = 0
        try:
            result = self.collection.insert_many(docs, ordered=False)
            inserted_count = len(result.inserted_ids)
        except BulkWriteError as bwe:
            errors = bwe.details.get('writeErrors', [])
            for err in errors:
                if err.get('code') == 11000:
                    duplicate_count += 1
                else:
                    other_error_count += 1
            # Even if there are errors, some docs may be inserted
            inserted_count = bwe.details.get('nInserted', 0)
        except Exception as e:
            other_error_count += 1
            logging.error(f"Critical insert error: {e}")

        total = len(docs)
        msg = f"    Crawled Page {page_num}: {total} articles | {inserted_count} inserted | {duplicate_count} duplicates"
        if other_error_count:
            msg += f" | {other_error_count} other errors"
        logging.info(msg)

    def close(self):
        if self.client:
            self.client.close()
        if self.server:
            self.server.stop()