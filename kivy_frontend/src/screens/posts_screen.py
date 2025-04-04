import requests
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView


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
        
        # Content layout that will contain the posts (or a status message)
        self.content_layout = BoxLayout(orientation="vertical")
        outer_layout.add_widget(self.content_layout)
        
        # Status label to show messages such as "Fetching posts..."
        self.status_label = Label(text="Fetching posts...", size_hint=(1, None), height=40)
        self.content_layout.add_widget(self.status_label)
        
        # Schedule fetching posts once the screen is built
        Clock.schedule_once(self.fetch_posts, 0)

    def fetch_posts(self, dt):
        try:
            # Change the URL if needed to match your Flask server
            response = requests.get("http://localhost:5000/posts")
            if response.status_code == 200:
                posts = response.json()
                # self.display_posts(posts)
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
            title_label = Label(text=post.get("title", "No Title"), bold=True, size_hint_y=None, height=30)
            # Text label for post content
            text_label = Label(text=post.get("text", "No Content"), size_hint_y=None, height=50)
            
            post_box.add_widget(title_label)
            post_box.add_widget(text_label)
            posts_layout.add_widget(post_box)
        
        scroll.add_widget(posts_layout)
        self.content_layout.add_widget(scroll)
