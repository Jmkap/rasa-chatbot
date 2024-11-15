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
from rasa_sdk.events import SlotSet, SessionStarted, ActionExecuted, EventType, FollowupAction
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
        
        # Debug Code
        symptom_data = {
            "control": "record_symptom",
            "data": {
                "symptomName": "Hyper Sense",
                "duration": 3,
                "intensity": 10
            }
        }
        condition_data = {
            "control": "record_condition",
            "data": {
                "conditionName": "Autism",
                "conditionScore": 88,
                "lifeThreat": False,
                "rank" : 1
            }
        } 
        dispatcher.utter_message(json_message=condition_data)
        dispatcher.utter_message(json_message=symptom_data)
        # End of Debug
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
                    symptom_data = {
                        "name": symptom,
                        "duration": 0,     # Default or placeholder value
                        "intensity": -1     # Default or placeholder value
                    }
                    unique_symptoms_kb.append(symptom_data)
        
        # Debug code
        # dispatcher.utter_message(f"Possible conditions:")
        # for condition in possible_conditions:
        #     condition_name = condition['name']
        #     dispatcher.utter_message(f"{condition_name}")
            
        label_ref = db.collection(u'Label')
        unique_symptom_names = [symptom_data["name"] for symptom_data in unique_symptoms_kb]
        query = label_ref.where(u'Related', u'array_contains_any', unique_symptom_names)
        results = query.stream()

        related_labels = []

        for label in results:
            label_data = label.to_dict()
            label_data['name'] = label.id
            if label.id == "Weight":
                stmt = label_data["Statement"]
                dispatcher.utter_message(text=f"{stmt}")
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
        danger = False
        
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
            sorted_conditions = sorted(user_conditions, key=lambda x: x["score"], reverse=False)
            dispatcher.utter_message("\nFinished impression phase.\n")
            dispatcher.utter_message("To summarize:")
            dispatcher.utter_message("Based on your symptoms,")
            count = 1
            
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
                symptom_name = symptoms["name"]
                dispatcher.utter_message(text=f"{count}. {symptom_name}")
                count+=1
                
            
            dispatcher.utter_message("\nThese are the conditions that best match them:")
            count = 1
            
            for condition in sorted_conditions and count <= 3:
                condition_name = condition['name']
                condition_score = condition['score']
                condition_life_threat = condition['threat']
                key_symp = condition["Key_symp"]
            
                if not condition_life_threat:
                    length = len(condition['symptom_length']) + len(key_symp)
                    condition_confidence = condition_score/length*100
            
                    if condition_confidence >= 100:
                        condition_confidence = 99
                        
                    condition_data = {
                        "control": "record_condition",
                        "data": {
                            "conditionName": condition_name,
                            "conditionScore": condition_confidence,
                            "lifeThreat": condition_life_threat
                        }
                    } 
                    dispatcher.utter_message(json_message=condition_data)
                    dispatcher.utter_message(text=f"{count}. {condition_name}, \nConfidence: {condition_confidence}%, \nLife-Threatening: {condition_life_threat}")
                    count+=1
            
                else:
                    danger = True
            
            if danger:
                dispatcher.utter_message(text=f"Your combination of symptoms seem peculiar. It might be best to consult with your trusted doctor as soon as you can.")
        
        else:
            dispatcher.utter_message(text=f"Your combination of symptoms do not lead to anything based on my limited knowledge.")
            dispatcher.utter_message(text=f"I would advise a visit to your trusted doctor as there may be something happening that you and I both do not know about")
        
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
        label_question = ""
        current_symptom = tracker.get_slot("current_symptom")
        
        # Debug
        dispatcher.utter_message(text=f"Entered AskHasSymptom")
        
        if symptoms:
            
            # Debug
            dispatcher.utter_message(text=f"Related Labels: {related_labels}")
            
            if related_labels and (not grouped_questions or not grouped_symptoms):
                dispatcher.utter_message(text=f"There are labels")
                for label in related_labels:
                    if symptoms[counter]["name"] in label['Related']:
                        grouped_symptoms.extend(label['Related'])
                        grouped_questions.extend(label['Questions'])
                        label_name = label['name']
                        
                        label_statement = label.get("Statement", None)
                        dispatcher.utter_message(text=f"The label statement of {label_name} is {label_statement}")
                        if 'Statement' in label.keys():
                            
                            # Debug
                            dispatcher.utter_message(text=f"There is a statement for label '{label_name}'")
                            
                            label_question = label['Statement']
                        else:
                            
                            # Debug
                            dispatcher.utter_message(text=f"There is NON statement for label '{label_name}'")
                        
                        related_labels.remove(label)
                        break
                    
                symptom_names = [symptom["name"] for symptom in symptoms]
                filtered_symptoms = [symptom for symptom in grouped_symptoms if symptom in symptom_names]
                filtered_indices = [grouped_symptoms.index(symptom) for symptom in filtered_symptoms]
                filtered_questions = [grouped_questions[i] for i in filtered_indices]
                grouped_symptoms = filtered_symptoms
                grouped_questions = filtered_questions
                asking_label = True
            
            # Debug
            dispatcher.utter_message(text=f"Grouped Symptoms: {grouped_symptoms}")
            dispatcher.utter_message(text=f"Grouped Questions: {grouped_questions}")
            dispatcher.utter_message(text=f"Unique Symptoms: {symptoms}")
            
                         
            # if there is a grouped question to be addressed, address it  first 
            # else, continue normally with the current code below
            # dispatcher.utter_message(f"The current label is: {label_name.lower()}")
            if label_name.lower() != "other" and (grouped_questions or grouped_symptoms):
                
                # ===DEBUG CODE====
                dispatcher.utter_message(f"Label: {label_name.lower()} is not the same as Label: other")
                
                # If currently asking label
                # return asking_label and related_labels to their slots, and update all other slots
                # the flow should return to validate symptom form
                if asking_label:
                    
                    # Debug
                    dispatcher.utter_message(text=f"Asking Label now...")
                    
                    dispatcher.utter_message(f"{label_question}")
                    return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), 
                            SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("label", label_name)]
                
                # If the user said no to the asked label in validate symptom form
                if not has_label:
                    
                    #Debug 
                    # dispatcher.utter_message(text=f"----------Debugging prints-----------")
                    dispatcher.utter_message(text=f"Entered not has_label. We should not be here...")
                    dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                    # dispatcher.utter_message(text=f"-------------------------------------")
                    # dispatcher.utter_message(text=f"\nSymptom List: {symptoms}")
                    
                    if symptoms[counter]:
                        # Remove the symptoms with denied labels
                        symptoms = [symptom for symptom in symptoms if symptom["name"] not in grouped_symptoms]
                    
                    return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", []), SlotSet("grouped_symptoms", []), SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom)]
                
                # Debug
                dispatcher.utter_message(text=f"Not asking for labels anymore")
                
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
                return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), 
                        SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom), SlotSet("label", label_name)]
            
            #Debug prints:    
            # dispatcher.utter_message(text=f"\nSymptom List: {symptoms}")
            # dispatcher.utter_message(text=f"----------Debugging prints-----------")
            # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
            # dispatcher.utter_message(text=f"-------------------------------------")
            
            # If the label is "Other"
            if label_name.lower() == "other":
                
                # Debug
                dispatcher.utter_message(text=f"Label is \"Other\"")
                
                question = grouped_questions.pop(0)
                asked_symptom = grouped_symptoms.pop(0)
                current_symptom = asked_symptom
                symptoms = [symptom for symptom in symptoms if symptom["name"] != asked_symptom]
                
                # dispatcher.utter_message(text=f"----------Debugging prints-----------")
                # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
                # dispatcher.utter_message(text=f"-------------------------------------")
                
                dispatcher.utter_message(text=f"{question}")
                return [SlotSet("unique_symptoms_kb", symptoms), SlotSet("grouped_questions", grouped_questions), SlotSet("grouped_symptoms", grouped_symptoms), 
                        SlotSet("related_labels", related_labels), SlotSet("asking_label", asking_label), SlotSet("current_symptom", current_symptom), SlotSet("label", label_name)]
            
            dispatcher.utter_message(text=f"Symptom has no label! Contact administration for this!")
            symptom_name = symptoms[counter]["name"]
            dispatcher.utter_message(text=f"Have you experienced {symptom_name}")
            return [SlotSet("unique_symptoms_kb", symptoms)]
        
        dispatcher.utter_message(text="FAILURE")
        return []
    
