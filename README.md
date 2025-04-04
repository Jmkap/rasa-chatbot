# **Firestore Database Initial Steps**
### Get a service account.
When using a firestore database and attempting to access it through code, you first need to make sure that you have a service account.
- You need to be added as a member of the project in **firebase** where your **firestore database** is stored.
- Once added, go to https://console.cloud.google.com/
- At the at the top left side inside the menu bar, to the right of the **Google Cloud Logo**, you can see the name of the project you are currently in. Click that name and ensure you are inside the correct project
- Click on the search bar at the top and type in "Service Account"
- It should show under the search results "Service Accounts" with "IAM & Admin" as its subtext; click that.
- Select an appropriate service account or create a new service account and select it
- At the top menu bar that contains "Details", "Permissions", "Keys", "Metrics", and "Logs", select "Keys"
- Click the "Add key" button and then "Create new key"
- Select the **JSON** key which should automatically download your service account file that contains this key
- This file goes into the **service account folder** and is recognized within the source code as **knowledgebase.json**, so be sure to rename it or change the file name within the code.

**IMPORTANT!**
----------------------------------------------------
- Ensure that you **DO NOT** commit your **virtual environment**.
- Also **DO NOT** commit the **service account**. The service account **MUST NOT** be shared online in any way to keep knowledgebase access safe.
- The folder named **.rasa** contains caches that are stored whenever the chatbot is trained. These files are heavy on the storage and can be cleared, but it will affect training speed. 
- The .rasa/cache folder size might become large over time. keep an eye on it.
- add the name of your virtual environment to .gitignore

----------------------------------------------------
// ALL RUN COMMANDS SHOULD NOT INCLUDE THE QUOTATION MARKS: ""

// ENSURE THAT YOUR CLI DIRECTORY IS AT THE FOLDER "Rasa Chatbot" run: "cd "path/to/rasa chatbot""

Things to do before anything else:

1. Python 3.8 - for some reason, rasa install packages 
do not work with higher versions
- Ensure that the working Python in your environment variables or at least within the virtual environment is exactly **3.8**
- This applies when attempting to install **RASA OPEN SOURCE** through **pip install**

3. Create a Virtual Environment(VENV) to setup rasa
	- run: "python -m venv _VENV_NAME_HERE_"

4. Run your created VENV
	- run: ".\_CREATED_VENV_NAME_HERE_\scripts\activate"
	- *NOTE*: the name of your venv, encased in parenthesis,
		should show in the command line if successful

5. Install Rasa
	- run: "pip install rasa"
	- IN CASE OF ERROR:
		- Check if the correct Python version, run: "python --version" in your VENV
		- If the correct version but still error, run: "python -m pip install --upgrade pip"
		- If all of the above has been done but the error persists, further troubleshooting may be required on a case-by-case basis.
		- Make sure to check on the error codes which might differ for each device.
		- Some familiar/previously encountered errors:
  			- psycopg2 error: "Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/"
   				- This error is usually fixed by updating microsoft visual c++ to the latest version
       			- SciPy Error: "SciPy requires GCC >= 8.0"
          			- This error is resolved simply by updating the current device's GCC version to >= 8.0 or simply the latest version either through **mingw-w64** or any other known or 					familiar methods
             			- Check the current GCC version by doing "gcc --version". If command is not recognized, GCC might not be properly installed or is not installed at all.
                	- Python Version Error: "...requires python 3.8 or greater"
                 		- This is usually fixed by installing **Python 3.8 specifically**. There have been multiple attempts to use the latest versions, yet display the same error during 					installation
                   		- Double-check environment variables and ensure that **Python 3.8 is above any other listed Python version**.

6. Install spaCy
	- run: "pip install spacy==3.4.4"
	- same steps with installing rasa
 	- 3.4.4 is needed since the later versions require Python 3.9 or greater

7. Download the spaCy language model:
	- run: "python -m spacy download en_core_web_md"

8. Download and put a Service Account for the Firebase Project in the "service account" folder
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

- rules.yml: includes rules that dictate how a conversation SHOULD go. These are paths that the chatbot attempts to follow no matter what and are not as flexible as stories. Stories and rules need to be distinct from each other if a story/rule looks the same, this will cause "confusion" for the chatbot, meaning the conversation might not go where expected

- nlu.yml: this is where intents are defined alongside other things like lookup-tables. Everything NLU.

- credentials.yml: Mostly untouched, but contains credentials information of the chatbot
- config.yml: File which decides which pipelines should be used for training. For a list of pipelines and their functions, visit the documentation of Rasa Open Source: https://legacy-docs-oss.rasa.com/docs/rasa/model-configuration
- endpoints.yml: Mostly concerned with addresses or endpoints that the running rasa server will communicate in. In current development, only the endpoints for the action server is configured.

- Action Server: This is the server that runs the actions.py which allows the chatbot to do custom actions. It is started by executing the command "rasa run actions" in a CLI.
- Rasa Server: This is the server that runs the Rasa Chatbot itself. It is started by executing "rasa shell" which runs the latest trained model inside the CLI. Chatting will only be available through the CLI

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
	(more info on this online / documentation)

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

Running "rasa shell" should allow you to chat with the chatbot once finished loading.
Running "rasa run actions.py" or "rasa run actions.py --debug" should  show the functions loaded and will keep that CLI running
There are other commands to execute both actions.py and test the chatbot.

-------------------------------------------------------------------------

If you want to run with the UI:
1. Android Studios URL should be changed to your current IPv4 Address found in the CMD "ipconfig" (If attempting to run locally)
	- If through a server, then it should be the server's public IPv4 instead.
2. actions.py must be run before proceeding.
3. instead of running "rasa shell", run: "rasa run -m models --enable-api --endpoints endpoints.yml"
4. adding "--debug" at the end of the command should show much more detail on runtime.
5. Adjusting the waiting time for REST API to produce an error is possible by adding "--response-time 15" to make the server wait for 15 seconds before returning a REST API error.
6. If it all works, rasa should connect to a server, and running the Android app should show an initial message from the chatbot (unless rest.api error occured)
7. If troubleshooting, check ALL the CLI for error messages, only one of them will show the actual error/exception depending on where the exception is.

-------------------------------------------------------------------------

Other Possibly Helpful souces:
1. https://legacy-docs-oss.rasa.com/docs/rasa/
2. https://www.youtube.com/playlist?list=PLp9h3aIPyUbZyCUP4ELTaS2ajxKNWaSnU
