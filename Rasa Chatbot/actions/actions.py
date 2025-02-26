# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from math import ceil
import os
import random
from firebase_admin import firestore, credentials, _apps, initialize_app
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType, FollowupAction, AllSlotsReset
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.types import DomainDict
from datetime import datetime

# Use a service account.
#CHANGED MOVED PATH        
path_cwd = os.getcwd()
cred_path = os.path.join(path_cwd, "service account\knowledgebase.json")
        
if not _apps:
    cred = credentials.Certificate(cred_path)
    initialize_app(cred)        
db = firestore.client()

#CHANGED (ADD NEW ACTIONS)
class AskForUserformPerson(Action):
    def name(self)-> Text:
        return "action_ask_user_form_PERSON"
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        doc_ref = db.collection("Dialogue").document("PERSON")
        doc = doc_ref.get()

        if doc.exists:
            response_list = doc.to_dict().get("terms", [])
            if response_list:
                chosen_response = random.choice(response_list)  # Pick a random response
                dispatcher.utter_message(text=chosen_response)
            else:
                dispatcher.utter_message(text="Hello! What would you like me to call you?")
        else:
            dispatcher.utter_message(text="Hi! What would you like me to call you?")
        return []
#CHANGED (ADD NEW ACTIONS)
class AskForUserformAge(Action):
    def name(self)-> Text:
        return "action_ask_user_form_age"
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        doc_ref = db.collection("Dialogue").document("age")
        doc = doc_ref.get()

        if doc.exists:
            response_list = doc.to_dict().get("terms", [])
            if response_list:
                chosen_response = random.choice(response_list)  # Pick a random response
                dispatcher.utter_message(text=chosen_response)
            else:
                dispatcher.utter_message(text="How old are you?")
        else:
            dispatcher.utter_message(text="What is your age? This will help me tailor the process better for your needs.")
        return []
#CHANGED (ADD NEW ACTIONS)
class AskForUserformMeno(Action):
    def name(self)-> Text:
        return "action_ask_user_form_isMenopause"
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        doc_ref = db.collection("Dialogue").document("isMenopause")
        doc = doc_ref.get()

        if doc.exists:
            response_list = doc.to_dict().get("terms", [])
            if response_list:
                chosen_response = random.choice(response_list)  # Pick a random response
                dispatcher.utter_message(text=chosen_response)
            else:
                dispatcher.utter_message(text="Have you reached menopause?")
        else:
            dispatcher.utter_message(text="Have you reached menopause?")
        return []
#CHANGED (ADD NEW ACTIONS)
class ActionAskTerms (Action):
    def name(self) -> Text:
        return "action_ask_terms"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:

        #Fetch responses from Firestore
        doc_ref = db.collection("Dialogue").document("scope")
        doc = doc_ref.get()

        if doc.exists:
            response_list = doc.to_dict().get("terms", [])
            if response_list:
                chosen_response = random.choice(response_list)  # Pick a random response
                dispatcher.utter_message(text=chosen_response)
            else:
                dispatcher.utter_message(text="Please seek a professional as this is a chatbot meant to help your journey along menstrual health")
        else:
            dispatcher.utter_message(text="Please seek a professional as this is a chatbot meant to help your journey along menstrual health")

        dispatcher.utter_message(text=f"Do you acknowledge that I am not a doctor or a medical professional and that my impressions must not be treated as a diagnosis?")
        
        return []
    
class ValidateDisclaimerForm(FormValidationAction):
    def name(self):
        return "validate_disclaimer_form"
    
    def validate_terms(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        intent = tracker.get_intent_of_latest_message()
        if slot_value == True:
            return {"terms": slot_value}
        
        dispatcher.utter_message(text="I am very sorry, but I cannot proceed with a session unless you agree to these terms :(")
        return {"terms": None}

#CHANGED (ADD NEW ACTIONS)   
class Action_Feelings(Action):
    def name(self):
        return "action_feelings"

    def run(self, dispatcher: CollectingDispatcher, tracker, domain):

        guidelines = f"""How to Interact with me 😃:
        \n- For questions with a ℹ️ icon, respond with "yes" or "no." If you need more information, you can reply with "What is that?"
        \n- For questions about duration, reply with a whole number. If you are not sure, you can reply with "I don’t know."
        \n- For questions about intensity, use a scale from 0 to 10."""

        dispatcher.utter_message(text=f"{guidelines}")

        # Fetch responses from Firestore
        doc_ref = db.collection("Dialogue").document("feelings")
        doc = doc_ref.get()

        if doc.exists:
            response_list = doc.to_dict().get("terms", [])
            if response_list:
                chosen_response = random.choice(response_list)  # Pick a random response
                dispatcher.utter_message(text=chosen_response)
            else:
                dispatcher.utter_message(text="How are you feeling?")
        else:
            dispatcher.utter_message(text="Are there any symptoms you have been noticing recently?")

        return []

# UTTER SYMPTOM #CHANGED
class ActionSaySymptom(Action):

    def name(self) -> Text:
        return "action_say_symptom"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        symptom = tracker.get_slot("symptom")
        context = tracker.get_slot("context")
        symptom_list = tracker.get_slot("symptom_context_list") or []
        
        new_symptom_list = list(symptom_list)
        
        if not context:
            if symptom:
                doc_ref = db.collection("Dialogue").document("symp_noCon")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                symp = random.choice(response_list)
                fsymp = symp.format(symptom=symptom) if "{symptom}" in symp else symp
                dispatcher.utter_message(text=fsymp)
                #dispatcher.utter_message(text=f"Your symptom is {symptom}. Let me see how I can help!")
            new_symptom_list.append(symptom)
            # Create a new session
            create_new = {
                "control": "create_new_session"
            }
            
            dispatcher.utter_message(json_message=create_new)
            return [SlotSet("symptom", None), SlotSet("context", None), SlotSet("symptom_context_list", new_symptom_list)]
        
        doc_ref = db.collection("Dialogue").document("symp_withCon")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        symp = random.choice(response_list)
        fsymp = symp.format(symptom=symptom,context=context) if "{symptom}" in symp and "{context}" in symp else symp
        dispatcher.utter_message(text=fsymp)        
        #dispatcher.utter_message(text=f"Your symptom is: {symptom}, specifically with {context}. Let me see how I can help!") #CHANGED
        new_symptom_list.append({"symptom": symptom, "context": context})
        
        return [SlotSet("symptom", None), SlotSet("context", None), SlotSet("symptom_context_list", new_symptom_list)]

# UTTER SYMPTOM LIST
# class ActionRepeatSymptom(Action):

#     def name(self) -> Text:
#         return "action_repeat_symptoms"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         symptom_list = tracker.get_slot("symptom_context_list")

#         if not symptom_list:
#             dispatcher.utter_message(text="Sorry, it seems that I do not have any information stored about your symptoms")
#             dispatcher.utter_message(text="What are you experiencing as of the moment?")
#             return []
        
#         # change to make it so it rereads all symptoms stored   
#         dispatcher.utter_message(text="Your symptoms include:")
#         for index, entry in enumerate(symptom_list, start=1):
#             symptom = entry.get("symptom")
#             context = entry.get("context")
#             dispatcher.utter_message(text=f"{index}.) Your symptom is: {symptom}, specifically with {context}.")
            
#         dispatcher.utter_message(text="End of symptom list")
        
#         return []

#CHANGED
class ActionSetUserInfo(Action):
    def name(self) -> Text:
        return "action_set_user_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # Get metadata
        metadata = tracker.latest_message.get("metadata", {})
        
        # Get the specific values
        username = metadata.get("username", "default_user")
        age = metadata.get("age", 0)
        isMenopause = metadata.get("isMenopause", False)
        
        # Get the current hour
        current_hour = datetime.now().hour

        # Determine the appropriate greeting
        if 5 <= current_hour < 12:
            greeting = f"Good morning, {username} 🌅"
        elif 12 <= current_hour < 18:
            greeting = f"Good afternoon, {username} 🌞"
        else:
            greeting = f"Good evening, {username} 🌙"

        # Respond to the user
        dispatcher.utter_message(text=f"{greeting}!")
        if isMenopause:
            doc_ref = db.collection("Dialogue").document("meno_reminder1")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            meno1 = random.choice(response_list)

            doc_ref = db.collection("Dialogue").document("meno_reminder2")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            meno2 = random.choice(response_list)
            # Respond to the user
            formatted_meno1 = meno1.format(username=username) if "{username}" in meno1 else meno1
            formatted_meno2 = meno2.format(username=username) if "{username}" in meno2 else meno2
            #dispatcher.utter_message(text=f"Just a friendly reminder, {username}☝️. I am designed to provide impressions and insights primarily for people who have not yet entered menopause. 🙏")
            #dispatcher.utter_message(text=f"If your concerns are still present, I would advise seeking a medical professional directly and immediately. 🩺🙂")
            dispatcher.utter_message(text=formatted_meno1)#CHANGED
            dispatcher.utter_message(text=formatted_meno2) #CHANGED

        return [
            SlotSet("PERSON", username),
            SlotSet("age", age),
            SlotSet("isMenopause", isMenopause)
        ]

class ActionClearUserInfo(Action):

    def name(self) -> Text:
        return "action_clear_user_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return[SlotSet("PERSON", None),
            SlotSet("age", None),
            SlotSet("isMenopause", None)]


