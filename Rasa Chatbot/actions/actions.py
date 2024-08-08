# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import firebase_admin
from firebase_admin import firestore, credentials, _apps, initialize_app
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType
from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.types import DomainDict

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
            return [SlotSet("symptom", None), SlotSet("context", None), SlotSet("symptom_context_list", new_symptom_list)]
        
        dispatcher.utter_message(text=f"Your symptom is: {symptom}, specifically with {context}. Let me see how I can help!")
        new_symptom_list.append({"symptom": symptom, "context": context})
        
        
        return [SlotSet("symptom", None), SlotSet("context", None), SlotSet("symptom_context_list", new_symptom_list)]

# UTTER SYMPTOM LIST
class ActionRepeatSymptom(Action):

    def name(self) -> Text:
        return "action_repeat_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        symptom_list = tracker.get_slot("symptom_context_list")

        if not symptom_list:
            dispatcher.utter_message(text="Sorry, it seems that I do not have any information stored about your symptoms")
            dispatcher.utter_message(text="What are you experiencing as of the moment?")
            return []
        
        # change to make it so it rereads all symptoms stored   
        dispatcher.utter_message(text="Your symptoms include:")
        for index, entry in enumerate(symptom_list, start=1):
            symptom = entry.get("symptom")
            context = entry.get("context")
            dispatcher.utter_message(text=f"{index}.) Your symptom is: {symptom}, specifically with {context}.")
            
        dispatcher.utter_message(text="End of symptom list")
        
        return []

# SET THE USER'S AGE TO A SLOT
class ActionSetUserInfo(Action):

    def name(self) -> Text:
        return "action_submit_user_form"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        age = tracker.get_slot("age")
        name = tracker.get_slot("PERSON")
        
        dispatcher.utter_message(text=f"Nice to meet you, {name} ")
        
        return [SlotSet("age", age), SlotSet("PERSON", name), SlotSet("is_new_user", False)]

# FLAG IF CHATBOT LISTENING FOR AFFIRMATION
class ActionTriggerListenNew(Action):

    def name(self) -> Text:
        return "action_trigger_listen_new"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        listen = tracker.get_slot("asked_new")
        
        listen = not listen
        
        return [SlotSet("asked_new", listen)]
        

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
        
        # Use a service account.
        if not _apps:
            cred = credentials.Certificate("C:/Users/Jmkap/Desktop/ChatBot Development/Rasa Chatbot/service account/knowledgebase.json")
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
        
        query = conditions_ref.where(u'Symptoms', u'array_contains_any', symptom_list)
        results = query.stream()
        
        possible_conditions = []
        unique_symptoms_kb = []
        for condition in results:
            condition_data = condition.to_dict()
            condition_data['name'] = condition.id
            condition_data['score'] = 0
            possible_conditions.append(condition_data)
            
        for condition in possible_conditions:
            symptoms = condition["Symptoms"]
            for symptom in symptoms:
                if symptom not in unique_symptoms_kb and symptom not in user_symptoms:
                    unique_symptoms_kb.append(symptom)
        
        # Debug code
        # dispatcher.utter_message(f"Possible conditions:")
        # for condition in possible_conditions:
        #     condition_name = condition['name']
        #     dispatcher.utter_message(f"{condition_name}")
            
        label_ref = db.collection(u'Label')
        query = label_ref.where(u'Related', u'array_contains_any', unique_symptoms_kb)
        results = query.stream()

        related_labels = []

        for label in results:
            label_data = label.to_dict()
            label_data['name'] = label.id
            related_labels.append(label_data)
        
        # Debug code
        # dispatcher.utter_message(f"Used Labels:")
        # for label in related_labels:
        #     label_name = label['name']
        #     dispatcher.utter_message(f"{label_name}")
            
                    
        return [SlotSet("possible_conditions", possible_conditions), SlotSet("unique_symptoms_kb", unique_symptoms_kb), SlotSet("related_labels", related_labels), SlotSet("user_symptoms", user_symptoms)]
        
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
        
        if not user_conditions:
            user_conditions = []
        
        for condition in possible_conditions:
            if condition["score"] >= len(condition["Symptoms"])/2:
                user_conditions.append({
                    "name": condition['name'],
                    "score": condition['score'],
                    "threat": condition['Life-Threat'],
                    "symptom_length" : condition['Symptoms']
                })
        
        if user_conditions:
            sorted_conditions = sorted(user_conditions, key=lambda x: x["score"], reverse=True)
            dispatcher.utter_message("\nFinished impression phase.\n")
            dispatcher.utter_message("To summarize:")
            dispatcher.utter_message("Based on your symptoms,")
            count = 1
            for symptom in symptoms:
                dispatcher.utter_message(text=f"{count}. {symptom}")
                count+=1
            dispatcher.utter_message("\nThese are the conditions that best match them:")
            count = 1
            for condition in sorted_conditions:
                condition_name = condition['name']
                condition_score = condition['score']
                condition_life_threat = condition['threat']
                length = len(condition['symptom_length'])
                condition_confidence = condition_score/length*100
                dispatcher.utter_message(text=f"{count}. {condition_name}, \nConfidence: {condition_confidence}%, \nLife-Threatening: {condition_life_threat}")
                count+=1
                if count > 3:
                    break
        else:
            dispatcher.utter_message(text=f"I don't seem to notice any implied conditions based on your symptoms.")
            dispatcher.utter_message(text=f"If something still continues to worry you, it might be better to consult with a medical professional.")
        return [SlotSet("unique_symptoms_kb", None), SlotSet("possible_conditions", None)]


                
            
