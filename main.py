from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.core.window import Window
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path
import os
import cv2
import numpy as np
from jnius import autoclass, cast
import threading
from pathlib import Path
import mimetypes

# Android imports
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Uri = autoclass('android.net.Uri')
DocumentFile = autoclass('androidx.documentfile.provider.DocumentFile')
Environment = autoclass('android.os.Environment')
Settings = autoclass('android.provider.Settings')
Build = autoclass('android.os.Build')

class FileCard(BoxLayout):
    def __init__(self, file_path, file_name, file_type, callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 120
        self.padding = 10
        self.spacing = 5
        self.file_path = file_path
        self.file_type = file_type
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Icon based on file type
        icon_text = "📄"
        if file_type == "image":
            icon_text = "🖼️"
        elif file_type == "video":
            icon_text = "🎬"
        elif file_type == "ppt":
            icon_text = "📊"
        elif file_type == "pdf":
            icon_text = "📕"
        
        icon_label = Label(text=icon_text, font_size='40sp', size_hint_y=0.6)
        name_label = Label(text=file_name[:30], font_size='12sp', size_hint_y=0.4, color=(0.2, 0.2, 0.2, 1))
        
        self.add_widget(icon_label)
        self.add_widget(name_label)
        
        self.bind(on_touch_down=self.on_card_touch)
        self.callback = callback
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_card_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            # Touch effect
            anim = Animation(height=110, duration=0.1) + Animation(height=120, duration=0.1)
            anim.start(self)
            self.callback(self.file_path, self.file_type)
            return True


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Header
        header = BoxLayout(size_hint_y=0.15, padding=[0, 10])
        title = Label(text='FileGlance', font_size='28sp', bold=True, color=(0.2, 0.2, 0.2, 1))
        header.add_widget(title)
        
        # AutoGlance Toggle
        toggle_box = BoxLayout(size_hint_y=0.1, spacing=10)
        toggle_label = Label(text='AutoGlance:', size_hint_x=0.6, color=(0.3, 0.3, 0.3, 1))
        self.auto_toggle = ToggleButton(text='OFF', size_hint_x=0.4, background_normal='', background_color=(0.7, 0.7, 0.7, 1))
        self.auto_toggle.bind(on_press=self.toggle_autoglance)
        toggle_box.add_widget(toggle_label)
        toggle_box.add_widget(self.auto_toggle)
        
        # Category buttons
        categories = [
            ('Images', 'image'),
            ('Videos', 'video'),
            ('PDFs', 'pdf'),
            ('Presentations', 'ppt')
        ]
        
        buttons_layout = GridLayout(cols=2, spacing=15, size_hint_y=0.6)
        
        for cat_name, cat_type in categories:
            btn = Button(
                text=cat_name,
                background_normal='',
                background_color=(0.3, 0.5, 0.7, 1),
                color=(1, 1, 1, 1),
                font_size='18sp'
            )
            btn.bind(on_press=lambda x, ct=cat_type: self.show_category(ct))
            buttons_layout.add_widget(btn)
        
        layout.add_widget(header)
        layout.add_widget(toggle_box)
        layout.add_widget(buttons_layout)
        
        self.add_widget(layout)
    
    def toggle_autoglance(self, instance):
        if instance.state == 'down':
            instance.text = 'ON'
            instance.background_color = (0.2, 0.7, 0.3, 1)
            App.get_running_app().autoglance_enabled = True
            App.get_running_app().start_camera_detection()
        else:
            instance.text = 'OFF'
            instance.background_color = (0.7, 0.7, 0.7, 1)
            App.get_running_app().autoglance_enabled = False
            App.get_running_app().stop_camera_detection()
    
    def show_category(self, category):
        App.get_running_app().current_category = category
        self.manager.current = 'files'
        self.manager.get_screen('files').load_files(category)


class FilesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'files'
        
        layout = BoxLayout(orientation='vertical')
        
        # Header with back button
        header = BoxLayout(size_hint_y=0.1, padding=10)
        back_btn = Button(text='← Back', size_hint_x=0.3, background_normal='', background_color=(0.5, 0.5, 0.5, 1))
        back_btn.bind(on_press=self.go_back)
        self.category_label = Label(text='Files', font_size='22sp', bold=True, color=(0.2, 0.2, 0.2, 1))
        header.add_widget(back_btn)
        header.add_widget(self.category_label)
        
        # Scrollable file list
        self.scroll = ScrollView()
        self.file_grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=10)
        self.file_grid.bind(minimum_height=self.file_grid.setter('height'))
        self.scroll.add_widget(self.file_grid)
        
        layout.add_widget(header)
        layout.add_widget(self.scroll)
        self.add_widget(layout)
    
    def load_files(self, category):
        self.file_grid.clear_widgets()
        self.category_label.text = category.capitalize()
        
        files = App.get_running_app().get_files_by_type(category)
        
        if not files:
            no_files = Label(text=f'No {category} files found', color=(0.5, 0.5, 0.5, 1))
            self.file_grid.add_widget(no_files)
        else:
            for file_path in files:
                file_name = os.path.basename(file_path)
                card = FileCard(file_path, file_name, category, self.open_file)
                self.file_grid.add_widget(card)
    
    def open_file(self, file_path, file_type):
        App.get_running_app().open_file(file_path, file_type)
    
    def go_back(self, instance):
        self.manager.current = 'home'


class FileGlanceApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.autoglance_enabled = False
        self.current_category = None
        self.face_cascade = None
        self.camera_thread = None
        self.camera_running = False
        self.current_rotation = 0
        self.current_file_widget = None
        
    def build(self):
        Window.clearcolor = (0.98, 0.98, 0.98, 1)
        
        # Request permissions
        self.request_storage_permissions()
        
        # Initialize face detection
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except:
            print("Face cascade not loaded")
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen())
        sm.add_widget(FilesScreen())
        
        return sm
    
    def request_storage_permissions(self):
        permissions = [
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.CAMERA
        ]
        
        if Build.VERSION.SDK_INT >= 30:
            # Android 11+
            try:
                if not Environment.isExternalStorageManager():
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                    uri = Uri.parse("package:" + PythonActivity.mActivity.getPackageName())
                    intent.setData(uri)
                    PythonActivity.mActivity.startActivity(intent)
            except:
                pass
        
        request_permissions(permissions)
    
    def get_files_by_type(self, file_type):
        files = []
        extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'video': ['.mp4', '.avi', '.mkv', '.mov', '.3gp', '.flv'],
            'pdf': ['.pdf'],
            'ppt': ['.ppt', '.pptx']
        }
        
        try:
            storage_path = primary_external_storage_path()
            for root, dirs, filenames in os.walk(storage_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in filenames:
                    if any(filename.lower().endswith(ext) for ext in extensions.get(file_type, [])):
                        files.append(os.path.join(root, filename))
                
                # Limit search depth
                if len(files) > 200:
                    break
        except Exception as e:
            print(f"Error scanning files: {e}")
        
        return files[:200]  # Limit to 200 files for performance
    
    def open_file(self, file_path, file_type):
        try:
            # Use Android Intent to open files
            intent = Intent(Intent.ACTION_VIEW)
            uri = Uri.parse("file://" + file_path)
            
            mime_type = mimetypes.guess_type(file_path)[0]
            if mime_type:
                intent.setDataAndType(uri, mime_type)
            else:
                intent.setData(uri)
            
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            PythonActivity.mActivity.startActivity(intent)
            
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f'Could not open file:\n{str(e)}'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
    
    def start_camera_detection(self):
        if not self.camera_running:
            self.camera_running = True
            self.camera_thread = threading.Thread(target=self.detect_faces)
            self.camera_thread.daemon = True
            self.camera_thread.start()
    
    def stop_camera_detection(self):
        self.camera_running = False
    
    def detect_faces(self):
        try:
            cap = cv2.VideoCapture(1)  # Front camera
            
            while self.camera_running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) > 1:
                    Clock.schedule_once(lambda dt: self.show_multiple_faces_warning())
                elif len(faces) == 1:
                    x, y, w, h = faces[0]
                    face_center_x = x + w // 2
                    frame_center_x = frame.shape[1] // 2
                    
                    # Calculate rotation based on face position
                    offset = face_center_x - frame_center_x
                    
                    if offset < -100:
                        target_rotation = -90
                    elif offset > 100:
                        target_rotation = 90
                    elif offset < -50:
                        target_rotation = -45
                    elif offset > 50:
                        target_rotation = 45
                    else:
                        target_rotation = 0
                    
                    if target_rotation != self.current_rotation:
                        self.current_rotation = target_rotation
                        Clock.schedule_once(lambda dt: self.rotate_content(target_rotation))
                
                Clock.schedule_once(lambda dt: None, 0.1)
            
            cap.release()
        except Exception as e:
            print(f"Camera error: {e}")
    
    def rotate_content(self, angle):
        if self.current_file_widget:
            anim = Animation(rotation=angle, duration=0.3, t='in_out_cubic')
            anim.start(self.current_file_widget)
    
    def show_multiple_faces_warning(self):
        if self.autoglance_enabled:
            popup = Popup(
                title='Multiple Faces Detected',
                content=Label(text='More faces detected,\nplease turn off the toggle'),
                size_hint=(0.7, 0.3),
                auto_dismiss=True
            )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)


if __name__ == '__main__':
    FileGlanceApp().run()
