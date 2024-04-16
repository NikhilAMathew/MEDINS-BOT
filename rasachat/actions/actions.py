from typing import Any, Text, Dict, List
from pymongo import MongoClient
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from datetime import datetime
import re

number = None

class ActionSaveDetails(Action):
    def name(self) -> Text:
        return "action_save_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        global number

        client = MongoClient("mongodb://localhost:27017")
        db = client['rasa']

        name = tracker.get_slot("name")
        dob = tracker.get_slot("dob")
        address = tracker.get_slot("address")
        email = tracker.get_slot("email")
        number = tracker.get_slot("number")
        select_policy = tracker.get_slot("select_policy")
        purchase_policy = tracker.get_slot("purchase_policy")

        document = {
            "name": name,
            "dob": dob,
            "address": address,
            "email": email,
            "number": number,
            "select_policy": select_policy,
            "purchase_policy": purchase_policy
        }
        print(document)
        # Save the document to MongoDB
        db.user_details.insert_one(document)

        return [SlotSet("number", number), SlotSet("name", name), SlotSet("dob", dob), SlotSet("email", email), SlotSet("address", address), SlotSet("purchase_policy", purchase_policy), SlotSet("select_policy", select_policy)]


def calculate_age(dob):
    dob_date = datetime.strptime(dob, "%d/%m/%Y")
    today = datetime.today()
    age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
    return age

class ActionInsurance(Action):
    def name(self) -> Text:
        return "action_insurance_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dob = tracker.get_slot("dob")
        age = calculate_age(dob)
        print("Age:", age)

        if age is not None:
            age = int(age)
            if age > 18 and age <= 35:
                dispatcher.utter_message("You belong to the young adult category.")
            elif  age > 35 and age <= 60:
                dispatcher.utter_message("You are eligible for senior citizen insurance.")
            else:
                dispatcher.utter_message("You do not belong to the young adult category.")
        else:
            dispatcher.utter_message("Age slot is not filled.")

        return []


class ActionPolicySchemes(Action):
    def name(self) -> Text:
        return "action_policy_schemes"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("custom action")
        # Here you would fetch policy schemes from your database or any other source
        buttons = [
            {"title": "Care Supreme Direct","payload":"/csd"},
            {"title": " Individual Health Guard – Gold","payload":"/ihgg"},
            {"title": "Health Gain","payload":"/hg"},
            {"title": " ReAssure 2.0 Bronze+ (Direct)","payload":"/read"},
            {"title": "Smart Health Pro","payload":"/shp"}
        ]

        dispatcher.utter_message(text="Here are the available policy schemes:", buttons=buttons)

        return []

class ActionSelectPolicy(Action):
    def name(self) -> Text:
        return "action_select_policy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        client = MongoClient("mongodb://localhost:27017")
        db = client['rasa']
        # print("select policy")
        selected_policy = tracker.get_slot("policy")
        print(selected_policy)

        global number

        if selected_policy:
            # Update the selected policy in the document
            db.user_details.update_one(
                {"number": number},
                {"$set": {"select_policy": selected_policy}}
            )

            response = f"You selected {selected_policy}. Here are the details of this policy..."

            dispatcher.utter_message(response)
        else:
            dispatcher.utter_message("No policy selected.")

        return []

class ActionPurchasePolicy(Action):

    def name(self) -> Text:
        return "action_purchase_policy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        buttons= [
                        {
                        "title": "Confirm",
                        "payload": "/confirm"
                        },
                        {
                            "title": "Cancel",
                            "payload": "/cancel"
                        }
                    ]

        dispatcher.utter_message(text="<h1>Confirmation</h2>You want to confirm the",buttons=buttons)
        return []