class ActionAskDay(Action):
    def name(self) -> Text:
        return "action_ask_day"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        asking_duration = tracker.get_slot("asking_duration")
        
        # Debug
        dispatcher.utter_message(text=f"Entered ASK DURATION")
        
        # If asking duration
        if asking_duration:
        # Execute action
            dispatcher.utter_message(text=f"Including today, for how many days have you been experiencing this symptom?")
            return[]
        
        # Debug
        dispatcher.utter_message(text=f"Skipping ASK DURATION, setting slot to 0")
        dispatcher.utter_message(text=f"If you still see me, something's wrong")
        
        return[SlotSet("day", 0)] 
    
class ActionAskIntensity(Action):
    def name(self) -> Text:
        return "action_ask_intensity"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        asking_intensity = tracker.get_slot("asking_intensity")
        
        # Debug
        dispatcher.utter_message(text=f"Entered ASK INTENSITY")
        
        # If asking duration
        if asking_intensity:
        # Execute action
            dispatcher.utter_message(text=f"On a scale of 0-10 (0 is no pain), how intense is the pain?")
            return[]
        
        # Debug
        dispatcher.utter_message(text=f"Skipping ASK INTENSITY, setting slot to 0")
        dispatcher.utter_message(text=f"If you still see me, something's wrong")
        
        return[SlotSet("intensity", 0), ] 
    
class ValidateSymptomForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_symptom_form"
    
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
        skip_cycle = tracker.get_slot("skip")
        
        # Debug Code
        dispatcher.utter_message(text=f"Exited Ask Actions")
        dispatcher.utter_message(text=f"Starting the cycle")
        dispatcher.utter_message(text=f"Skip Cycle?: {skip_cycle}")
        
        # if request to skip cycle,
        # return immediately
        if (skip_cycle):
            
            # Debug
            dispatcher.utter_message(text=f"Skipping this cycle...")
            
            skip_cycle = False
            return {"has_symptom" : None, "day": None, "skip": skip_cycle}
        
        # Initialize arrays
        if not user_symptoms:
            user_symptoms = []
        if not diagnosed_conditions:
            diagnosed_conditions = []

        has_been_diagnosed = False
        diagnosed = []
        
        # Will be marked true if 
        # asking_label was set to true in AskHasSymptom
        if asking_label:
            
            # Debug
            dispatcher.utter_message(text=f"Asking Label in validate symptom form")
            
            # If user said no,
            # Cut out symptoms from the current label (which are in the current grouped symptoms slot)
            if not slot_value:
                
                # Debug
                dispatcher.utter_message(text=f"\nAccording to your response, you have not experienced anything related to this label")
                dispatcher.utter_message(text=f"\nRemoving the grouped symptoms from your possible symptom lists...")
                
                symptoms = [symptom for symptom in symptoms if symptom["name"] not in grouped_symptoms]
                
                if symptoms:
                    return {"grouped_questions": [], "grouped_symptoms": [], "has_label" : slot_value, "possible_conditions" : conditions, "has_symptom" : None, "day": None, 
                            "loop_counter" : current_counter, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "unique_symptoms_kb": symptoms}
            # If there are remaining symptoms, 
            # return the user's answer (slot value), update asking_label and all other slots
            # has_symptom slot must be set to none so the form continues to loop.
            # this returns to AskHasSymptom and skips if not has_label part
            if symptoms:
                return {"has_label" : slot_value, "asking_label" : False, "possible_conditions" : conditions, "has_symptom" : None, "day": None, 
                        "loop_counter" : current_counter, "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "unique_symptoms_kb": symptoms}
        
        #Debug Code    
        # dispatcher.utter_message(text=f"Current Counter and Symptom: {current_counter} and {current_symptom}")           
        # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}")
        
        # If the user says yes to symptom question
        if slot_value:
            
            #Debug Code
            #dispatcher.utter_message(text=f"I am inserting {current_symptom} to the user symptoms")
            
            # Append the current symptom being asked to user's symptoms
            asking_duration = True
            matching_symptom = next((symptom for symptom in symptoms if symptom["name"] == current_symptom), None)
            user_symptoms.append(matching_symptom)
            if conditions:
                for condition in conditions:
                    if current_symptom in condition["Symptoms"]:
                        if current_symptom in condition["Key_symp"]:
                            condition["score"] += 2
                        else:
                            condition["score"] += 1

                    # If a condition has a high enough score, and it's not an already diagnosed condition
                    # Display to the user progress so far.
                    diagnosed_conditions_names = [cond['name'] for cond in diagnosed_conditions]
                    if condition["score"] >= len(condition["Symptoms"])/2 and condition["name"] not in diagnosed_conditions_names:
                        has_been_diagnosed = True
                        diagnosed.append(condition)
                    
                    #Debug Prints
                    # dispatcher.utter_message(text=f"\n\nCondition: {condition['name']}, Score: {condition['score']}\n")
                    # dispatcher.utter_message(text=f"{diagnosed}\n\n")
            else:
                dispatcher.utter_message(text="Currently, no conditions match your symptoms.")
        
        #Debug Code
        # dispatcher.utter_message(text=f"----------Debugging prints-----------")
        # dispatcher.utter_message(text=f"Grouped symptoms: {grouped_symptoms}\n\nUnique symptoms: {symptoms}\n\nUser symptoms: {user_symptoms}")
        # dispatcher.utter_message(text=f"-------------------------------------")
        
        # Display progress so far if there's a new diagnosis.
        if has_been_diagnosed:
            dispatcher.utter_message(text="Your symptoms so far are:")
            count = 1
            for symptom in user_symptoms:
                dispatcher.utter_message(text=f"{count}. {symptom}")
                count += 1
            dispatcher.utter_message(text="\nYour current symptoms match the following conditions:")
            count = 1
            for condition in diagnosed_conditions:
                condition_name = condition['name']
                condition_score = condition['score']
                threat = condition['Life-Threat']
                confidence = condition_score/len(condition['Symptoms'])*100
                dispatcher.utter_message(text=f"{count}. Name: {condition_name}\nConfidence: {confidence}%\nLife-Threatening: {threat}")
                diagnosed_conditions.append(condition)
                count+=1
            
            has_been_diagnosed = False
        
        # remove the current symptom from the symptom list to update the list and move on to the next symptom
        symptoms = [symptom for symptom in symptoms if symptom["name"] != current_symptom]
        
        #Debug Prints
        # unique_symptoms_len = len(symptoms)
        # dispatcher.utter_message(text=f"\n\nSymptom Length: {unique_symptoms_len}\nCounter: {current_counter}")
        
        # Move to next slot, update everything
        
        # Debug
        dispatcher.utter_message(text=f"Exiting Validate Has Symptom")
        if slot_value:
            return {"possible_conditions" : conditions, "has_symptom" : None, "day": None, "loop_counter": current_counter, "unique_symptoms_kb": symptoms,
                "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration}
        
        return {"possible_conditions" : conditions, "has_symptom" : slot_value, "day": None, "loop_counter": current_counter, "unique_symptoms_kb": symptoms,
                "user_symptoms" : user_symptoms, "diagnosed_condition": diagnosed_conditions, "asking_duration": asking_duration}
    
    def validate_day(
        self,
        slot_value: any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        asking_duration = tracker.get_slot("asking_duration")
        asking_intensity = tracker.get_slot("asking_intensity")
        symptoms = tracker.get_slot("unique_symptoms_kb")
        user_symptoms = tracker.get_slot("user_symptoms")
        label = tracker.get_slot("label")
        
        # Debug
        dispatcher.utter_message(text=f"Entered VALIDATE DURATION")
        
        if asking_duration:
            
            # Debug
            dispatcher.utter_message(text=f"User answered: {slot_value}")
            
            if label.lower() == "pain":
                asking_intensity = True
            else:
                asking_intensity = False
                
                    # Debug
                dispatcher.utter_message(text=f"Exiting VALIDATE DURATION")
                
                return {"intensity": None, "day": slot_value, "asking_intensity": asking_intensity, "asking_duration": False}
                
            
        
        # Debug
        dispatcher.utter_message(text=f"Skipping VALIDATE DURATION")
        dispatcher.utter_message(text=f"If you still see this, something's wrong")
        
        return {"intensity": None, "day": 0}
    
    def validate_intensity(
        self,
        slot_value: any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        asking_intensity = tracker.get_slot("asking_intensity")
        symptoms = tracker.get_slot("unique_symptoms_kb")
        
        # Debug
        dispatcher.utter_message(text=f"Entered VALIDATE INTENSITY")
        
        if asking_intensity:
            
            # Debug
            dispatcher.utter_message(text=f"User answered: {slot_value}")
            dispatcher.utter_message(text=f"Exiting VALIDATE INTENSITY")
            
            if symptoms:
                return {"has_symptom": None, "intensity": slot_value, "asking_intensity": False}
            return {"has_symptom": True, "intensity": slot_value, "asking_intensity": False}
        
        # Debug
        dispatcher.utter_message(text=f"Skipping VALIDATE INTENSITY")
        dispatcher.utter_message(text=f"If you still see this, something's wrong")
        
        return {"has_symptom": None, "intensity": 0}
        
    
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