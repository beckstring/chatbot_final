import os
import time
import wave
import datetime
#import pyaudio
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.expansionpanel import (MDExpansionPanel, MDExpansionPanelOneLine,
                                       MDExpansionPanelThreeLine)
from kivymd.uix.list import IconLeftWidget, TwoLineIconListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivy.utils import platform
from kivymd import images_path


import openai
#from gtts import gTTS
#import speech_recognition as sr






#####################################

PATH_TO_HISTORY = "files"
PATH_TO_PERSONALITY = "personality_profile/personality.txt"
PATH_TO_SYSTEM_PROMPT = "prompts/system_prompt.txt"
PATH_TO_SUMMARY_PROMPT = "prompts/summary_prompt.txt"
PATH_TO_STORAGE_PROMPT = "prompts/storage_prompt.txt"
PATH_TO_API_KEY = "settings/api_key.txt"
##### Utils #######################

def get_text_file_names(directory_path):
    text_file_names = []
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.txt'):
            text_file_names.append(file_name)
    return text_file_names

def read_text_file(file_path):
    with open(file_path, 'r') as f:
        text = f.read()
    return text

def write_text_file(path,text):
    # Generate the file name based on the current date and time
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M') + '.txt'
    # Write the text to the file
    with open(f"{path}/{now}", 'w') as f:
        f.write(text)

def overwrite_text_file(path, text):
    # Write the text to the file
    with open(path, 'w') as f:
        f.write(text)

def create_filesystem(path, filename):
    if not os.path.exists(path):
        os.mkdir(path)
    if not os.path.exists(f"{path}/{filename}.txt"):
        with open(f"{path}/{filename}.txt", "w"):
            pass


#####################################

# Create directory if it does not exist.
if not os.path.exists("files"):
    # create the directory if it doesn't exist
    os.mkdir("files")

# Create profile folder / personality profile if it does not exist

create_filesystem(path = "personality_profile", 
                    filename = "personality")

# Create files to store the prompts
create_filesystem(path = "prompts", 
                    filename = "system_prompt")

# Create files to store the prompts
create_filesystem(path = "prompts", 
                    filename = "summary_prompt")

# Create files to store the prompts
create_filesystem(path = "prompts", 
                    filename = "storage_prompt")

# Create files to store the prompts
create_filesystem(path = "settings", 
                    filename = "api_key")


