"""Taskbar Pet - Cube Desktop Companion"""

import tkinter as tk
import random
import time

from config import (
    PET_WIDTH, PET_HEIGHT, TASKBAR_HEIGHT, PET_X,
    SPAM_CLICK_THRESHOLD, SPAM_CLICK_WINDOW, SPAM_ERROR_DURATION,
    AUTO_SAVE_INTERVAL, IDLE_CHAT_DELAY_MIN, IDLE_CHAT_DELAY_MAX, KEEP_ON_TOP_INTERVAL
)
from state import PetState
from pet import PetCharacter
from bubble import BubbleSystem
from messages import REGISTRY, DEFAULTS


class PetWindow:
    """Main application window and event handler"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Taskbar Pet")
        
        self._setup_window()
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        self.state = PetState.load()
        
        self.x = PET_X
        self.y = self.screen_height - PET_HEIGHT - TASKBAR_HEIGHT - 10
        
        self.root.geometry(f"{PET_WIDTH}x{PET_HEIGHT}+{self.x}+{self.y}")
        
        self.pet = PetCharacter(self.root, self.state)
        self.pet.pack()
        
        self.pet.bind("<Button-1>", self.on_left_click)
        self.pet.bind("<Button-3>", self.on_right_click)
        self.root.bind("<Escape>", self.on_escape)
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<Alt-c>", self.on_alt_c)
        self.root.bind("<Alt-C>", self.on_alt_c)
        
        self.running = False
        self.menu_visible = False
        self.welcome_done = False
        self.is_hungry_persistent = False
        self.current_mode = 'idle'
        self.idle_text_timer = None
        self.state_cycle_timer = None
        
        self.bubble = BubbleSystem(self.root, self.x, self.y, PET_WIDTH)
        
        self.menu_frame = None
        
        self.animate()
        self.update_stats()
        self.auto_save()
        self.keep_on_top()
        
        self.root.after(1000, self._show_welcome)
        self.root.after(100, self._force_position)
        
        print(f"[PET] Cube pet at bottom-left. x={self.x}, y={self.y}")
        print("Controls: Click=menu, Right-click=random mode, 1-5 to select")
    
    def _setup_window(self):
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
    
    def _show_welcome(self):
        self.bubble.show_bubble('msg_welcome')
        self.welcome_done = True
        self.root.after(2000, self._start_idle_mode)
    
    def _start_idle_mode(self):
        self.current_mode = 'idle'
        self.pet.set_animation('idle')
        self._idle_text_loop()
        self._random_state_loop()
    
    def _idle_text_loop(self):
        if self.current_mode == 'idle' and not self.menu_visible:
            self.bubble.show_bubble('idle')
        delay = random.randint(5000, 10000)
        self.idle_text_timer = self.root.after(delay, self._idle_text_loop)
    
    def _random_state_loop(self):
        if not self.menu_visible and not self.is_hungry_persistent:
            modes = ['idle', 'typing', 'happy', 'hungry']
            mode = random.choice(modes)
            if mode == 'hungry':
                self.is_hungry_persistent = True
            self._trigger_mode(mode)
        delay = random.randint(20000, 30000)
        self.state_cycle_timer = self.root.after(delay, self._random_state_loop)
    
    def _trigger_mode(self, mode, text_key=None, duration=None):
        self.current_mode = mode
        self.pet.set_animation(mode)
        if text_key:
            self.bubble.show_bubble(text_key, delay=500)
        if duration is None:
            duration = random.randint(3000, 5000)
        self.root.after(duration, lambda: self.pet.set_animation('idle'))
    
    def on_alt_c(self, event):
        if self.menu_visible:
            self._hide_menu()
        else:
            self.bubble._destroy_bubble()
            self._show_action_menu()
    
    def _show_action_menu(self):
        self._hide_menu()
        
        self.menu_visible = True
        self.menu_frame = tk.Toplevel(self.root)
        self.menu_frame.overrideredirect(True)
        self.menu_frame.wm_attributes("-topmost", True)
        
        menu_bg = tk.Frame(self.menu_frame, bg='white', relief='solid', borderwidth=1)
        menu_bg.pack(fill='both', expand=True)
        
        items = [
            ("1. Pet", self._action_pet),
            ("2. Feed", self._action_feed),
            ("3. Think", self._action_think),
            ("4. Show idea list", self._action_ideas),
            ("5. Terminate", self.on_escape)
        ]
        
        for text, command in items:
            btn = tk.Button(menu_bg, text=text, bg='white', fg='black', 
                           activebackground='#e0e0e0', activeforeground='black',
                           padx=15, pady=5, anchor='w', cursor='hand2',
                           relief='flat', command=command)
            btn.pack(fill='x', padx=2, pady=2)
            btn.bind("<Enter>", lambda e: e.widget.config(bg='#e0e0e0'))
            btn.bind("<Leave>", lambda e: e.widget.config(bg='white'))
        
        menu_width = 150
        menu_height = 180
        menu_x = self.x + PET_WIDTH - (menu_width // 2)
        menu_y = max(10, self.y - menu_height - 20)
        self.menu_frame.geometry(f"{menu_width}x{menu_height}+{menu_x}+{menu_y}")
        
        self.bubble._destroy_bubble()
        self.root.focus_force()
    
    def _hide_menu(self):
        self.menu_visible = False
        if self.menu_frame:
            try:
                self.menu_frame.destroy()
            except Exception:
                pass
            self.menu_frame = None
    
    def on_key_press(self, event):
        if event.keysym == 'Escape':
            self.on_escape(event)
        elif event.char == '1' and self.menu_visible:
            self._action_pet()
        elif event.char == '2' and self.menu_visible:
            self._action_feed()
        elif event.char == '3' and self.menu_visible:
            self._action_think()
        elif event.char == '4' and self.menu_visible:
            self._action_ideas()
        elif event.char == '5' and self.menu_visible:
            self.on_escape(event)
    
    def _action_pet(self):
        self._hide_menu()
        self.is_hungry_persistent = False
        self._trigger_mode('happy', 'happy')
    
    def _action_feed(self):
        self._hide_menu()
        self.state.hunger = max(0, self.state.hunger - 25)
        self.is_hungry_persistent = False
        self._trigger_mode('happy', 'happy')
    
    def _action_think(self):
        self._hide_menu()
        self._trigger_mode('working', 'working')
        self.root.after(3000, lambda: self._trigger_mode('aha', 'aha'))
    
    def _action_ideas(self):
        self._hide_menu()
        self._trigger_mode('working', 'working')
        ideas = ["Build a sandcastle", "Learn Python", "Watch the sunset", "Read a book", "Take a nap"]
        self.root.after(2000, lambda: self.bubble.show_bubble(f"Idea: {random.choice(ideas)}"))
    
    def on_left_click(self, event=None):
        if self.menu_visible:
            self._hide_menu()
        else:
            self.bubble._destroy_bubble()
            self._show_action_menu()
    
    def on_right_click(self, event=None):
        """Right click - immediately change to random mode"""
        self.bubble._destroy_bubble()
        modes = ['typing', 'happy', 'hungry', 'aha', 'working']
        mode = random.choice(modes)
        if mode == 'hungry':
            self.is_hungry_persistent = True
        self._trigger_mode(mode, mode)
    
    def on_escape(self, event=None):
        self._hide_menu()
        self.state.save()
        print("Pet saved. Goodbye!")
        self.root.destroy()
    
    def animate(self):
        delay = self.pet.update_animation()
        self.root.after(delay, self.animate)
    
    def update_stats(self):
        if not self.state.is_eating:
            self.state.hunger = min(100, self.state.hunger + 0.5)
            self.state.energy = max(0, self.state.energy - 0.3)
            self.state.age += 0.1
        self.root.after(1000, self.update_stats)
    
    def auto_save(self):
        self.state.save()
        self.root.after(AUTO_SAVE_INTERVAL, self.auto_save)
    
    def _force_position(self):
        self.root.geometry(f"{PET_WIDTH}x{PET_HEIGHT}+{self.x}+{self.y}")
    
    def keep_on_top(self):
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.after(KEEP_ON_TOP_INTERVAL, self.keep_on_top)
    
    def run(self):
        self.running = True
        self.root.mainloop()


if __name__ == "__main__":
    print("Taskbar Pet - Cube Edition")
    pet = PetWindow()
    pet.run()
