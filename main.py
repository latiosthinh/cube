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
        
        # Window setup
        self._setup_window()
        
        # Screen dimensions
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Load state
        self.state = PetState.load()
        
        # Position
        self.x = PET_X
        self.y = self.screen_height - PET_HEIGHT - TASKBAR_HEIGHT - 10
        
        self.root.geometry(f"{PET_WIDTH}x{PET_HEIGHT}+{self.x}+{self.y}")
        
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
        
        # Bubble system
        self.bubble = BubbleSystem(self.root, self.x, self.y, PET_WIDTH)
        
        # Start loops
        self._start_loops()
        
        # Welcome message
        self.bubble.show_bubble('msg_welcome_01', delay=1000)
        
        # Force position
        self.root.after(100, self._force_position)
        
        print(f"[PET] Cube pet at bottom-left. x={self.x}, y={self.y}")
        print("Controls: Click=Pet, Right-click=Feed, ESC=Exit")
    
    def _setup_window(self):
        """Configure window properties"""
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
    
    def _start_loops(self):
        """Start all background loops"""
        self.animate()
        self.update_stats()
        self.auto_save()
        self.idle_chat_loop()
        self.keep_on_top()
    
    def _force_position(self):
        """Ensure window stays at bottom-left"""
        self.root.geometry(f"{PET_WIDTH}x{PET_HEIGHT}+{self.x}+{self.y}")
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def on_left_click(self, event):
        """Handle left click - typing mode with messages"""
        current_time = time.time()
        
        # Spam detection
        if current_time - self.last_click_time < SPAM_CLICK_WINDOW:
            self.click_count += 1
        else:
            self.click_count = 1
        self.last_click_time = current_time
        
        if self.click_count >= SPAM_CLICK_THRESHOLD:
            self.bubble._destroy_bubble()
            if self.click_timer:
                self.root.after_cancel(self.click_timer)
            self.pet.set_animation('error')
            self.click_count = 0
            
            # Use total_time from registry config
            error_config = REGISTRY.get('error', {})
            duration = error_config.get('total_time', 5000)
            self.click_timer = self.root.after(duration, lambda: self.pet.set_animation('idle'))
            return
        
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        
        if self.state.is_sleeping:
            self.bubble.show_bubble('msg_sleep_01')
            return
        
        self.state.happiness = min(100, self.state.happiness + 8)
        self.state.health = min(100, self.state.health + 2)
        self.pet.set_animation('typing')
        
        msg_ids = [k for k in REGISTRY.keys() if k.startswith('msg_pet_')]
        msg_id = random.choice(msg_ids)
        self.bubble.show_bubble(msg_id, on_typing_complete=lambda: self.pet.set_animation('idle'))
    
    def on_right_click(self, event):
        """Handle right click - working mode"""
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        
        if self.state.is_sleeping:
            self.bubble.show_bubble('msg_sleep_01')
            return
        
        self.state.hunger = max(0, self.state.hunger - 25)
        self.pet.set_animation('working')
        self.bubble.show_bubble('msg_feed_01')
        
        # Use total_time from registry config, default 5000ms
        working_config = REGISTRY.get('working', {})
        duration = working_config.get('total_time', 5000)
        self.click_timer = self.root.after(duration, lambda: self.pet.set_animation('idle'))
    
    def on_escape(self, event):
        """Exit on ESC"""
        self.state.save()
        print("Pet saved. Goodbye!")
        self.root.destroy()
    
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
        self.root.after(AUTO_SAVE_INTERVAL, self.auto_save)
    
    def idle_chat_loop(self):
        """Show random chat during idle"""
        if self.pet.animation_state == 'idle' and not self.state.is_sleeping and not self.state.is_eating:
            phrases = [k for k in REGISTRY.keys() if k.startswith('msg_pet_')]
            if phrases:
                self.bubble.show_bubble(random.choice(phrases), delay=random.randint(IDLE_CHAT_DELAY_MIN, IDLE_CHAT_DELAY_MAX))
        self.root.after(random.randint(IDLE_CHAT_DELAY_MIN, IDLE_CHAT_DELAY_MAX), self.idle_chat_loop)
    
    def keep_on_top(self):
        """Keep window always on top"""
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.after(KEEP_ON_TOP_INTERVAL, self.keep_on_top)
    
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