# SET THE USER'S AGE TO A SLOT
#CHANGED
class ActionSubmitUserInfo(Action):

    def name(self) -> Text:
        return "action_submit_user_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        age = tracker.get_slot("age")
        name = tracker.get_slot("PERSON")
        isMenopause = tracker.get_slot("isMenopause")
        doc_ref = db.collection("Dialogue").document("meno_reminder1")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        meno1 = random.choice(response_list)
        fmeno1 = meno1.format(username=name) if "{username}" in meno1 else meno1

        doc_ref = db.collection("Dialogue").document("greetings 2")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        greet = random.choice(response_list)
        fgreet= greet.format(name=name) if "{name}" in greet else greet

        if isMenopause:
            dispatcher.utter_message(text=fmeno1) #CHANGED
            #dispatcher.utter_message(text=f"Also, {name}👋, I want you to know that I am designed to provide impressions and insights primarily for people who have not yet entered menopause. 🤔")
        dispatcher.utter_message(text=fgreet) #CHANGED
        #dispatcher.utter_message(text=f"Nice to meet you, {name}")
        
        user_data = {
            "control": "record_user_info",
            "data": {
                "name": name,
                "age": age,
                "isMenopause": isMenopause
            }
        }
        
        dispatcher.utter_message(json_message=user_data)
        
        return [SlotSet("age", age), SlotSet("PERSON", name), SlotSet("isMenopause", isMenopause)]

# FLAG IF CHATBOT LISTENING FOR AFFIRMATION
# class ActionTriggerListenNew(Action):

#     def name(self) -> Text:
#         return "action_trigger_listen_new"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         listen = tracker.get_slot("asked_new")
        
#         listen = not listen
        
#         return [SlotSet("asked_new", listen)]
        

# Test function to see user data stored in chatbot
#CHANGED
class ActionGetUserData(Action):

    def name(self) -> Text:
        return "action_get_user_data"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        name = tracker.get_slot("PERSON")
        age = tracker.get_slot("age")
        new = tracker.get_slot("is_new_user")
        asking = tracker.get_slot("asked_new")
        
        if not name:
            doc_ref = db.collection("Dialogue").document("no_name")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            no_n = random.choice(response_list) 
            dispatcher.utter_message(text=no_n) 
            #dispatcher.utter_message(text="Sorry, it seems that I have not stored your name") #CHANGED
        if not age:
            doc_ref = db.collection("Dialogue").document("no_age")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            no_a = random.choice(response_list) 
            dispatcher.utter_message(text=no_a) 
            #dispatcher.utter_message(text="Sorry, it seems that I do not have your age") #CHANGED
        
        if age and name:
            doc_ref = db.collection("Dialogue").document("name_age")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            na_age = random.choice(response_list)
            fna1= na_age.format(name=name,age=age,new=new) if "{name}" in na_age and "{age}" in na_age and "{new}" in na_age else na_age
            dispatcher.utter_message(text=fna1)
            #dispatcher.utter_message(text=f"User: {name}\nAge: {age}\nNew User?: {new}") #CHANGED
        else:
            doc_ref = db.collection("Dialogue").document("no_name_age")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            no_na_age = random.choice(response_list)
            fna1= no_na_age.format(new=new) if "{new}" in no_na_age else no_na_age
            dispatcher.utter_message(text=fna1)
            #dispatcher.utter_message(text=f"Missing Age or Name\nNew User?: {new}.")#CHANGED
        doc_ref = db.collection("Dialogue").document("asking")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        askin = random.choice(response_list)
        fask= askin.format(asking=asking) if "{asking}" in askin else askin
        dispatcher.utter_message(text=fask)    
        #dispatcher.utter_message(text=f"Asking If New?: {asking}")#CHANGED
        
        return []
    
