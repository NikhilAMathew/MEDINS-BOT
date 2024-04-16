# import traceback
# from pymongo import MongoClient
# from rasa.core.tracker_store import TrackerStore
# from rasa.core.brokers.broker import EventBroker

# class MongoDBTrackerStore(TrackerStore):

#     def __init__(
#         self,
#         domain,
#         collection: str = "slot",
#         host: str = "localhost",
#         port: int = 27017,
#         db: str = "rasa",
#         event_broker: EventBroker = None,
#     ):
#         self.collection = collection
#         self.mongo_client = MongoClient(host, port)
#         self.db = self.mongo_client[db]
#         super().__init__(domain, event_broker)

#     def save(self, tracker) -> None:
#         try:
#             if self.event_broker:
#                 self.stream_events(tracker)

#             slots_data = self.extract_slots_data(tracker)
#             if slots_data:
#                 self.db[self.collection].replace_one(
#                     {"sender_id": tracker.sender_id},
#                     slots_data,
#                     upsert=True
#                 )

#         except Exception as e:
#             traceback.print_exc()

#     def retrieve(self, sender_id: str):
#         """Retrieve a tracker from MongoDB"""
#         data = self.db[self.collection].find_one({"sender_id": sender_id})
#         if data:
#             dialogue = self.deserialise_tracker(data)
#             return dialogue
#         else:
#             return None

#     def keys(self):
#         """Return sender_ids of the Tracker Store in MongoDB"""
#         return [doc["sender_id"] for doc in self.db[self.collection].find()]

#     def extract_slots_data(self, tracker) -> dict:
#         """Extract slot information from the tracker"""
#         existing_data = self.db[self.collection].find_one({"sender_id": tracker.sender_id})
    
#         if existing_data and "slots" in existing_data:
#             existing_slots = existing_data["slots"]
#         else:
#             existing_slots = {}

#         # Get slot values once and store the result
#         new_slots = tracker.current_slot_values()

#         # Update only non-None values from new_slots
#         merged_slots = {key: value for key, value in new_slots.items() if value is not None}

#         # Update existing_slots with non-None values from new_slots
#         for key, value in new_slots.items():
#             if value is not None:
#                 existing_slots[key] = value

#         slots_data = {
#             "sender_id": tracker.sender_id,
#             "slots": existing_slots,
#         }

#         return slots_data

#     def deserialise_tracker(self, data: dict):
#         """Deserialise tracker from MongoDB data"""
#         sender_id = data.get("sender_id", "")
#         return self.init_tracker(sender_id)