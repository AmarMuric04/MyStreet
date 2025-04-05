import json
import threading

import requests
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from session import get_token

API_URL = "http://localhost:5000/posts"  # Change if needed

class PostsScreen(Screen):
    def __init__(self, **kwargs):
        super(PostsScreen, self).__init__(**kwargs)
        # Outer layout for the entire screen
        outer_layout = BoxLayout(orientation="vertical", padding=20, spacing=10)
        self.add_widget(outer_layout)
        
        # Header layout with the Posts title
        header_layout = BoxLayout(size_hint=(1, None), height=50)
        header_label = Label(text="Posts", font_size=24, color="black")
        header_layout.add_widget(header_label)
        outer_layout.add_widget(header_layout)
        
        # Input layout for new post creation
        input_layout = BoxLayout(orientation="vertical", size_hint=(1, None), height=150, spacing=10)
        
        # Title input
        self.title_input = TextInput(hint_text="Enter title", multiline=False, size_hint=(1, None), height=40)
        input_layout.add_widget(self.title_input)
        
        # Text input
        self.text_input = TextInput(hint_text="Enter post text", multiline=True, size_hint=(1, None), height=70)
        input_layout.add_widget(self.text_input)
        
        # Button to post the new post
        self.post_button = Button(text="Submit Post", size_hint=(1, None), height=40)
        self.post_button.bind(on_press=self.create_post)
        input_layout.add_widget(self.post_button)
        
        outer_layout.add_widget(input_layout)
        
        # Content layout that will contain the posts (or a status message)
        self.content_layout = BoxLayout(orientation="vertical")
        outer_layout.add_widget(self.content_layout)
        
        # Status label to show messages such as "Fetching posts..."
        self.status_label = Label(text="Fetching posts...", size_hint=(1, None), height=40)
        self.content_layout.add_widget(self.status_label)
        
        # Schedule fetching posts once the screen is built
        Clock.schedule_once(self.fetch_posts, 0)
    
    def create_post(self, instance):
        title = self.title_input.text.strip()
        text = self.text_input.text.strip()
        if not title or not text:
            self.status_label.text = "Error: Title and text are required."
            return
        
        # Update UI immediately before starting the network request.
        self.post_button.text = "Submitting Post..."
        self.post_button.disabled = True
        
        # Create post payload; image and tags are optional
        post_data = {
            "title": title,
            "text": text,
            "image": None,
            "tags": []
        }
        
        # Offload the network call to a separate thread
        threading.Thread(target=self.create_post_thread, args=(post_data,)).start()
    
    def create_post_thread(self, post_data):
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {get_token()}"
                },
                data=json.dumps(post_data)
            )
            if response.status_code == 201:
                msg = "Post created successfully!"
                # Clear the input fields and refresh posts in the main thread.
                Clock.schedule_once(lambda dt: self.clear_inputs(), 0)
                Clock.schedule_once(lambda dt: self.fetch_posts(0), 0)
            else:
                msg = f"Error creating post: {response.status_code}"
        except Exception as e:
            msg = f"Error: {str(e)}"
        
        # Update the UI with the status message on the main thread.
        Clock.schedule_once(lambda dt: self.update_post_status(msg), 0)
    
    def update_post_status(self, msg):
        self.status_label.text = msg
        self.post_button.text = "Submit Post"
        self.post_button.disabled = False

    def clear_inputs(self):
        self.title_input.text = ""
        self.text_input.text = ""
    
    def fetch_posts(self, dt):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                posts = response.json()
                self.display_posts(posts)
            else:
                self.status_label.text = f"Error fetching posts: {response.status_code}"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
    
    def display_posts(self, posts):
        # Clear the content layout (this will remove the status label)
        self.content_layout.clear_widgets()
        
        # Create a scrollable view to hold posts if there are many.
        scroll = ScrollView(size_hint=(1, 1))
        posts_layout = BoxLayout(orientation="vertical", size_hint_y=None, spacing=10, padding=10)
        posts_layout.bind(minimum_height=posts_layout.setter('height'))
        
        # Iterate through the posts and create a widget for each
        for post in posts:
            post_box = BoxLayout(orientation="vertical", size_hint_y=None, height=100, padding=5, spacing=5)
            
            # Title label with bold text
            title_label = Label(text=post.get("title", "No Title"), bold=True, size_hint_y=None, height=30, color="black")
            # Text label for post content
            text_label = Label(text=post.get("text", "No Content"), size_hint_y=None, height=50, color="black")
            
            post_box.add_widget(title_label)
            post_box.add_widget(text_label)
            posts_layout.add_widget(post_box)
        
        scroll.add_widget(posts_layout)
        self.content_layout.add_widget(scroll)
