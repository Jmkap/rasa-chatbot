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

# UTTER SYMPTOM
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
            dispatcher.utter_message(text=f"Your symptom is {symptom}. Let me see how I can help!")
            new_symptom_list.append({"symptom": symptom, "context": "NA"})
            # Create a new session
            create_new = {
                "control": "create_new_session"
            }
            
            dispatcher.utter_message(json_message=create_new)
            return [SlotSet("symptom", None), SlotSet("context", None), SlotSet("symptom_context_list", new_symptom_list)]
        
        dispatcher.utter_message(text=f"Your symptom is: {symptom}, specifically with {context}. Let me see how I can help!")
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
            dispatcher.utter_message(text=f"Just a friendly reminder, {username}☝️. I am designed to provide impressions and insights primarily for people who have not yet entered menopause. 🙏")
            dispatcher.utter_message(text=f"If your concerns are still present, I would advise seeking a medical professional directly and immediately. 🩺🙂")

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
class ActionSubmitUserInfo(Action):

    def name(self) -> Text:
        return "action_submit_user_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        age = tracker.get_slot("age")
        name = tracker.get_slot("PERSON")
        isMenopause = tracker.get_slot("isMenopause")
        
        if isMenopause:
            dispatcher.utter_message(text=f"Also, {name}👋, I want you to know that I am designed to provide impressions and insights primarily for people who have not yet entered menopause. 🤔")
        
        dispatcher.utter_message(text=f"Nice to meet you, {name}")
        
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
            dispatcher.utter_message(text="Sorry, it seems that I have not stored your name")
        if not age:
            dispatcher.utter_message(text="Sorry, it seems that I do not have your age")
        
        if age and name:
            dispatcher.utter_message(text=f"User: {name}\nAge: {age}\nNew User?: {new}")
        else:
            dispatcher.utter_message(text=f"Missing Age or Name\nNew User?: {new}.")
            
        dispatcher.utter_message(text=f"Asking If New?: {asking}")
        
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
        # Use a service account.
        
        path_cwd = os.getcwd()
        cred_path = os.path.join(path_cwd, "service account\knowledgebase.json")
        
        if not _apps:
            cred = credentials.Certificate(cred_path)
            initialize_app(cred)
        
        db = firestore.client()
        
        symptom_dicts = tracker.get_slot("symptom_context_list")
        if symptom_dicts:
            symptom_list = [symptom['symptom'] for symptom in symptom_dicts]
            
        user_symptoms = tracker.get_slot("user_symptoms") or []
        
        user_symptoms.extend(symptom_list)  
        #Debug Print
        # dispatcher.utter_message(text=f"Current user symptoms: {symptom_list}")
        
        conditions_ref = db.collection(u'Conditions')
        
        
        for i in range(0, len(symptom_list), batch_size):
            batch = symptom_list[i:i + batch_size]
            query = conditions_ref.where(u'Symptoms', u'array_contains_any', symptom_list)
            results = query.stream()
        
            possible_conditions = []
            for condition in results:
                condition_data = condition.to_dict()
                condition_data['name'] = condition.id
                condition_data['score'] = 0
                possible_conditions.append(condition_data)
                
        
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
        
        dispatcher.utter_message("\nAll Done! Here's my impression from our session.\n")
        dispatcher.utter_message("Based on your symptoms,")
        
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
                        dispatcher.utter_message("\nThese are the conditions that best match them:")
                    dispatcher.utter_message(json_message=condition_data)
                    dispatcher.utter_message(text=f"{count}. {condition_name}")
                    count+=1
            
                else:
                    danger = True
            
            if danger:
                dispatcher.utter_message(text=f"Your combination of symptoms seem peculiar. It might be best to consult with your trusted doctor as soon as you can.")
        
        else:
            dispatcher.utter_message(text=f"Your combination of symptoms do not seem to lead to anything based on my limited knowledge.")
            dispatcher.utter_message(text=f"I would advise a visit to your trusted doctor if your symptoms persist, worsen, or are causing discomfort.")
        
        dispatcher.utter_message(text="The session is complete! A PDF report is now available for your convenience. Please tap the download button on the upper right corner of the app to acquire it.")
        
        return [AllSlotsReset()]