# KNOWLEDGE BASE
class ActionConsultKnowledge(Action):
    def name(self) -> str:
        return "action_consult_knowledge"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        batch_size = 30
        
        current_symptom = tracker.get_slot("current_symptom")
        symptom_explanations = tracker.get_slot("symptom_explanations")
        possible_conditions = tracker.get_slot("possible_conditions")
        
        
        symptom_dicts = tracker.get_slot("symptom_context_list")
        if symptom_dicts:
            symptom_list = [symptom.lower() for symptom in symptom_dicts]
            
        user_symptoms = tracker.get_slot("user_symptoms") or []
        
        user_symptoms.extend(symptom_list)  
        #Debug Print
        # dispatcher.utter_message(text=f"Current user symptms: {symptom_list}")
        
        conditions_ref = db.collection(u'Conditions')
        possible_conditions = []
        
        has_results = False
        
        for i in range(0, len(symptom_list), batch_size):
            batch = symptom_list[i:i + batch_size]
            query = conditions_ref.where(u'Symptoms', u'array_contains_any', symptom_list)
            results = query.stream()
        
            for condition in results:
                has_results = True
                condition_data = condition.to_dict()
                condition_data['name'] = condition.id
                condition_data['score'] = 0
                possible_conditions.append(condition_data)
        if not has_results:
            doc_ref = db.collection("Dialogue").document("noid")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            no_id = random.choice(response_list)
            dispatcher.utter_message(text=no_id)      
            return [FollowupAction("action_listen")]
        # edit if probing now accounts for multiple symptoms
        current_symptom = user_symptoms.pop()
        user_symptoms = []
        
        
        unique_symptoms_kb = []
        for condition in possible_conditions:
            symptoms = condition["Symptoms"]
            for symptom in symptoms:
                # removed: "and symptom not in user_symptoms"
                if symptom not in unique_symptoms_kb:
                    symptom_data = {
                        "name": symptom,
                        "duration": 0,     # Default or placeholder value
                        "intensity": -1     # Default or placeholder value
                    }
                    if symptom_data["name"] == current_symptom:
                        user_symptoms.append(symptom_data)
                        
                    unique_symptoms_kb.append(symptom_data)
        
        # Debug code
        # dispatcher.utter_message(f"Possible conditions:")
        # for condition in possible_conditions:
        #     condition_name = condition['name']
        #     dispatcher.utter_message(f"{condition_name}")
            
        label_ref = db.collection(u'Label')
        unique_symptom_names = [symptom_data["name"] for symptom_data in unique_symptoms_kb]

        
        batch_size = 30
        related_labels = []

        for i in range(0, len(unique_symptom_names), batch_size):
            batch = unique_symptom_names[i:i + batch_size]
            query = label_ref.where(u'Related', u'array_contains_any', batch)
            results = query.stream()

            for label in results:
                label_data = label.to_dict()
                label_data['name'] = label.id
                related_labels.append(label_data)
            
            # Debug
            # if label.id == "Weight":
            #     stmt = label_data["Statement"]
                # dispatcher.utter_message(text=f"{stmt}")
                
            related_labels.append(label_data)
        
        # Debug code
        # dispatcher.utter_message(f"Used Labels:")
        # for label in related_labels:
        #     label_name = label['name']
        #     dispatcher.utter_message(f"{label_name}")
        
        # Reference to the "Symptoms" collection
        symptoms_ref = db.collection(u'Symptoms')

        # Retrieve all documents in the collection
        symptoms_snapshot = symptoms_ref.select([u'Explanation', u'Visual']).stream()

        # Convert the documents into a list of dictionaries
        symptom_explanations = []
        for symptom in symptoms_snapshot:
            symptom_explanation = symptom.to_dict()
            symptom_explanation["name"] = symptom.id
            symptom_explanations.append(symptom_explanation)
            
        # Debug
        # dispatcher.utter_message(text=f"User Symptoms: {user_symptoms}")
        # dispatcher.utter_message(text=f"Symptom Explanations: {symptom_explanations}")
            
                    
        return [SlotSet("possible_conditions", possible_conditions), SlotSet("unique_symptoms_kb", unique_symptoms_kb), SlotSet("symptom_explanations", symptom_explanations),
                SlotSet("related_labels", related_labels), SlotSet("user_symptoms", user_symptoms), SlotSet("current_symptom", current_symptom)]
        
        #dispatcher.utter_message(text=f"Symptoms: {symptom_list}")
        #dispatcher.utter_message(text=f"Conditions:")
        #for condition in conditions:
        #    dispatcher.utter_message(text=f"{condition['name']}")
        