KV = '''

<DrawerClickableItem@MDNavigationDrawerItem>
    focus_color: "#e7e4c0"
    text_color: "#4a4939"
    icon_color: "#4a4939"
    ripple_color: "#c5bdd2"
    selected_color: "#0c6c4d"


<DrawerLabelItem@MDNavigationDrawerItem>
    focus_color: "#e7e4c0"
    text_color: "#4a4939"
    icon_color: "#4a4939"
    ripple_color: "#c5bdd2"
    selected_color: "#0c6c4d"

<SidebarButton@MDRectangleFlatIconButton>
    text_color: "#4a4939"
    icon_color: "#4a4939"
    line_color: 0, 0, 0, 0


<ChatbotBackend>:

    BoxLayout:
        # This one serves the top bar
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15

            # Ghost label to push other labels to the right #REFACTOR 
            MDLabel:
                size_hint_x: 0.6

            MDIconButton:
                icon: root.sound_icon
                on_press: root.update_sound_button()

            MDIconButton:
                icon: 'eye-refresh-outline'
                on_press: root.update_profile_button()

            MDIconButton:
                icon: 'account-tie'
                on_press: root.personalize_content()
                md_bg_color: root.button_color

            MDIconButton:
                icon: 'refresh'
                on_press: root.initalize_conversation()

            # Icons to save and update the icon properties
            MDIconButton:
                icon: 'floppy'
                on_press: root.save_button()
            

        MDScrollView:
            do_scroll_x: False
            do_scroll_y: True
            MDLabel:
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: 10, 10
                text: root.chat_history

        MDBoxLayout:
            size_hint_y: 0.2
            TextInput:
                id: user_input
                text: root.user_input
                multiline: True

        MDBoxLayout:
            size_hint_y: 0.125

            MDIconButton:
                icon: 'delete'
                size_hint_x: 1/3
                on_press: root.delete_button()

            MDIconButton:
                icon: 'record'
                text_color: "white"
                on_press: root.start_recording()
                on_release: root.end_recording()
                size_hint_x: 1/3

            MDIconButton:
                icon: 'send'
                text_color: "white"
                on_press: root.send_button()
                on_release: root.speak()
                size_hint_x: 1/3

####### HISTORY CLASS ###################### 
                

# Used to load history
<HistoryClass>:
    adaptive_height: True
    MDLabel:
        text: root.second_text
        adaptive_height: True
        padding: 10, 10


####### HISTORY SCREEN ######################  

<HistoryScreen>:
    BoxLayout:
        # This one serves the top bar
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15

            # Ghost label to push other labels to the right #REFACTOR 
            MDLabel:
                size_hint_x: 0.8
            
        MDScrollView:
            MDGridLayout:
                id: box
                cols: 1
                adaptive_height: True      

####### Personality SCREEN ######################  

<PersonalityScreen>:
    BoxLayout:
        # This one serves the top bar
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15

            # Ghost label to push other labels to the right #REFACTOR 
            MDLabel:
                size_hint_x: 0.8

        MDScrollView:
            do_scroll_x: False
            do_scroll_y: True
            TextInput:
                id: personality_profile
                text: root.personality_profile
                multiline: True
    
        MDRectangleFlatIconButton:
            size_hint_y: 0.125
            icon: "update"
            text: "Update Profile"
            text_color: "white"
            line_color: "white"
            icon_color: "white"
            size_hint_x: 1
            on_press: root.update_profile()

####### PROMPT SCREEN ######################  

<PromptScreen>:
    BoxLayout:
        # This one serves the top bar
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15


        MDScrollView:
            do_scroll_x: False
            do_scroll_y: True
            MDGridLayout:
                cols: 1
                adaptive_height: False 

                MDLabel:
                    size_hint_y: 0.1
                    text: "SYSTEM PROMPT"
                
                TextInput:
                    id: system_prompt
                    text: root.system_prompt
                    multiline: True

                MDSeparator:

                MDLabel:
                    size_hint_y: 0.1
                    text: "SUMMARY PROMPT"
                
                TextInput:
                    id: summary_prompt
                    text: root.summary_prompt
                    multiline: True

                MDSeparator:

                MDLabel:
                    size_hint_y: 0.1
                    text: "STORAGE PROMPT"
                
                TextInput:
                    id: storage_prompt
                    text: root.storage_prompt
                    multiline: True

    
        MDRectangleFlatIconButton:
            size_hint_y: 0.125
            icon: "update"
            text: "Update Prompts"
            text_color: "white"
            line_color: "white"
            icon_color: "white"
            size_hint_x: 1
            on_press: root.update_prompts()
                            
####### API-key SCREEN ######################  

<ApiScreen>:
    BoxLayout:
        # This one serves the top bar
        orientation: 'vertical'

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: 0.15


        MDScrollView:
            do_scroll_x: False
            do_scroll_y: True
            MDGridLayout:
                cols: 1
                adaptive_height: False 

                MDLabel:
                    size_hint_y: 0.2
                    text: "API KEY"
                
                TextInput:
                    id: api_key
                    text: root.api_key
                    multiline: True

    
        MDRectangleFlatIconButton:
            size_hint_y: 0.125
            icon: "update"
            text: "Update Prompts"
            text_color: "white"
            line_color: "white"
            icon_color: "white"
            size_hint_x: 1
            on_press: root.update_prompts()

####### SETTINGS CLASS ######################        

<ChatbotSettings>:

    MDFloatLayout:

        # Add slider for temperature 
        MDSlider:
            id: slider
            min: 0
            max: 1
            value: 0.7
            hint: True
            step: 0.01  

####### SKELLETON / Screen Manager ######################
            
<ContentNavigationDrawer>

    MDList:
        MDNavigationDrawerLabel:
            text: "Menu"

        SidebarButton:
            icon: "chat"
            text_right_color: "#4a4939"
            text: "Chatbot"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "chatbot"

        SidebarButton:
            icon: "head-snowflake-outline"
            text_right_color: "#4a4939"
            text: "Profile"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "profile"

        SidebarButton:
            icon: "book"
            text: "History"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "history"

        MDNavigationDrawerDivider:

        MDNavigationDrawerLabel:
            text: "Settings"

        SidebarButton:
            icon: "key"
            text: "API-Key"

            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "api_screen"


        SidebarButton:
            text: "Prompts"
            icon: "message-outline"
            on_press:
                root.nav_drawer.set_state("close")
                root.screen_manager.current = "prompts"

####### SCREEN MANAGER ######################

MDScreen:
    MDTopAppBar:
        title: ""
        elevation: 4
        pos_hint: {"top": 1}
        md_bg_color: "#e7e4c0"
        specific_text_color: "#4a4939"
        left_action_items: [["menu", lambda x: nav_drawer.set_state("open")]]


    MDNavigationLayout:

        MDScreenManager:
            id: screen_manager


            MDScreen:
                name: "chatbot"
                id: ChatbotClass

                ChatbotBackend
                

            PersonalityScreen:
                name: "profile"

            HistoryScreen:
                name: "history"

            
            ApiScreen:
                name: "api_screen"
                id: api_screen 

                
            PromptScreen:
                name: "prompts"
                id: prompts 
            
                

        MDNavigationDrawer:
            id: nav_drawer
            radius: (0, 16, 16, 0)

            ContentNavigationDrawer:
                screen_manager: screen_manager
                nav_drawer: nav_drawer
'''


