"""
Taskbar Pet - Cube Desktop Companion
A cute cube pet that lives in your taskbar with interactive animations.
"""

import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw
import random
import json
import os
from datetime import datetime
import tkinter.font as tkfont

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG_FILE = "pet_config.json"
MESSAGE_REGISTRY_FILE = "message_registry.json"
DEFAULT_DISPLAY_TIME = 1500
DEFAULT_FONT_SIZE = 24
SCALE_FACTOR = 0.5

# ============================================================================
# MESSAGE REGISTRY
# ============================================================================

def load_message_registry():
    """Load message registry from JSON file"""
    try:
        with open(MESSAGE_REGISTRY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('messages', {}), data.get('defaults', {}).get('display_time', DEFAULT_DISPLAY_TIME)
    except Exception as e:
        print(f"Error loading message registry: {e}")
        return {}, DEFAULT_DISPLAY_TIME

MESSAGE_REGISTRY, GLOBAL_DEFAULT_DISPLAY_TIME = load_message_registry()

# ============================================================================
# PET STATE
# ============================================================================

class PetState:
    """Manages pet stats and persistence"""
    
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

# ============================================================================
# PET CHARACTER (CANVAS)
# ============================================================================

class PetCharacter(tk.Canvas):
    """Renders the pet sprite with animations"""
    
    def __init__(self, parent, state, width=105, height=78):
        super().__init__(parent, width=width, height=height, bg='black', highlightthickness=0)
        self.state = state
        self.frames = {}
        self.message_frames = {}
        self.current_photo = None
        self.animation_state = 'idle'
        self.frame_index = 0
        self.parent_window = parent
        
        self.load_all_sprites()
        self.set_animation('idle')
        
    def load_all_sprites(self):
        """Load all sprite frames from assets"""
        pet_type = self.state.pet_type
        
        # Base animations
        sprite_configs = {
            'idle': 2,
            'typing': 3,
            'working': 2,
            'error': 3
        }
        
        for anim, count in sprite_configs.items():
            self.frames[anim] = []
            for i in range(count):
                self.frames[anim].append(self._load_sprite(pet_type, f'{anim}_{i}'))
        
        # Message-specific sprites
        for msg_id, config in MESSAGE_REGISTRY.items():
            self.message_frames[msg_id] = []
            for i in range(config["frames"]):
                sprite = self._load_sprite(pet_type, f'{msg_id}_{i}', fallback_to_idle=True)
                self.message_frames[msg_id].append(sprite)
        
        if self.frames['idle']:
            self.sprite = self.create_image(52, 39, image=self.frames['idle'][0])
    
    def _load_sprite(self, pet_type, filename, fallback_to_idle=False):
        """Load a single sprite with fallback"""
        try:
            img = Image.open(f'assets/{pet_type}/{filename}.png')
            if img.width > 0 and img.height > 0:
                new_size = (int(img.width * SCALE_FACTOR), int(img.height * SCALE_FACTOR))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
        except Exception:
            pass
        
        if fallback_to_idle and self.frames.get('idle'):
            return self.frames['idle'][0]
        
        # Create empty placeholder
        img = Image.new('RGBA', (105, 78), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)
        
    def set_animation(self, state):
        if state != self.animation_state:
            self.animation_state = state
            self.frame_index = 0
            
    def update_animation(self):
        """Update sprite frame, return delay until next update"""
        if self.animation_state not in self.frames or not self.frames[self.animation_state]:
            self.animation_state = 'idle'
            
        frames = self.frames[self.animation_state]
        if not frames:
            return 300
            
        # Check for message-specific sprites
        if self.parent_window and hasattr(self.parent_window, 'current_message_id'):
            msg_id = self.parent_window.current_message_id
            if msg_id and msg_id in self.message_frames:
                msg_frames = self.message_frames[msg_id]
                if msg_frames and self.animation_state in ['typing', 'working', 'error']:
                    self.frame_index = (self.frame_index + 1) % len(msg_frames)
                    self.itemconfig(self.sprite, image=msg_frames[self.frame_index])
                    self.current_photo = msg_frames[self.frame_index]
                    return 200
        
        self.itemconfig(self.sprite, image=frames[self.frame_index])
        self.current_photo = frames[self.frame_index]
        
        if self.animation_state == 'idle' and len(frames) > 1:
            self.frame_index = 1 - self.frame_index
            return random.randint(2000, 5000)
        elif self.animation_state in ['working', 'typing', 'error'] and len(frames) > 1:
            self.frame_index = (self.frame_index + 1) % len(frames)
            return 200
        else:
            self.frame_index = (self.frame_index + 1) % len(frames)
            return 400

# ============================================================================
# PET WINDOW (MAIN APP)
# ============================================================================

class PetWindow:
    """Main application window and event handler"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Taskbar Pet")
        
        # Window setup
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        # Screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.taskbar_height = 50
        
        # Load state
        self.state = PetState.load()
        
        # Pet dimensions
        self.pet_width = 105
        self.pet_height = 78
        self.x = 10
        self.y = self.screen_height - self.pet_height - self.taskbar_height - 10
        
        self.root.geometry(f"{self.pet_width}x{self.pet_height}+{self.x}+{self.y}")
        
        # Create pet
        self.pet = PetCharacter(self.root, self.state)
        self.pet.pack()
        
        # Event bindings
        self.pet.bind("<Button-1>", self.on_left_click)
        self.pet.bind("<Button-3>", self.on_right_click)
        self.root.bind("<Escape>", self.on_escape)
        
        # Interaction state
        self.running = False
        self.click_count = 0
        self.click_timer = None
        self.last_click_time = 0
        
        # Bubble state
        self.bubble = None
        self.bubble_label = None
        self.bubble_canvas = None
        self.bubble_photo = None
        self.typing_text = ""
        self.typing_index = 0
        self.typing_timer = None
        self.display_time = DEFAULT_DISPLAY_TIME
        self.on_typing_complete = None
        self.current_message_id = None
        
        # Font
        self.font_path = os.path.join(os.path.dirname(__file__), 'assets', 'font', 'CuteFont-Regular.ttf')
        self.font_size = DEFAULT_FONT_SIZE
        self.pil_font = self._load_font()
        
        # Start loops
        self.animate()
        self.update_stats()
        self.auto_save()
        self.idle_chat_loop()
        self.keep_on_top()
        
        # Welcome message
        self.show_bubble('msg_welcome_01', delay=1000)
        
        # Force position
        self.root.after(100, self._force_position)
        
        print(f"[PET] Cube pet at bottom-left. x={self.x}, y={self.y}")
        print("Controls: Click=Pet, Right-click=Feed, ESC=Exit")
    
    def _load_font(self):
        """Load custom font using PIL"""
        try:
            font = ImageFont.truetype(self.font_path, self.font_size)
            print("[FONT] Loaded Cute Font via PIL")
            return font
        except Exception as e:
            print(f"[FONT] Could not load Cute Font: {e}, using Arial")
            return None
    
    def _force_position(self):
        """Ensure window stays at bottom-left"""
        self.root.geometry(f"{self.pet_width}x{self.pet_height}+{self.x}+{self.y}")
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def on_left_click(self, event):
        """Handle left click - typing mode with messages"""
        import time
        current_time = time.time()
        
        # Spam detection
        if current_time - self.last_click_time < 2.0:
            self.click_count += 1
        else:
            self.click_count = 1
        self.last_click_time = current_time
        
        if self.click_count >= 3:
            self._destroy_bubble()
            if self.click_timer:
                self.root.after_cancel(self.click_timer)
            self.pet.set_animation('error')
            self.click_count = 0
            self.click_timer = self.root.after(5000, lambda: self.pet.set_animation('idle'))
            return
        
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        
        if self.state.is_sleeping:
            self.show_bubble('msg_sleep_01')
            return
        
        self.state.happiness = min(100, self.state.happiness + 8)
        self.state.health = min(100, self.state.health + 2)
        self.pet.set_animation('typing')
        
        msg_ids = [k for k in MESSAGE_REGISTRY.keys() if k.startswith('msg_pet_')]
        msg_id = random.choice(msg_ids)
        self.show_bubble(msg_id, on_typing_complete=lambda: self.pet.set_animation('idle'))
    
    def on_right_click(self, event):
        """Handle right click - working mode for 5 seconds"""
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        
        if self.state.is_sleeping:
            self.show_bubble('msg_sleep_01')
            return
        
        self.state.hunger = max(0, self.state.hunger - 25)
        self.pet.set_animation('working')
        self.show_bubble('msg_feed_01')
        self.click_timer = self.root.after(5000, lambda: self.pet.set_animation('idle'))
    
    def on_escape(self, event):
        """Exit on ESC"""
        self.state.save()
        print("Pet saved. Goodbye!")
        self.root.destroy()
    
    # ========================================================================
    # BUBBLE SYSTEM
    # ========================================================================
    
    def show_bubble(self, message_id_or_text, duration=2000, on_typing_complete=None, delay=0):
        """Show speech bubble with typing effect"""
        if delay > 0:
            self.root.after(delay, lambda: self._show_bubble_impl(message_id_or_text, duration, on_typing_complete))
        else:
            self._show_bubble_impl(message_id_or_text, duration, on_typing_complete)
    
    def _show_bubble_impl(self, message_id_or_text, duration=2000, on_typing_complete=None):
        """Internal bubble display"""
        # Resolve message config
        if message_id_or_text in MESSAGE_REGISTRY:
            msg_id = message_id_or_text
            msg_config = MESSAGE_REGISTRY[message_id_or_text]
            text = msg_config["text"]
            self.display_time = msg_config.get("display_time", GLOBAL_DEFAULT_DISPLAY_TIME)
        else:
            msg_id = None
            text = message_id_or_text
            self.display_time = duration
        
        self._destroy_bubble()
        
        # Create bubble window
        self.bubble = tk.Toplevel(self.root)
        self.bubble.overrideredirect(True)
        self.bubble.wm_attributes("-topmost", True)
        
        bubble_canvas = tk.Canvas(self.bubble, bg='white', highlightthickness=0)
        bubble_canvas.pack(fill='both', expand=True)
        
        self.typing_text = text
        self.typing_index = 0
        self.bubble_canvas = bubble_canvas
        self.on_typing_complete = on_typing_complete
        self.current_message_id = msg_id
        self.bubble_photo = None
        
        self.bubble_label = tk.Label(bubble_canvas, bg='white', padx=12, pady=8)
        self.bubble_label.pack()
        
        bubble_x = self.x + self.pet_width // 2
        bubble_y = self.y - 40
        self.bubble.geometry(f"+{bubble_x}+{bubble_y}")
        
        self.bubble.after(10, lambda: self._draw_rounded_border(bubble_canvas, 100, 50))
        self._type_next_char()
    
    def _type_next_char(self):
        """Type next character with effect"""
        if self.typing_index < len(self.typing_text):
            current_text = self.typing_text[:self.typing_index + 1]
            
            if self.pil_font:
                bbox = self.pil_font.getbbox(current_text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                text_img = Image.new('RGBA', (text_width + 24, text_height + 16), (255, 255, 255, 0))
                draw = ImageDraw.Draw(text_img)
                draw.text((12, 8), current_text, font=self.pil_font, fill=(0, 0, 0, 255))
                
                self.bubble_photo = ImageTk.PhotoImage(text_img)
                self.bubble_label.configure(image=self.bubble_photo, text="")
            else:
                self.bubble_label.configure(text=current_text, image="")
            
            self.typing_index += 1
            self.bubble.update_idletasks()
            
            label_width = self.bubble_label.winfo_reqwidth()
            label_height = self.bubble_label.winfo_reqheight()
            
            self._draw_rounded_border(self.bubble_canvas, label_width, label_height)
            
            bubble_x = self.x + (self.pet_width - label_width) // 2 + 30
            bubble_y = self.y - label_height - 10
            self.bubble.geometry(f"+{bubble_x}+{bubble_y}")
            
            self.typing_timer = self.root.after(80, lambda: self._type_next_char())
        else:
            if self.on_typing_complete:
                self.on_typing_complete()
                self.on_typing_complete = None
            self.typing_timer = self.root.after(self.display_time, lambda: self._destroy_bubble())
    
    def _destroy_bubble(self):
        """Clean up bubble"""
        if self.typing_timer:
            try:
                self.root.after_cancel(self.typing_timer)
                self.typing_timer = None
            except:
                pass
        
        if self.bubble:
            try:
                self.bubble.destroy()
                self.bubble = None
                self.bubble_label = None
                self.bubble_canvas = None
                self.bubble_photo = None
            except:
                pass
        
        self.typing_text = ""
        self.typing_index = 0
        self.on_typing_complete = None
        self.current_message_id = None
    
    def _draw_rounded_border(self, canvas, width, height):
        """Draw rounded rectangle border"""
        if width < 10 or height < 10:
            return
        
        radius = 10
        canvas.delete("border")
        
        # Corners
        canvas.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, outline='#cccccc', width=2, tags="border")
        canvas.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, outline='#cccccc', width=2, tags="border")
        canvas.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, outline='#cccccc', width=2, tags="border")
        canvas.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, outline='#cccccc', width=2, tags="border")
        
        # Edges
        canvas.create_line(radius, 0, width-radius, 0, fill='#cccccc', width=2, tags="border")
        canvas.create_line(width, radius, width, height-radius, fill='#cccccc', width=2, tags="border")
        canvas.create_line(radius, height, width-radius, height, fill='#cccccc', width=2, tags="border")
        canvas.create_line(0, radius, 0, height-radius, fill='#cccccc', width=2, tags="border")
    
    # ========================================================================
    # LOOPS
    # ========================================================================
    
    def animate(self):
        """Animation loop"""
        delay = self.pet.update_animation()
        self.root.after(delay, self.animate)
    
    def update_stats(self):
        """Update pet stats over time"""
        if not self.state.is_eating:
            self.state.hunger = min(100, self.state.hunger + 0.5)
            self.state.energy = max(0, self.state.energy - 0.3)
            self.state.age += 0.1
        self.root.after(1000, self.update_stats)
    
    def auto_save(self):
        """Auto-save every 30 seconds"""
        self.state.save()
        self.root.after(30000, self.auto_save)
    
    def idle_chat_loop(self):
        """Show random chat during idle"""
        if self.pet.animation_state == 'idle' and not self.state.is_sleeping and not self.state.is_eating:
            phrases = [k for k in MESSAGE_REGISTRY.keys() if k.startswith('msg_pet_')]
            if phrases:
                self.show_bubble(random.choice(phrases), delay=random.randint(5000, 10000))
        self.root.after(random.randint(15000, 30000), self.idle_chat_loop)
    
    def keep_on_top(self):
        """Keep window always on top"""
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.after(500, self.keep_on_top)
    
    def run(self):
        """Start the pet"""
        self.running = True
        self.root.mainloop()

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("Taskbar Pet - Cube Edition")
    pet = PetWindow()
    pet.run()
