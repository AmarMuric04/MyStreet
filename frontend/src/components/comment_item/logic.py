from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

Builder.load_file("frontend/src/components/comment_item/design.kv")

class CommentItem(MDBoxLayout):
  message = StringProperty()
  username = StringProperty()
  date = StringProperty()
  likes = NumericProperty(0)

  def like():
    pass
  
  def edit():
    pass
  
  def delete():
    pass
  
  def report():
    pass