class ChatbotBackend(BoxLayout):
    chat_history = StringProperty()
    user_input = StringProperty()
    button_color = StringProperty()
    sound_icon = StringProperty()
        
    def __init__(self, **kwargs):
        super(ChatbotBackend, self).__init__(**kwargs)

        # Define personalization option
        self.personalize = False
        # Initialitze button color
        self.button_color = "#E7E5BE"

        # Initalize sound variable
        self.sound_on = False

        # Initalize sound icon
        self.sound_icon = "volume-off"

        # Initialize everything for chat conversation
        self.initalize_conversation()

        # Setup a speech to text engine
        # initialize the recognizer
        #self.speech_regonizer = sr.Recognizer()


    def personalize_content(self):
        """
        Switch personalization option to on / off
        """
        if self.personalize:
            self.personalize = False
            # Change to white if not on
            self.button_color = "#E7E5BE"
        else:
            self.personalize = True
            # Change to red if active
            self.button_color = "#FF0000"

        # Update system prompt
        self.initalize_conversation()

    def update_sound_button(self):
        """
        Update sound preference
        """
        if self.sound_on:
            self.sound_on = False
            self.sound_icon = "volume-off"
        else:
            self.sound_on = True
            self.sound_icon = "volume-high"
        


    def initalize_conversation(self):
        """
        Load the system prompt and start a conversation
        """
        # Read API key from file
        temp_api_key = read_text_file(PATH_TO_API_KEY)
        # Set API key
        openai.api_key = temp_api_key
        # Set model
        self.model_id = 'gpt-3.5-turbo'
        
        # Create list to store ChatConversation
        self.conversation = []

        # Load relevant prompts
        self.system_prompt = read_text_file(PATH_TO_SYSTEM_PROMPT)
        self.summary_prompt = read_text_file(PATH_TO_SUMMARY_PROMPT)
        self.storage_prompt = read_text_file(PATH_TO_STORAGE_PROMPT)

        # Load personality profile
        self.personality_profile = read_text_file(PATH_TO_PERSONALITY)

        # Personalize system prompt
        if self.personalize:
            # Add System prompt to conversation list 
            temp_system_prompt = f"{self.system_prompt} \n Consider the following profile in your answers: {self.personality_profile}"
            self.conversation.append({'role': 'system', 'content': temp_system_prompt})
        else:
            self.conversation.append({'role': 'system', 'content': self.system_prompt})

        # Create variables to store chat_histoy, user input and chatbot response
        self.chat_history = ""
        self.user_input = ""
        self.chatbot_response = ""

        # Load the conversation history / system prompt
        self.update_chat_history()


    def get_chatbot_answer(self):
        """
        Submit latest user input to OpenAI API
        """
        
        # Get response for latest input
        response = openai.ChatCompletion.create(model=self.model_id,
                                                messages=self.conversation)
        
        print(response)

        # Store chatbot response
        self.chatbot_response = response["choices"][0]["message"]["content"]

        # Append chatbot answer to conversation
        self.conversation.append({'role': 'assistant', 'content': self.chatbot_response})

    def add_user_input(self):
        """
        Append user input to conversation history
        """
        # Append user input to conversation
        self.conversation.append({'role': 'user', 'content': self.ids.user_input.text})

        # Clear user input 
        self.ids.user_input.text = ""

    def update_chat_history(self):
        # Iterate through conversation and append messages
        self.chat_history = ""
        for idx, item in enumerate(self.conversation):
            # append the formatted string to the result string
            self.chat_history += f"{item['role'].upper()}: {item['content']}\n\n"     

    def send_button(self):
        # Append user input to conversation history
        self.add_user_input()

        # Call OpenAI update to receive an answer
        self.get_chatbot_answer()

        # Update the chat history
        self.update_chat_history()


    def delete_button(self):
        # Remove last user input and chatbot answer from the conversation
        self.conversation = self.conversation[:-2]
        print(self.conversation)
        # Update the history
        self.update_chat_history()

    def save_button(self):
        """
        Save conversation as text file
        """
        # Add submit request with summary prompt to summarize the conversation
        self.conversation.append({'role': 'user', 'content': self.summary_prompt})

        # Get summary of the conversation
        self.get_chatbot_answer()

        # Update the history
        self.update_chat_history()

        # Store Chat history as text file
        write_text_file(path = PATH_TO_HISTORY,
                        text = self.chat_history)
        
    def update_profile_button(self):
        """
        Extend personality profile
        """
        # Add submit request with storage prompt 
        update_request = f"{self.storage_prompt} \n This is the current profile: {self.personality_profile}"
        self.conversation.append({'role': 'user', 'content': update_request})

        # Get summary of the conversation
        self.get_chatbot_answer()

        # Update the history
        self.update_chat_history()

        # Store updated personality profile as text file
        overwrite_text_file(path = PATH_TO_PERSONALITY,
                            text = self.chatbot_response)

    
    # Class utils ############################
        
    def speak(self):
        """
        Read Chatbot response
        """
        if self.sound_on:
            # Initialize GTTS with text, language, voice, and speed
            #tts = gTTS(text= self.chatbot_response, lang='en', tld='com', slow=False, lang_check=False)

            # Save audio file
            #tts.save('audio.mp3')

            # Load audio file
            #audio = AudioSegment.from_file('audio.mp3', format='mp3')

            # Increase playback speed
            #faster_audio = audio.speedup(playback_speed=1.2)

            # Save faster audio file
            #faster_audio.export('faster_audio.mp3', format='mp3')

            # Play faster audio file
            #os.system("audio.mp3")
            pass


    def start_recording(self):
        pass

    def end_recording(self):
       pass

    def record(self, dt):
        pass

    def voice_to_text(self):
        """
        Translate voice input to text
        """
        """
        # use the AudioFile method to read the audio file
        with sr.AudioFile("output.wav") as source:
            # extract audio data from the file
            audio_data = self.speech_regonizer.record(source)

            # use the recognize_google method to convert speech to text
            text = self.speech_regonizer.recognize_google(audio_data)

        # Add text to the text input field
        self.ids.user_input.text = f"{self.ids.user_input.text}\n {text}."
        """
        pass