# Display the possible conditions a user has
#CHANGED
class ActionDisplayUserCondition(Action):
    def name(self) -> str:
        return "action_display_user_conditions"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_conditions = tracker.get_slot("user_conditions")
        possible_conditions = tracker.get_slot("possible_conditions")
        symptoms = tracker.get_slot("user_symptoms")
        danger = False
        
        
        if not user_conditions:
            user_conditions = []
        
        for condition in possible_conditions:
            if condition["score"] >= len(condition["Symptoms"])/2:
                user_conditions.append({
                    "name": condition['name'],
                    "score": condition['score'],
                    "threat": condition['Life-Threat'],
                    "Symptoms" : condition['Symptoms'],
                    
                })
        doc_ref = db.collection("Dialogue").document("Fin_imp1")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        fin1 = random.choice(response_list)
 
        doc_ref = db.collection("Dialogue").document("Fin_imp3")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        fin3 = random.choice(response_list)

        dispatcher.utter_message(text="\n"+fin1+"\n") 
        dispatcher.utter_message(text=fin3)
        #dispatcher.utter_message("\nAll Done! Here's my impression from our session.\n") #CHANGED
        #dispatcher.utter_message("Based on your symptoms,") #CHANGED
        
        count = 1  
        if symptoms:
            for symptom in symptoms:
                symptom_data = {
                    "control": "record_symptom",
                    "data": {
                        "symptomName": symptom["name"],
                        "duration": symptom["duration"],
                        "intensity": symptom["intensity"]
                    }
                }
                dispatcher.utter_message(json_message=symptom_data)
                symptom_name = symptom["name"]
                symptom_duration = symptom["duration"]
                symptom_intensity = symptom["intensity"]
                if int(symptom_intensity) >= 0:
                    dispatcher.utter_message(text=f"{count}. {symptom_name}, for {symptom_duration} days, with intensity of {symptom_intensity} out of 10")
                else:
                    dispatcher.utter_message(text=f"{count}. {symptom_name}, for {symptom_duration} days.")
                count+=1
        
        if user_conditions:
            
            # Calculate confidence
            for condition in user_conditions:
                condition_score = condition['score']
                length = len(condition['Symptoms'])
                
                condition_confidence = condition_score/length*100
        
                if condition_confidence >= 100:
                    condition_confidence = 99
                condition['score'] = condition_confidence
                
            # Sort by confidence
            sorted_conditions = sorted(user_conditions, key=lambda x: x["score"], reverse=True)
            count = 1
            
            for count, condition in enumerate(sorted_conditions[:3], start=1):
                condition_name = condition['name']
                condition_confidence = condition['score']
                condition_life_threat = condition['threat']
            
                if not condition_life_threat:
                    condition_data = {
                        "control": "record_condition",
                        "data": {
                            "conditionName": condition_name,
                            "conditionScore": condition_confidence,
                            "lifeThreat": condition_life_threat
                        }
                    }
                    if count <= 1:
                        doc_ref = db.collection("Dialogue").document("match")
                        doc = doc_ref.get()
                        response_list = doc.to_dict().get("terms", [])
                        mat = random.choice(response_list)
                        dispatcher.utter_message(text=mat)
                        #dispatcher.utter_message("\nThese are the conditions that best match them:") #CHANGED
                    dispatcher.utter_message(json_message=condition_data)
                    dispatcher.utter_message(text=f"{count}. {condition_name}")
                    count+=1
            
                else:
                    danger = True
            
            if danger:
                doc_ref = db.collection("Dialogue").document("not_known_danger")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                nknown = random.choice(response_list)
                dispatcher.utter_message(text=nknown)
                #dispatcher.utter_message(text=f"Your combination of symptoms seem peculiar. It might be best to consult with your trusted doctor as soon as you can.") #CHANGED
        
        else:
            doc_ref = db.collection("Dialogue").document("not_known1")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            nknown = random.choice(response_list)
            dispatcher.utter_message(text=nknown)
            #dispatcher.utter_message(text=f"Your combination of symptoms do not seem to lead to anything based on my limited knowledge.")#CHANGED
            doc_ref = db.collection("Dialogue").document("not_known2")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            nknown2 = random.choice(response_list)
            dispatcher.utter_message(text=nknown2)
            #dispatcher.utter_message(text=f"I would advise a visit to your trusted doctor if your symptoms persist, worsen, or are causing discomfort.")#CHANGED
        doc_ref = db.collection("Dialogue").document("complete")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        compl = random.choice(response_list)
        dispatcher.utter_message(text=compl)
        #dispatcher.utter_message(text="The session is complete! A PDF report is now available for your convenience. Please tap the download button on the upper right corner of the app to acquire it.")
        #CHANGED
        dispatcher.utter_message(text=f"This is an important reminder that this is NOT a diagnosis and that I am NOT a doctor. If you're experiencing any symptoms that worry you, please consult your doctor.")
        return [AllSlotsReset()]