# Asks the User if has symptom
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
            
            dispatcher.utter_message(text=f"Symptom has no label! Contact administration for this!")
            symptom_name = symptoms[counter]["name"]
            dispatcher.utter_message(text=f"Have you experienced {symptom_name}")
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
            
            dispatcher.utter_message(text=f"I want to confirm, can your current symptom, {asked_symptom}, be described as {explanation}?")
            
            # Debug
            # dispatcher.utter_message(text=f"Current Symptom: {current_symptom}")
            
            return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("asking_label", asking_label), SlotSet("user_symptoms", user_symptoms),
                    SlotSet("current_symptom", current_symptom), SlotSet("label", current_label), SlotSet("execute", "has_symptom")]
        
        dispatcher.utter_message(text="FAILURE")
        return []
    
class ActionAskDay(Action):
    def name(self) -> Text:
        return "action_ask_day"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        # Debug
        # dispatcher.utter_message(text=f"Entered ASK DURATION")
        
        # Execute action
        dispatcher.utter_message(text=f"Including today, for how many days have you been experiencing this symptom?")
        
        # Debug
        # dispatcher.utter_message(text=f"Exiting ASK DURATION")
        
        return[]
    
class ActionAskIntensity(Action):
    def name(self) -> Text:
        return "action_ask_intensity"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        
        # Debug
        # dispatcher.utter_message(text=f"Entered ASK INTENSITY")
        
        # Execute action
        dispatcher.utter_message(text=f"On a scale of 0-10 (0 is no pain), how intense is the pain?")
        
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
                    dispatcher.utter_message(
                        text="Here's an image for your reference:",
                        image=visual
                    )
                dispatcher.utter_message(text=f"When experiencing {current_symptom}, it typically means {explanation}")
                dispatcher.utter_message(text=f"Would you say you're experiencing this symptom?")
                return {"has_symptom": None, "skip": True, "execute": None}
            else:
                dispatcher.utter_message(text=f"That went over my head—could you try rephrasing? I’m here to explain the symptoms as well, so feel free to ask about that!")
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
            else:
                
                # Debug
                # dispatcher.utter_message(text=f"Label \"pain\" is NOT same as label \"{label}\"")
                
                asking_intensity = False
    
            # Ask duration since user said yes
            asking_duration = True
            
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
                dispatcher.utter_message(text="Currently, no conditions match your symptoms.")
        
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
                dispatcher.utter_message(text="Your symptoms so far are:")
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
                        dispatcher.utter_message(text="\nYour current symptoms match the following conditions:")
                    
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
                
                return {"possible_conditions" : conditions, "has_symptom" : slot_value, "day": None, "intensity": 1 ,"loop_counter": current_counter, "first_ask": False,
                        "unique_symptoms_kb": symptoms, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration, "execute": None}
            # if asking for intensity, proceed as normal
            
            # Debug
            # dispatcher.utter_message(text=f"Proceeding to ask for intensity")
            
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
        
        
        
        # Debug
        # dispatcher.utter_message(text=f"Entered VALIDATE DURATION")
        # dispatcher.utter_message(text=f"User answered: {slot_value}")
        # dispatcher.utter_message(text=f"Ask for intensity?: {asking_intensity}")
        # dispatcher.utter_message(text=f"Intensity: {intensity}")
        # dispatcher.utter_message(text=f"Exiting VALIDATE DURATION")
        
        # TODO: set the current_symptom duration to the user input
        # Code here
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

class ActionAskNeedAssistance(Action):
    def name(self) -> Text:
        return "action_ask_need_assistance"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        dispatcher.utter_message(
            response="utter_further_assist"
        )

class ActionSubmitRestart (Action):
    def name(self) -> Text:
        return "action_submit_restart"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        restart = tracker.get_slot("need_assistance")
        
        if (restart):
            dispatcher.utter_message(
                response="utter_feelings"
            )
        else:
            dispatcher.utter_message(
                response="utter_future_assist"
            )

        return [AllSlotsReset()]