class ChatbotSettings(BoxLayout):
    def __init__(self, **kwargs):
        super(ChatbotSettings, self).__init__(**kwargs)


#### History class ############

class HistoryClass(MDBoxLayout):
    """Custom content."""
    first_text = StringProperty()
    second_text = StringProperty()
    def __init__(self, first_text, second_text, **kwargs):
        super(HistoryClass, self).__init__(**kwargs)
        self.first_text = first_text.split(".")[0]
        self.second_text = second_text

###############################

class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class HistoryClass(MDBoxLayout):
    """Custom content."""
    first_text = StringProperty()
    second_text = StringProperty()
    def __init__(self, first_text, second_text, **kwargs):
        super(HistoryClass, self).__init__(**kwargs)
        self.first_text = first_text.split(".")[0]
        self.second_text = second_text


class HistoryScreen(MDScreen):
    def on_enter(self):
        #HistoryPage.update_history()
        """
        Remove all old widgets and adds latest history to the app
        """
        self.ids.box.clear_widgets()
        file_names = get_text_file_names(PATH_TO_HISTORY)
        
        for name in file_names:
            # retrieve file content
            content = read_text_file(f"{PATH_TO_HISTORY}/{name}")

            temp_content = HistoryClass(
                first_text=name, second_text=content
            )

            self.ids.box.add_widget(
                MDExpansionPanel(
                    content=temp_content,
                    panel_cls=MDExpansionPanelOneLine(
                        text=name,
                    ),
                )
            )