# Asks the User if has symptom
#CHANGED
class ActionAskHasSymptom (Action):
    def name(self) -> Text:
        return "action_ask_has_symptom"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        skip = tracker.get_slot("skip")
        if skip:
            return [SlotSet("skip", False)]
        symptoms = tracker.get_slot("unique_symptoms_kb")
        counter = tracker.get_slot("loop_counter")
        related_labels = tracker.get_slot("related_labels") or []
        grouped_symptoms = tracker.get_slot("grouped_symptoms") or []
        grouped_questions = tracker.get_slot("grouped_questions") or []
        user_symptoms = tracker.get_slot("user_symptoms")
        asking_label = tracker.get_slot("asking_label")
        has_label = tracker.get_slot("has_label")
        first_ask = tracker.get_slot("first_ask")
        current_label = tracker.get_slot("label")
        label_name = ""
        label_question = ""
        current_symptom = tracker.get_slot("current_symptom")
        
        
        # Debug
        # dispatcher.utter_message(text=f"Entered AskHasSymptom")
        # dispatcher.utter_message(text=f"User Symptoms: {user_symptoms}")
        # dispatcher.utter_message(text=f"Asking for the first time?: {first_ask}")
        
        
        
        slot = tracker.get_slot("requested_slot")
        if symptoms and not (first_ask and user_symptoms):
            
            # Debug
            # dispatcher.utter_message(text=f"Related Labels: {related_labels}")
            
            if related_labels and not (grouped_questions and grouped_symptoms):
                
                # Debug
                # dispatcher.utter_message(text=f"There are labels part 3")
                
                for label in related_labels:
                    # sympcountname = symptoms[counter]["name"]
                    # dispatcher.utter_message(text=f"Checking: {sympcountname}")
                    if symptoms[counter]["name"] in label['Related']:
                        grouped_symptoms.extend(label['Related'])
                        grouped_questions.extend(label['Questions'])
                        label_name = label['name']
                        current_label = label_name
                        
                        
                        # dispatcher.utter_message(text=f"Found symptom in a label")
                        # debug
                        # label_statement = label.get("Statement", None)
                        # dispatcher.utter_message(text=f"The label statement of {label_name} is {label_statement}")
                        
                        if 'Statement' in label.keys():
                            
                            # Debug
                            # dispatcher.utter_message(text=f"There is a statement for label '{label_name}'")
                            # dispatcher.utter_message(text=f"There is a statement")
                            
                            label_question = label['Statement']
                        # else:
                            
                        #     # Debug
                        #     dispatcher.utter_message(text=f"There is NON statement for label '{label_name}'")
                        
                        related_labels.remove(label)
                        break
                    
                symptom_names = [symptom["name"] for symptom in symptoms]
                filtered_symptoms = [symptom for symptom in grouped_symptoms if symptom in symptom_names]
                filtered_indices = [grouped_symptoms.index(symptom) for symptom in filtered_symptoms]
                filtered_questions = [grouped_questions[i] for i in filtered_indices]
                grouped_symptoms = filtered_symptoms
                grouped_questions = filtered_questions
                if label_name.lower() != "other":
                    asking_label = True
                if label_name.lower() == "other":
                    asking_label = False
            
            # Debug
            # dispatcher.utter_message(text=f"Grouped Symptoms: {grouped_symptoms}")
            # dispatcher.utter_message(text=f"Grouped Questions: {grouped_questions}")
            # dispatcher.utter_message(text=f"Unique Symptoms: {symptoms}")
            
                         
            # if there is a grouped question to be addressed, address it  first 
            # else, continue normally with the current code below
            # dispatcher.utter_message(f"The current label is: {label_name.lower()}")
            if label_name.lower() != "other" and (grouped_questions or grouped_symptoms):
                
                # ===DEBUG CODE====
                # dispatcher.utter_message(f"Label: {label_name.lower()} is not the same as Label: other")
                
                # If currently asking label
                # return asking_label and related_labels to their slots, and update all other slots
                # the flow should return to validate symptom form
                if asking_label:
                    
                    # Debug
                    # dispatcher.utter_message(text=f"Asking Label now...")
                    
                    dispatcher.utter_message(f"{label_question}")
                    return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), 
                            SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("label", current_label)]
                
                # If the user said no to the asked label in validate symptom form
                if not has_label:
                    
                    #Debug 
                    # dispatcher.utter_message(text=f"----------Debugging prints-----------")
                    # dispatcher.utter_message(text=f"Entered not has_label. We should not be here...")
                    # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                    # dispatcher.utter_message(text=f"-------------------------------------")
                    # dispatcher.utter_message(text=f"\nSymptom List: {symptoms}")
                    
                    if symptoms[counter]:
                        # Remove the symptoms with denied labels
                        symptoms = [symptom for symptom in symptoms if symptom["name"] not in grouped_symptoms]
                    
                    return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", []), SlotSet("grouped_symptoms", []),
                            SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom)]
                
                # Debug
                # dispatcher.utter_message(text=f"Not asking for labels anymore")
                
                # user said yes to the label
                # the form should loop and skip to this part until the grouped questions and symptoms are empty
                question = grouped_questions.pop(0)
                asked_symptom = grouped_symptoms.pop(0)
                current_symptom = asked_symptom
                
                # Debugging prints
                # dispatcher.utter_message(text=f"----------Debugging prints-----------")
                # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                # dispatcher.utter_message(text=f"-------------------------------------")
                
                # Ask the question for that symptom
                dispatcher.utter_message(text=f"{question}")
                
                # Return updated slots to validate symptom form
                return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), SlotSet("first_ask", first_ask),
                        SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom), SlotSet("label", current_label), SlotSet("execute", "has_symptom")]
            
            #Debug prints:    
            # dispatcher.utter_message(text=f"\nSymptom List: {symptoms}")
            # dispatcher.utter_message(text=f"----------Debugging prints-----------")
            # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
            # dispatcher.utter_message(text=f"-------------------------------------")
            # dispatcher.utter_message(text=f"The label right now before asking is: {label_name}")
            
            # If the label is "Other"
            if label_name.lower() == "other":
                
                # Debug
                # dispatcher.utter_message(text=f"Label is \"Other\"")
                
                question = grouped_questions.pop(0)
                asked_symptom = grouped_symptoms.pop(0)
                current_symptom = asked_symptom
                
                
                # dispatcher.utter_message(text=f"Questions: {grouped_questions}")
                # dispatcher.utter_message(text=f"Symptoms: {grouped_symptoms}")
                # dispatcher.utter_message(text=f"----------Debugging prints-----------")
                # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                # dispatcher.utter_message(text=f"-------------------------------------")
                
                dispatcher.utter_message(text=f"{question}")
                return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), SlotSet("first_ask", first_ask), 
                        SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom), SlotSet("label", current_label), SlotSet("execute", "has_symptom")]
            doc_ref = db.collection("Dialogue").document("no_label")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            nol = random.choice(response_list)
            dispatcher.utter_message(text=nol)
            #dispatcher.utter_message(text=f"Symptom has no label! Contact administration for this!") #CHANGED

            symptom_name = symptoms[counter]["name"]

            doc_ref = db.collection("Dialogue").document("experience")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            exp = random.choice(response_list)
            fexp=exp.format(symptom_name=symptom_name) if "{symptom_name}" in exp else exp
            dispatcher.utter_message(text=fexp)
            #dispatcher.utter_message(text=f"Have you experienced {symptom_name}") #CHANGED
            return [SlotSet("unique_symptoms_kb", symptoms)]
        
        if symptoms:
            # this happens if: 
            # its the first time asking AND user_symptom contains something
            # Adjust for multiple initial symptoms if implemented
            symptom_explanations = tracker.get_slot("symptom_explanations")
            asked_symptom = user_symptoms[0]["name"]
            symptom_obj = user_symptoms[0]
            user_symptoms.clear()
            
            for label in related_labels:
                    if asked_symptom in label['Related']:
                        label_name = label['name']
                        current_label = label_name
                        break

            explanation = next((symptom["Explanation"] for symptom in symptom_explanations if symptom["name"] == asked_symptom), 
                               None)
            
            current_symptom = asked_symptom
            doc_ref = db.collection("Dialogue").document("confirm")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            con1 = random.choice(response_list)
            fcon1=con1.format(asked_symptom=asked_symptom,explanation=explanation) if "{asked_symptom}" in con1 and "{explanation}" in con1  else con1
            dispatcher.utter_message(text=fcon1)
            #dispatcher.utter_message(text=f"I want to confirm, can your current symptom, {asked_symptom}, be described as {explanation}?") #CHANGED
            
            # Debug
            # dispatcher.utter_message(text=f"Current Symptom: {current_symptom}")
            
            return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("asking_label", asking_label), SlotSet("user_symptoms", user_symptoms),
                    SlotSet("current_symptom", current_symptom), SlotSet("label", current_label), SlotSet("execute", "has_symptom")]
        
        dispatcher.utter_message(text="FAILURE")
        return []
#CHANGED    
class ActionAskDay(Action):
    def name(self) -> Text:
        return "action_ask_day"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        # Debug
        # dispatcher.utter_message(text=f"Entered ASK DURATION")
        
        # Execute action
        doc_ref = db.collection("Dialogue").document("Days")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        day = random.choice(response_list)
        dispatcher.utter_message(text=day)
        #dispatcher.utter_message(text=f"Including today, for how many days have you been experiencing this symptom?") #CHANGED
        
        # Debug
        # dispatcher.utter_message(text=f"Exiting ASK DURATION")
        
        return[]
#CHANGED    
class ActionAskIntensity(Action):
    def name(self) -> Text:
        return "action_ask_intensity"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        # Debug
        # dispatcher.utter_message(text=f"Entered ASK INTENSITY")
        
        # Execute action
        doc_ref = db.collection("Dialogue").document("Intense")
        doc = doc_ref.get()
        response_list = doc.to_dict().get("terms", [])
        intense = random.choice(response_list)
        dispatcher.utter_message(text=intense)
        #dispatcher.utter_message(text=f"On a scale of 0-10 (0 is no pain), how intense is the pain?") #CHANGED
        
        # Debug
        # dispatcher.utter_message(text=f"Exiting ASK INTENSITY")
        
        return[]
    
class ValidateSymptomForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_symptom_form"
    
    def extract_has_symptom(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
    
        execute = tracker.get_slot("execute")
        if execute == "has_symptom":        
            intent = tracker.get_intent_of_latest_message()
            if intent == "affirm":
                has_symptom = True
            elif intent == "deny":
                has_symptom = False
            else:
                has_symptom = intent    
            return {"has_symptom": has_symptom}
    
    #CHANGED
    def validate_has_symptom(
        self,
        slot_value: any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        current_counter = tracker.get_slot("loop_counter")
        conditions = tracker.get_slot("possible_conditions")
        
        current_symptom = tracker.get_slot("current_symptom")
        symptoms = tracker.get_slot("unique_symptoms_kb")
        user_symptoms = tracker.get_slot("user_symptoms")
        
        diagnosed_conditions = tracker.get_slot("diagnosed_condition")
        
        grouped_symptoms = tracker.get_slot("grouped_symptoms")
        asking_duration = tracker.get_slot("asking_duration")
        asking_intensity = tracker.get_slot("asking_intensity")
        asking_label = tracker.get_slot("asking_label")
        has_label = tracker.get_slot("has_label")
        label = tracker.get_slot("label")
        first_ask = tracker.get_slot("first_ask")
        
        
        if isinstance(slot_value, str):
            if slot_value == "ask_symptom_question":
                symptom_explanations = tracker.get_slot("symptom_explanations")
                symp_explanation = next((explanation for explanation in symptom_explanations if explanation["name"] == current_symptom))
                explanation = symp_explanation["Explanation"]
                visual = None
                if symp_explanation["Visual"]:
                    visual = symp_explanation["Visual"]
                
                if visual:
                    doc_ref = db.collection("Dialogue").document("image")
                    doc = doc_ref.get()
                    response_list = doc.to_dict().get("terms", [])
                    ima = random.choice(response_list)
                    dispatcher.utter_message(
                        text=ima,
                        image=visual
                    )
                    #dispatcher.utter_message(
                    #    text="Here's an image for your reference:",
                    #    image=visual
                    #) #CHANGED
                doc_ref = db.collection("Dialogue").document("when_ex1")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                wex = random.choice(response_list)
                fwex1=wex.format(current_symptom=current_symptom,explanation=explanation) if "{current_symptom}" in wex and "{explanation}" in wex else wex
                dispatcher.utter_message(text=fwex1)
                #dispatcher.utter_message(text=f"When experiencing {current_symptom}, it typically means {explanation}") #CHANGED
                doc_ref = db.collection("Dialogue").document("when_ex2")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                wex2 = random.choice(response_list)
                dispatcher.utter_message(text=wex2)
                #dispatcher.utter_message(text=f"Would you say you're experiencing this symptom?")#CHANGED
                return {"has_symptom": None, "skip": True, "execute": None}
            else:
                doc_ref = db.collection("Dialogue").document("unsure")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                unsure = random.choice(response_list)
                dispatcher.utter_message(text=unsure)
                #dispatcher.utter_message(text=f"That went over my head—could you try rephrasing? I’m here to explain the symptoms as well, so feel free to ask about that!")#CHANGED
            return {"has_symptom": None, "skip": True, "execute": None}
        
        # dispatcher.utter_message(text=f"Entered validate symptom")
        
        # Initialize arrays
        if not user_symptoms:
            user_symptoms = []
        if not diagnosed_conditions:
            diagnosed_conditions = []

        has_been_diagnosed = False
        diagnosed = []
        
        # Will be marked true if 
        # asking_label was set to true in AskHasSymptom
        if asking_label and not first_ask:
            
            # Debug
            # dispatcher.utter_message(text=f"Asking Label in validate symptom form")
            
            # If user said no,
            # Cut out symptoms from the current label (which are in the current grouped symptoms slot)
            if not slot_value:
                
                # Debug
                # dispatcher.utter_message(text=f"\nAccording to your response, you have not experienced anything related to this label")
                # dispatcher.utter_message(text=f"\nRemoving the grouped symptoms from your possible symptom lists...")
                
                symptoms = [symptom for symptom in symptoms if symptom["name"] not in grouped_symptoms]
                
                if symptoms:
                    return {"grouped_questions": [], "grouped_symptoms": [], "has_label" : slot_value, "possible_conditions" : conditions, "has_symptom" : None, "day": None, 
                            "loop_counter" : current_counter, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "unique_symptoms_kb": symptoms, "execute": None}
             
            # If there are remaining symptoms, 
            # return the user's answer (slot value), update asking_label and all other slots
            # has_symptom slot must be set to none so the form continues to loop.
            # this returns to AskHasSymptom and skips if not has_label part
            if symptoms:
                return {"has_label" : slot_value, "asking_label" : False, "possible_conditions" : conditions, "has_symptom" : None, "day": None, "execute": None,
                        "loop_counter" : current_counter, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "unique_symptoms_kb": symptoms}
        
        #Debug Code    
        # dispatcher.utter_message(text=f"Current Counter and Symptom: {current_counter} and {current_symptom}")           
        # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
        
        # If the user says yes to symptom question
        
        # Debug
        # dispatcher.utter_message(text=f"The current symptom is: {current_symptom}")
        
        if slot_value:
            
            # dispatcher.utter_message(text=f"Not asking label, said yes to symptom")
            
            #Debug Code
            #dispatcher.utter_message(text=f"I am inserting {current_symptom} to the user symptoms")
            
            # if label == pain, ask intensity
            # else, no ask
            
            if label.lower() == "pain" or label.lower() == "sex":
                
                # Debug
                # dispatcher.utter_message(text=f"Label \"pain\" IS same as label \"{label}\"")
            
                asking_intensity = True
                asking_duration = True
            elif label.lower() == "weight" or label.lower() == "infertility":
                
                asking_intensity = False
                asking_duration = False

            else:
                # Ask duration since user said yes
                asking_duration = True
                asking_intensity = False
            
            # Append the current symptom being asked to user's symptoms
            # dispatcher.utter_message(text=f"Here now! The current symptom is: {current_symptom}")
            # dispatcher.utter_message(text=f"The label is: {label}")
            matching_symptom = next((symptom for symptom in symptoms if symptom["name"] == current_symptom), None)
            
            # debug
            # dispatcher.utter_message(text=f"Storing symptom to user_symptoms: {matching_symptom}...")
            
            user_symptoms.append(matching_symptom)
            
            # debug
            # dispatcher.utter_message(text=f"current list of user symptoms: {user_symptoms}")
            
            if conditions:
                for condition in conditions:

                    condition_score = condition["score"]
                    condition_name = condition["name"]

                    if current_symptom in condition["Symptoms"]:
                        
                        # Debug                        
                        # dispatcher.utter_message(text=f"{current_symptom} is in {condition_name} with a score of {condition_score}")
                        
                        if current_symptom in condition["Key_symp"]:
                            condition["score"] += 2
                        else:
                            condition["score"] += 1
                    
                    # Debug
                    # condition_score = condition["score"]
                    # length = len(condition["Symptoms"])
                    # dispatcher.utter_message(text=f"The current score of {condition_name} is {condition_score}/{length}")

                    # If a condition has a high enough score, and it's not an already diagnosed condition
                    # Display to the user progress so far.
                    if condition["score"] >= len(condition["Symptoms"])/2:
                        diagnosed_conditions_names = [cond['name'] for cond in diagnosed_conditions]
                        if condition["name"] not in diagnosed_conditions_names:
                            has_been_diagnosed = True
                            diagnosed.append(condition)
                            diagnosed_conditions.append(condition)
                    
                    #Debug Prints
                    # dispatcher.utter_message(text=f"\n\nCondition: {condition['name']}, Score: {condition['score']}\n")
                    # dispatcher.utter_message(text=f"{diagnosed}\n\n")
            else: 
                doc_ref = db.collection("Dialogue").document("no_symp_match")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                no_symp_m = random.choice(response_list)
                dispatcher.utter_message(text=no_symp_m)
                #dispatcher.utter_message(text="Currently, no conditions match your symptoms.") #CHANGED
        
        if not slot_value and first_ask:
            # Assuming one symptom only
            user_symptoms.clear()
        
        #Debug Code
        # dispatcher.utter_message(text=f"----------Debugging prints-----------")
        # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}\n\nUser symptoms: {user_symptoms}")
        # dispatcher.utter_message(text=f"-------------------------------------")
        
        # Display progress so far if there's a new diagnosis.
        if has_been_diagnosed:
            if len(diagnosed) > 1 or not diagnosed[0]["Life-Threat"]:
                doc_ref = db.collection("Dialogue").document("symp_sofar")
                doc = doc_ref.get()
                response_list = doc.to_dict().get("terms", [])
                sympsofar = random.choice(response_list)
                dispatcher.utter_message(text=sympsofar)
                #dispatcher.utter_message(text="Your symptoms so far are:") #CHANGED
                count = 1
                for symptom in user_symptoms:
                    symptom_name = symptom["name"]
                    dispatcher.utter_message(text=f"{count}. {symptom_name}")
                    count += 1
                count = 1
                
                for condition in diagnosed:
                    condition_name = condition['name']
                    
                    # get explanation
                    if isinstance(condition["Explanation"], list):
                        random_explanation = random.choice(condition["Explanation"])
                    elif isinstance(condition["Explanation"], str):
                        random_explanation = condition["Explanation"]
                    else:
                        random_explanation = "No explanation available."
                    
                    if count <= 1:
                        doc_ref = db.collection("Dialogue").document("curr_match")
                        doc = doc_ref.get()
                        response_list = doc.to_dict().get("terms", [])
                        curr_match = random.choice(response_list)
                        curr_match= "\n"+curr_match
                        dispatcher.utter_message(text=curr_match)
                        #dispatcher.utter_message(text="\nYour current symptoms match the following conditions:") #CHANGED
                    
                    if not condition["Life-Threat"]:
                        dispatcher.utter_message(text=f"{count}. Name: {condition_name}")
                    
                    # Display explanations and references
                    dispatcher.utter_message(text=random_explanation)
                    
                    references = "\n".join(condition["References"])
                    dispatcher.utter_message(text=f"Reference/s:\n{references}")
                    
                    count+=1
                has_been_diagnosed = False
        
        # remove the current symptom from the symptom list to update the list and move on to the next symptom
        # dispatcher.utter_message(text=f"The current symptom is: {current_symptom}")
        # dispatcher.utter_message(text=f"Symptoms now: {symptoms}")
        symptoms = [symptom for symptom in symptoms if symptom["name"] != current_symptom]
        # dispatcher.utter_message(text=f"Symptoms after removing: {symptoms}")
        
        
        #Debug Prints
        # unique_symptoms_len = len(symptoms)
        # dispatcher.utter_message(text=f"\n\nSymptom Length: {unique_symptoms_len}\nCounter: {current_counter}")
        # dispatcher.utter_message(text=f"User Symptoms: {user_symptoms}")
        # dispatcher.utter_message(text=f"Exiting Validate Has Symptom")
        
        # Move to next slot, update everything
        if slot_value:
            # If not asking for intensity, set proceed to askday, set intensity to a value
            
            if not asking_intensity:
                
                # Debug
                # dispatcher.utter_message(text=f"Skipping ask for intensity")
                if not asking_duration:
                    
                    if symptoms:    
                        return {"possible_conditions" : conditions, "has_symptom" : None, "day": "-1", "intensity": 1 ,"loop_counter": current_counter, "first_ask": False,
                                "unique_symptoms_kb": symptoms, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "execute": None}
                    
                    return {"possible_conditions" : conditions, "has_symptom" : slot_value, "day": 0, "intensity": 0 , "loop_counter": current_counter, "unique_symptoms_kb": symptoms,
                            "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "first_ask": True, "execute": None}
                    
                return {"possible_conditions" : conditions, "has_symptom" : slot_value, "day": None, "intensity": 1 ,"loop_counter": current_counter, "first_ask": False,
                        "unique_symptoms_kb": symptoms, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "execute": None}
            
            return {"possible_conditions" : conditions, "has_symptom" : slot_value, "day": None, "intensity": None ,"loop_counter": current_counter, "unique_symptoms_kb": symptoms,
                    "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "asking_intensity": asking_intensity,  "first_ask": False, "execute": None}
        
        # says no to symptom, don't ask day
        if symptoms:
            return {"possible_conditions" : conditions, "has_symptom" : None, "loop_counter": current_counter, "unique_symptoms_kb": symptoms,
                    "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "first_ask": False, "execute": None}
        
        return {"possible_conditions" : conditions, "has_symptom" : slot_value, "day": 0, "intensity": 0 , "loop_counter": current_counter, "unique_symptoms_kb": symptoms,
                "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "first_ask": True, "execute": None}

    def validate_day(
        self,
        slot_value: any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        asking_intensity = tracker.get_slot("asking_intensity")
        intensity = tracker.get_slot("intensity")
        symptoms = tracker.get_slot("unique_symptoms_kb")
        user_symptoms = tracker.get_slot("user_symptoms")
        current_symptom = tracker.get_slot("current_symptom")
        has_symptom = tracker.get_slot("has_symptom")
        intent = tracker.get_intent_of_latest_message()

        # Debug
        # dispatcher.utter_message(text=f"Entered VALIDATE DURATION")
        # dispatcher.utter_message(text=f"User answered: {slot_value}")
        # dispatcher.utter_message(text=f"Ask for intensity?: {asking_intensity}")
        # dispatcher.utter_message(text=f"Intensity: {intensity}")
        # dispatcher.utter_message(text=f"Exiting VALIDATE DURATION")
        
        if intent == "not_known":    
            for symptom in user_symptoms:
                if symptom["name"] == current_symptom:
                    
                    # Update the 'duration' key for the matching symptom
                    symptom["duration"] = "-1"
                    break
            
            if asking_intensity:
                return {"day": slot_value, "asking_intensity": asking_intensity, 
                        "asking_duration": False, "user_symptoms": user_symptoms}
            if symptoms:
                # if not empty,
                # set has_symptom to None,
                # allowing the form to continue back to asking symptoms
                return {"has_symptom": None, "day": slot_value, "asking_intensity": asking_intensity, 
                        "asking_duration": False, "user_symptoms": user_symptoms}
            return {"has_symptom": True, "day": slot_value, "asking_intensity": asking_intensity, 
            "asking_duration": False, "user_symptoms": user_symptoms}
        
        # TODO: set the current_symptom duration to the user input
        # Code here
        if intent == "say_days" or intent == "say_age" or intent == "provide_intensity":
            for symptom in user_symptoms:
                if symptom["name"] == current_symptom:
                    
                    # Update the 'duration' key for the matching symptom
                    symptom["duration"] = slot_value 
                    break
            
            # if asking intensity, set a value for day; 
            # allowing the system to move to the next slot
            if asking_intensity:
                return {"day": slot_value, "asking_intensity": asking_intensity, 
                        "asking_duration": False, "user_symptoms": user_symptoms}
            
            # if not asking for intensity, 
            # check if symptom list is empty
            if symptoms:
                # if not empty,
                # set has_symptom to None,
                # allowing the form to continue back to asking symptoms
                return {"has_symptom": None, "day": slot_value, "asking_intensity": asking_intensity, 
                        "asking_duration": False, "user_symptoms": user_symptoms}
            # if empty,
            # set has_symptom a value,
            # stopping the form loop without asking for intensity
            return {"has_symptom": True, "day": slot_value, "asking_intensity": asking_intensity, 
                    "asking_duration": False, "user_symptoms": user_symptoms}
        else:
            doc_ref = db.collection("Dialogue").document("unsure_day")
            doc = doc_ref.get()
            response_list = doc.to_dict().get("terms", [])
            unsure = random.choice(response_list)
            dispatcher.utter_message(text=unsure)
            return {"day": None, "skip": True, "execute": None}
    
    def validate_intensity(
        self,
        slot_value: any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        symptoms = tracker.get_slot("unique_symptoms_kb")
        user_symptoms = tracker.get_slot("user_symptoms")
        current_symptom = tracker.get_slot("current_symptom")
        label = tracker.get_slot("label")
        
        # Debug
        # dispatcher.utter_message(text=f"Entered VALIDATE INTENSITY")
        # dispatcher.utter_message(text=f"User answered: {slot_value}")
        # dispatcher.utter_message(text=f"Exiting VALIDATE INTENSITY")
        # dispatcher.utter_message(text=f"Updated {current_symptom}")
        
        # TODO: set the current_symptom duration to the user input
        # Code here
        for symptom in user_symptoms:
            if symptom["name"] == current_symptom:
                
                # debug
                # dispatcher.utter_message(text=f"from {symptom}")
                
                # Update the 'duration' key for the matching symptom
                symptom["intensity"] = slot_value
                
                # debug
                # dispatcher.utter_message(text=f"to {symptom}")
                
                break
        
        # if user has more symptoms,
        # set has_symptom to None, 
        # allowing the form to loop from the start.
        if symptoms:
            
            # Debug
            # dispatcher.utter_message(text=f"User still has symptoms, continuing back to Ask Symptoms")
            
            return {"has_symptom": None, "intensity": slot_value, "asking_intensity": False, "user_symptoms": user_symptoms}
        
        # if no more symptoms,
        # set a value to has_symptom, ending the active loop
        return {"has_symptom": True, "intensity": slot_value, "asking_intensity": False, "user_symptoms": user_symptoms}
    
# Asks the User if has symptom
class ActionTestForm (Action):
    def name(self) -> Text:
        return "action_test"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        has = tracker.get_slot("has_symptom")
        
        cond = tracker.get_slot("possible_conditions")
        
        dispatcher.utter_message("This is the condition structure:")
        dispatcher.utter_message(cond)
        
        return []

class ActionAskNeedAssistance(Action): #CHANGED
    def name(self) -> Text:
        return "action_ask_need_assistance"
    
    #def run(
    #    self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    #) -> List[EventType]:
    #    dispatcher.utter_message(
    #        response="utter_further_assist"
    #    ) #CHANGED
    def run(self, dispatcher: CollectingDispatcher, tracker, domain):

        #Fetch responses from Firestore
        doc_ref = db.collection("Dialogue").document("futher_assist")
        doc = doc_ref.get()
        if doc.exists:
            response_list = doc.to_dict().get("terms", [])
            if response_list:
                chosen_response = random.choice(response_list)  # Pick a random response
                dispatcher.utter_message(text=chosen_response)
            else:
                dispatcher.utter_message(text="Do you require further assistance?")
        else:
            dispatcher.utter_message(text="Do you require further assistance?")

        return []

class ActionSubmitRestart (Action):
    def name(self) -> Text:
        return "action_submit_restart"
    def get_random_response(self, response_key: str) -> str:
        
        doc_ref = db.collection("Dialogue").document(response_key)
        doc = doc_ref.get()

        if doc.exists:
            terms = doc.to_dict().get("terms", [])
            if terms:
                return random.choice(terms)

        # Fallback response if Firestore document or terms are missing
        return "Sorry, I couldn't find a suitable response."

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        restart = tracker.get_slot("need_assistance")
        response_key = "feelings" if restart else "future"
        message = self.get_random_response(response_key)
        dispatcher.utter_message(text=message)
        
        return [AllSlotsReset()]
    
   # def run(
    #    self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    #) -> List[EventType]:
    #    restart = tracker.get_slot("need_assistance")
     #   if (restart):
     #       dispatcher.utter_message(
      #          action="action_feelings"
       #     ) 
            #Action_Feelings(Action)

        #if (restart):
        #    dispatcher.utter_message(
        #        response="utter_feelings"
        #    ) #CHANGED

     #   else:
      #     dispatcher.utter_message(
       #         action="action_ask_need_assistance"
        #    ) #CHANGED
            #ActionAskNeedAssistance(Action)
        #else:
        #    dispatcher.utter_message(
        #        response="utter_future_assist"
        #    ) #CHANGED

       # return [AllSlotsReset()]