# Asks the User if has symptom
class ActionAskHasSymptom (Action):
    def name(self) -> Text:
        return "action_ask_has_symptom"
    
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        symptoms = tracker.get_slot("unique_symptoms_kb")
        counter = tracker.get_slot("loop_counter")
        related_labels = tracker.get_slot("related_labels") or []
        grouped_symptoms = tracker.get_slot("grouped_symptoms") or []
        grouped_questions = tracker.get_slot("grouped_questions") or []
        asking_label = tracker.get_slot("asking_label")
        has_label = tracker.get_slot("has_label")
        label_name = ""
        current_symptom = tracker.get_slot("current_symptom")
        
        if symptoms:
            if related_labels and not grouped_questions:
                for label in related_labels:
                    if symptoms[counter] in label['Related']:
                        grouped_symptoms.extend(label['Related'])
                        grouped_questions.extend(label['Questions'])
                        label_name = label['name']
                        related_labels.remove(label)
                        break
                filtered_symptoms = [symptom for symptom in grouped_symptoms if symptom in symptoms]
                filtered_indices = [grouped_symptoms.index(symptom) for symptom in filtered_symptoms]
                filtered_questions = [grouped_questions[i] for i in filtered_indices]
                grouped_symptoms = filtered_symptoms
                grouped_questions = filtered_questions
                asking_label = True
                         
            # if there is a grouped question to be addressed, address it  first 
            # else, continue normally with the current code below
            dispatcher.utter_message(f"The current label is: {label_name.lower()}")
            if label_name.lower() != "other" and (grouped_questions or grouped_symptoms):
                dispatcher.utter_message(f"Label: {label_name.lower()} is not the same as Label: other")
                if asking_label:
                    dispatcher.utter_message(f"Excluding the previous symptoms mentioned, are you experiencing symptoms related to {label_name}?")
                    return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label)]
                if not has_label:
                    #Debug 
                    dispatcher.utter_message(text=f"----------Debugging prints-----------")
                    dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                    dispatcher.utter_message(text=f"-------------------------------------")
                    # dispatcher.utter_message(text=f"\nSymptom List: {symptoms}")
                    # dispatcher.utter_message(text=f"\nAccording to your response, you have not experienced anything related to {label_name}")
                    # dispatcher.utter_message(text=f"\nRemoving the grouped symptoms from your possible symptom lists...")
                    
                    if counter < len(symptoms):
                        if symptoms[counter]:
                            dispatcher.utter_message(text=f"Have you experienced {symptoms[counter]}")
                            current_symptom = symptoms[counter]
                            symptoms.remove(symptoms[counter])
                    return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", []), SlotSet("grouped_symptoms", []), SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom)]

                question = grouped_questions.pop(0)
                asked_symptom = grouped_symptoms.pop(0)
                current_symptom = asked_symptom
                symptoms.remove(asked_symptom)
                
                # Debugging prints
                dispatcher.utter_message(text=f"----------Debugging prints-----------")
                dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                dispatcher.utter_message(text=f"-------------------------------------")
                dispatcher.utter_message(text=f"{question}")
                
                return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom)]
            
            #Debug prints:    
            # dispatcher.utter_message(text=f"\nSymptom List: {symptoms}")
            dispatcher.utter_message(text=f"----------Debugging prints-----------")
            dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
            dispatcher.utter_message(text=f"-------------------------------------")
            if label_name.lower() == "other":
                question = grouped_questions.pop(0)
                asked_symptom = grouped_symptoms.pop(0)
                current_symptom = asked_symptom
                symptoms.remove(asked_symptom)
                
                dispatcher.utter_message(text=f"----------Debugging prints-----------")
                dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                dispatcher.utter_message(text=f"-------------------------------------")
                
                dispatcher.utter_message(text=f"{question}")
                return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom)]
            dispatcher.utter_message(text=f"Have you experienced {symptoms[counter]}")
            return [SlotSet("unique_symptoms_kb", symptoms)]
        
        dispatcher.utter_message(text="FAILURE")
        return []
    
class ValidateSymptomForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_symptom_form"
    
    def validate_has_symptom(
        self,
        slot_value: Any,
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
        asking_label = tracker.get_slot("asking_label")
        has_label = tracker.get_slot("has_label")
        
        if not user_symptoms:
            user_symptoms = []
        if not diagnosed_conditions:
            diagnosed_conditions = []

        has_been_diagnosed = False
        diagnosed = []
            
        if asking_label:
            if not slot_value:
                symptoms = [symptom for symptom in symptoms if symptom not in grouped_symptoms]
            if symptoms:    
                return {"has_label" : slot_value, "asking_label" : False, "possible_conditions" : conditions, "has_symptom" : None, "loop_counter" : current_counter, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "unique_symptoms_kb": symptoms}
        
        #Debug Code    
        dispatcher.utter_message(text=f"Current Counter and Symptom: {current_counter} and {current_symptom}")           
        # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
        
        if slot_value:
            #Debug Code
            #dispatcher.utter_message(text=f"I am inserting {current_symptom} to the user symptoms")
            
            user_symptoms.append(current_symptom)
            if conditions:
                for condition in conditions:
                    if current_symptom in condition["Symptoms"]:
                        condition["score"] += 1
                    if condition["score"] >= len(condition["Symptoms"])/2 and condition not in diagnosed_conditions:
                        has_been_diagnosed = True
                        diagnosed.append(condition)
                    
                    #Debug Prints
                    # dispatcher.utter_message(text=f"\n\nCondition: {condition['name']}, Score: {condition['score']}\n")
                    # dispatcher.utter_message(text=f"{diagnosed}\n\n")
            else:
                dispatcher.utter_message(text="Currently, no conditions match your symptoms.")
        
        #Debug Code
        dispatcher.utter_message(text=f"----------Debugging prints-----------")
        dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}\n\nUser symptoms: {user_symptoms}")
        dispatcher.utter_message(text=f"-------------------------------------")
        
        
        if has_been_diagnosed:
            dispatcher.utter_message(text="Your symptoms so far are:")
            count = 1
            for symptom in user_symptoms:
                dispatcher.utter_message(text=f"{count}. {symptom}")
                count += 1
            dispatcher.utter_message(text="\nYour current symptoms match the following conditions:")
            count = 1
            for condition in diagnosed:
                condition_name = condition['name']
                condition_score = condition['score']
                threat = condition['Life-Threat']
                confidence = condition_score/len(condition['Symptoms'])*100
                dispatcher.utter_message(text=f"{count}. Name: {condition_name}\nConfidence: {confidence}%\nLife-Threatening: {threat}")
                diagnosed_conditions.append(condition)
                count+=1
            
            has_been_diagnosed = False
        
        unique_symptoms_len = len(symptoms) 
        #Debug Prints
        dispatcher.utter_message(text=f"\n\nSymptom Length: {unique_symptoms_len}\nCounter: {current_counter}")
            
        if symptoms:
            #Debug prints
            dispatcher.utter_message(text=f"\nThere are symptoms remaining: {symptoms}")
            return {"possible_conditions" : conditions, "has_symptom" : None, "loop_counter" : current_counter, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions}
        dispatcher.utter_message(text=f"\nThere are no more symptoms remaining: {symptoms}. The form should stop now and the user conditions should be displayed")
        return {"possible_conditions" : conditions, "has_symptom" : slot_value, "loop_counter": 0, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions}
    
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