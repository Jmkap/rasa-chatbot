*WAIT! YOUR FILES ARE INCOMPLETE*
---------------------------------------------------
Get a service account.
- need to be added to the database
- Go to https://console.cloud.google.com/iam-admin/serviceaccounts?project=menstrual-app-4b6b5&supportedpurview=project and select the menstrual app project
- Click the enabled "drflow-knowledge..."
- Go to keys
- Download a **JSON** key

----------------------------------------------------
// ALL RUN COMMANDS SHOULD NOT INCLUDE THE QUOTATION MARKS: ""

// ENSURE THAT YOUR CLI DIRECTORY IS AT THE FOLDER "Rasa Chatbot" run: "cd "path/to/rasa chatbot""

Things to do before anything else:

1. Python 3.8 - for some reason, rasa install packages 
do not work with higher versions

2. Create a Virtual Environment(VENV) to setup rasa
	- run: "python -m venv _VENV_NAME_HERE_"

3. Run your created VENV
	- run: ".\_CREATED_VENV_NAME_HERE_\scripts\activate"
	- *NOTE*: the name of your venv encased in parenthesis 
		should show in the command line if successful

4. Install Rasa
	- run: "pip install rasa"
	- IN CASE OF ERROR:
		- check if correct python version, run: "python --version" in your VENV
		- if correct version but still error, run: "python -m pip install --upgrade pip"
		- if all of the above is done but still error, further troubleshooting is required
		Make sure to check the error prints to know what's wrong (ask help from Jm if can't fix)

5. Install spaCy
	- run: "pip install spacy"
	- same steps with installing rasa

6. Download the spaCy language model:
	- run: "python -m spacy download en_core_web_md"

7. Download and put a Service Account for the Firebase Project in the "service account" folder
	- Read note in "service account folder"

===============ALL SET | More notes below================

How to Run Rasa Chatbot:

There are two parts of the chatbot: The .yml files and the actions.py file. 

.YML FILES
-----------------------------------------------------------
The .yml files mainly include chatbot settings, nlu, domain, stories, etc.
- domain.yml: includes entities, utterances/responses, additional actions, forms, etc.

- stories.yml: includes stories that dictate how a conversation MIGHT go. The chatbot may deviate from a defined story 
	depending on it's training data and other stories or rules

- rules.yml: includes rules that dictate how a conversationg SHOULD go. storiese and rules need to be distinct from each other
	if a story/rule looks the same, this will cause "confusion" for the chatbot, meaning the conversation might not go where expected

- nlu.yml: this is where intents are defined alongside other things like lookup-tables. Everything NLU.

- credentials, config, endpoints.yml: Mostly concerned with the settings of the chatbot. The pipelines to be used, credentials, or the url of the actions.py server
	(if not confident with the changes in these files, MAKE SURE IT WILL NOT BREAK THE CHATBOT FIRST OR CREATE A BACKUP)

------------------------------------------------------------------
*FOR FURTHER INFORMATION, VISIT THE RASA API DOCUMENTATION: https://rasa.com/docs/rasa/*
------------------------------------------------------------------


ACTIONS.PY
-----------------------------------------------------------
The actions.py is a python file where you can define custom actions
- rasa includes "actions" which are a set of instruction on what the chatbot needs to do.

- there are pre-defined actions and custom actions(actions.py).

- All actions, before being used, need to be declared in the "actions" part of the "domain.yml"

- actions are usually used in stories or rules where for example, if an intent is detected, do a certain action. (check stories.yml and rules.yml for concretee examples)

- This is where the knowledge base is loaded, forms are modified, impressions are made, or any specific undefined algorithm is done.

- Each function represents a custom action and some functions are already existing actions that are overridden for more specific uses (like Validate*FormName*Form)
	(more info on these online/documentation)

- We are also able to store entities from other sources into the chatbot's existing entities, provided that the stored entities are the appropriate/expected data type (look at domain.yml for entities)

-------------------------------------------------------------------

To run and use the chatbot:

1. Open two terminals/CLI
2. make sure that the directories are in "Rasa Chatbot" and that your venv is running on both
3. If changes are made with ANY .yml file, if not then ignore this step:
	- train the chatbot with: "rasa train"
4. One CLI will run the chatbot, run: "rasa shell" or "rasa shell --debug". This will run the latest trained model. If --debug is used, it will show the entire "thinking process" of the chatbot as well as possible exceptions. 
5. The other CLI will run "actions.py", run: "rasa run actions" or "rasa run actions --debug" if you want to see the errors/exceptions that happened
6. Wait for both CLI to finish running, this will usually be denoted by "finished running" messages". 

Running "rasa shell" should allow you to chat with the  chatbot once finished loading.
Running "rasa run actions.py" or "rasa run actions.py --debug" should  show the functions loaded and will keep that CLI running
There are other commands to execute both actions.py or to test the chatbot.

-------------------------------------------------------------------------

If you want to run with the UI:
1. Android Studios url should be changed to your current IPv4 Address found in the CMD "ipconfig"
2. actions.py must be run before proceeding.
3. instead of running "rasa shell", run: "rasa run -m models --enable-api --endpoints endpoints.yml"
4. If it all works, rasa should connect to a server and running the android app should show an initial message from the chatbot (unless rest.api error occured)
5. If troubleshooting, check ALL the CLI for error messages, only one of them will show the actual error/exception depending on where the exception is.

-------------------------------------------------------------------------

Other Possibly Helpful souces:
1. https://www.youtube.com/playlist?list=PLp9h3aIPyUbZyCUP4ELTaS2ajxKNWaSnU