class PersonalityScreen(MDScreen):
    personality_profile = StringProperty()

    def update_personality_profile(self):
        self.personality_profile = read_text_file(file_path = PATH_TO_PERSONALITY)

    def update_profile(self):
        """
        Update personality profile based on written documents.
        """
        temp_profile = self.ids.personality_profile.text
        overwrite_text_file(path = PATH_TO_PERSONALITY,
                            text = temp_profile)

    def on_enter(self):
        #HistoryPage.update_history()
        """
        Read updated personality profile
        """
        self.update_personality_profile()



class PromptScreen(MDScreen):
    system_prompt = StringProperty()
    summary_prompt = StringProperty()
    storage_prompt = StringProperty()

    def read_prompts(self):
        # Load prompts
        self.system_prompt = read_text_file(file_path = PATH_TO_SYSTEM_PROMPT)
        self.summary_prompt = read_text_file(file_path = PATH_TO_SUMMARY_PROMPT)
        self.storage_prompt = read_text_file(file_path = PATH_TO_STORAGE_PROMPT)

    def update_prompts(self):
        """
        Update prompts based on written input.
        """
        # Update system prompt
        temp_system_prompt = self.ids.system_prompt.text
        overwrite_text_file(path = PATH_TO_SYSTEM_PROMPT,
                            text = temp_system_prompt)
        
        # Update system prompt
        temp_summary_prompt = self.ids.summary_prompt.text
        overwrite_text_file(path = PATH_TO_SUMMARY_PROMPT,
                            text = temp_summary_prompt)
        
        # Update storage prompt
        temp_storage_prompt = self.ids.storage_prompt.text
        overwrite_text_file(path = PATH_TO_STORAGE_PROMPT,
                            text = temp_storage_prompt)

    def on_enter(self):
        #HistoryPage.update_history()
        """
        Read the prompts
        """
        self.read_prompts()


class ApiScreen(MDScreen):
    api_key = StringProperty()

    def read_api_key(self):
        # Load prompts
        self.api_key = read_text_file(file_path = PATH_TO_API_KEY)

    def update_prompts(self):
        """
        Update prompts based on written input.
        """
        # Update 
        temp_api_key = self.ids.api_key.text
        overwrite_text_file(path = PATH_TO_API_KEY,
                            text = temp_api_key)
        

    def on_enter(self):
        """
        Read the API key
        """
        self.read_api_key()


class Example(MDApp):
            
    def build(self):
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)
    
    



Example().run()














