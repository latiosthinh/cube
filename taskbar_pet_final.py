"""
Taskbar Pet Pro - Final version with working interactions
"""

import tkinter as tk
from PIL import Image, ImageTk
import random
import json
import os
from datetime import datetime

CONFIG_FILE = "pet_config.json"

class PetState:
    def __init__(self):
        self.hunger = 50
        self.happiness = 70
        self.energy = 80
        self.health = 100
        self.age = 0
        self.is_sleeping = False
        self.is_eating = False
        self.last_fed = datetime.now()
        self.pet_type = "cube"
        self.position_x = 0
        self.name = ""
        
    def save(self, filename=CONFIG_FILE):
        data = {
            'hunger': self.hunger,
            'happiness': self.happiness,
            'energy': self.energy,
            'health': self.health,
            'age': self.age,
            'is_sleeping': self.is_sleeping,
            'is_eating': self.is_eating,
            'last_fed': self.last_fed.isoformat(),
            'pet_type': self.pet_type,
            'position_x': self.position_x,
            'name': self.name
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filename=CONFIG_FILE):
        state = cls()
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                state.hunger = data.get('hunger', 50)
                state.happiness = data.get('happiness', 70)
                state.energy = data.get('energy', 80)
                state.health = data.get('health', 100)
                state.age = data.get('age', 0)
                state.is_sleeping = data.get('is_sleeping', False)
                state.is_eating = data.get('is_eating', False)
                if 'last_fed' in data:
                    state.last_fed = datetime.fromisoformat(data['last_fed'])
                state.pet_type = data.get('pet_type', 'cube')
                state.position_x = data.get('position_x', 0)
                state.name = data.get('name', '')
                
                hours_passed = (datetime.now() - state.last_fed).total_seconds() / 3600
                state.hunger = min(100, state.hunger + int(hours_passed * 10))
                state.energy = max(0, state.energy - int(hours_passed * 5))
            except Exception as e:
                print(f"Error loading save: {e}")
        return state

class PetCharacter(tk.Canvas):
    def __init__(self, parent, state, width=105, height=78):
        super().__init__(parent, width=width, height=height, bg='black', highlightthickness=0)
        self.state = state
        self.frames = {}
        self.current_photo = None
        self.animation_state = 'idle'
        self.frame_index = 0
        
        self.load_all_sprites()
        self.set_animation('idle')
        
    def load_all_sprites(self):
        pet_type = self.state.pet_type
        self.frames = {
            'idle': [],
            'typing': [],
            'working': [],
            'error': []
        }
        
        sprite_configs = {
            'idle': 2,
            'typing': 3,
            'working': 2,
            'error': 3
        }
        
        scale_factor = 0.5
        
        for anim, count in sprite_configs.items():
            for i in range(count):
                try:
                    img = Image.open(f'assets/{pet_type}/{anim}_{i}.png')
                    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.frames[anim].append(photo)
                except FileNotFoundError as e:
                    print(f"Sprite not found: assets/{pet_type}/{anim}_{i}.png")
                    img = Image.new('RGBA', (105, 78), (0, 0, 0, 0))
                    photo = ImageTk.PhotoImage(img)
                    self.frames[anim].append(photo)
        
        if self.frames['idle']:
            self.sprite = self.create_image(52, 39, image=self.frames['idle'][0])
            print(f"[PET] Loaded {len(self.frames['idle'])} idle frames")
        
    def set_animation(self, state):
        if state != self.animation_state:
            self.animation_state = state
            self.frame_index = 0
            
    def update_animation(self):
        if self.animation_state not in self.frames or not self.frames[self.animation_state]:
            self.animation_state = 'idle'
            
        frames = self.frames[self.animation_state]
        if not frames:
            return 300
            
        self.itemconfig(self.sprite, image=frames[self.frame_index])
        self.current_photo = frames[self.frame_index]
        
        if self.animation_state == 'idle' and len(frames) > 1:
            self.frame_index = 1 - self.frame_index
            print(f"[ANIM] Idle frame: {self.frame_index}")
            return random.randint(2000, 5000)
        else:
            self.frame_index = (self.frame_index + 1) % len(frames)
            return 400

class PetWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Taskbar Pet")
        
        # Key settings
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "black")
        
        # Force always on top
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.taskbar_height = 50
        
        self.state = PetState.load()
        
        self.pet_width = 105
        self.pet_height = 78
        
        self.x = 10
        self.y = self.screen_height - self.pet_height - self.taskbar_height + 40
        
        # Create pet as Canvas (better event handling than Label)
        self.pet = PetCharacter(self.root, self.state)
        self.pet.pack()
        
        # Set position after packing
        self.root.geometry(f"{self.pet_width}x{self.pet_height}+{self.x}+{self.y}")
        
        # Make canvas clickable
        self.pet.bind("<Button-1>", self.on_left_click)
        self.pet.bind("<Button-3>", self.on_right_click)
        self.pet.bind("<Enter>", self.on_mouse_enter)
        self.pet.bind("<Leave>", self.on_mouse_leave)
        
        # Bind keyboard to root
        self.root.bind("<Escape>", self.on_escape)
        
        # Movement
        self.running = False
        
        # Speech bubble
        self.bubble = None
        
        # Start loops
        self.animate()
        self.update_stats()
        self.auto_save()
        self.idle_chat_loop()
        self.keep_on_top()
        
        pet_name = self.state.name if self.state.name else self.state.pet_type.title()
        self.root.after(1000, lambda: self.show_bubble(f"Hi! I'm {pet_name}!"))
        
        # Force position after window is shown
        self.root.after(100, self._force_position)
        
        print(f"[PET] Cube pet at bottom-left. x={self.x}, y={self.y}")
        print("Controls: Click=Pet, Right-click=Feed, ESC=Exit")
        
    def _force_position(self):
        """Ensure window stays at bottom-left"""
        self.root.geometry(f"{self.pet_width}x{self.pet_height}+{self.x}+{self.y}")
        
    def on_left_click(self, event):
        """Pet the pet"""
        print("Left click detected!")
        if self.state.is_sleeping:
            self.show_bubble("Zzz...")
            return
            
        self.state.happiness = min(100, self.state.happiness + 8)
        self.state.health = min(100, self.state.health + 2)
        self.pet.set_animation('working')
        self.show_bubble("<3")
        self.root.after(1000, lambda: self.pet.set_animation('idle'))
        
    def on_right_click(self, event):
        """Feed the pet"""
        print("Right click detected!")
        if self.state.is_sleeping:
            self.show_bubble("Zzz...")
            return
            
        self.state.hunger = max(0, self.state.hunger - 25)
        self.pet.set_animation('typing')
        self.show_bubble("YUM!")
        self.root.after(2000, lambda: self.pet.set_animation('idle'))
        
    def on_mouse_enter(self, event):
        """Mouse entered pet area"""
        pass
        
    def on_mouse_leave(self, event):
        """Mouse left pet area"""
        pass
        
    def on_escape(self, event):
        """Exit on ESC"""
        self.state.save()
        print("Pet saved. Goodbye!")
        self.root.destroy()
        
    def show_bubble(self, text, duration=2000):
        """Show speech bubble"""
        if self.bubble:
            try:
                self.bubble.destroy()
            except:
                pass
                
        self.bubble = tk.Toplevel(self.root)
        self.bubble.overrideredirect(True)
        self.bubble.wm_attributes("-topmost", True)
        self.bubble.wm_attributes("-transparentcolor", "black")
        
        label = tk.Label(
            self.bubble,
            text=text,
            bg="black",
            fg="white",
            font=("Arial", 14, "bold"),
            padx=10,
            pady=5
        )
        label.pack()
        
        bubble_x = self.x + self.pet_width // 2
        bubble_y = self.y - 40
        self.bubble.geometry(f"+{bubble_x}+{bubble_y}")
        
        self.root.after(duration, lambda: self._destroy_bubble())
        
    def _destroy_bubble(self):
        """Safely destroy bubble"""
        if self.bubble:
            try:
                self.bubble.destroy()
                self.bubble = None
            except:
                pass

    def keep_on_top(self):
        """Keep window always on top"""
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.after(500, self.keep_on_top)
                
    def idle_chat_loop(self):
        """Show random chat bubbles during idle"""
        if self.pet.animation_state == 'idle' and not self.state.is_sleeping and not self.state.is_eating:
            phrases = ["Hi!", "Hey there!", "Meet Cube!", "Hello!", "What's up?", "Nice day!", "Working hard!", "Cube life!"]
            phrase = random.choice(phrases)
            self.show_bubble(phrase, duration=random.randint(5000, 10000))
        self.root.after(random.randint(15000, 30000), self.idle_chat_loop)
                
    def animate(self):
        """Animation loop"""
        delay = self.pet.update_animation()
        self.root.after(delay, self.animate)
            
    def update_stats(self):
        """Update pet stats"""
        if not self.state.is_eating:
            self.state.hunger = min(100, self.state.hunger + 0.5)
            self.state.energy = max(0, self.state.energy - 0.3)
            self.state.age += 0.1
            
        self.root.after(1000, self.update_stats)
        
    def auto_save(self):
        """Auto-save every 30 seconds"""
        self.state.save()
        self.root.after(30000, self.auto_save)
        
    def run(self):
        """Start the pet"""
        self.running = True
        self.root.mainloop()

if __name__ == "__main__":
    print("Taskbar Pet Pro - Starting...")
    pet = PetWindow()
    pet.run()
