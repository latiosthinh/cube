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
        self.root.bind("<Key>", self.on_key_press)
        self.root.bind("<Alt-c>", self.on_alt_c)
        self.root.bind("<Alt-C>", self.on_alt_c)
        
        # Interaction state
        self.running = False
        self.click_count = 0
        self.click_timer = None
        self.last_click_time = 0
        self.menu_visible = False
        
        # Bubble system
        self.bubble = BubbleSystem(self.root, self.x, self.y, PET_WIDTH)
        
        # State display cooldown
        self.last_state_display = 0
        self.state_display_cooldown = 8000
        
        # Custom menu frame
        self.menu_frame = None
        
        # Start loops
        self._start_loops()
        
        # Welcome message after 1 second
        self.root.after(1000, lambda: self.bubble.show_bubble('msg_welcome'))
        
        # Force position
        self.root.after(100, self._force_position)
        
        print(f"[PET] Cube pet at bottom-left. x={self.x}, y={self.y}")
        print("Controls: Click cube for menu, 1-4 to select")
    
    def _setup_window(self):
        """Configure window properties"""
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-transparentcolor", "black")
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
    
    def on_alt_c(self, event):
        """Toggle menu with Alt+C"""
        if self.menu_visible:
            self._hide_menu()
        else:
            self.bubble._destroy_bubble()
            self._show_action_menu()
    
    def _show_action_menu(self):
        """Show action menu at top right of cube"""
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
            ("3. Show idea list", self._action_ideas),
            ("4. Terminate", self.on_escape)
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
        menu_height = 150
        menu_x = self.x + PET_WIDTH - (menu_width // 2)
        menu_y = max(10, self.y - menu_height - 10)
        self.menu_frame.geometry(f"{menu_width}x{menu_height}+{menu_x}+{menu_y}")
        
        self.bubble._destroy_bubble()
        self.root.focus_force()
    
    def _hide_menu(self):
        """Hide action menu"""
        self.menu_visible = False
        if self.menu_frame:
            try:
                self.menu_frame.destroy()
            except Exception:
                pass
            self.menu_frame = None
    
    def on_key_press(self, event):
        """Handle keyboard shortcuts"""
        if event.keysym == 'Escape':
            self.on_escape(event)
        elif event.char == '1' and self.menu_visible:
            self._action_pet()
        elif event.char == '2' and self.menu_visible:
            self._action_feed()
        elif event.char == '3' and self.menu_visible:
            self._action_ideas()
        elif event.char == '4' and self.menu_visible:
            self.on_escape(event)
    
    def _action_pet(self):
        """Pet action"""
        self._hide_menu()
        self.on_left_click(None)
    
    def _action_feed(self):
        """Feed action"""
        self._hide_menu()
        self.on_right_click(None)
    
    def _action_ideas(self):
        """Show idea list"""
        self._hide_menu()
        ideas = [
            "Build a sandcastle",
            "Learn Python",
            "Watch the sunset",
            "Read a book",
            "Take a nap"
        ]
        idea = random.choice(ideas)
        self.bubble.show_bubble(f"Idea: {idea}")
    
    def _start_loops(self):
        """Start all background loops"""
        self.animate()
        self.update_stats()
        self.auto_save()
        self.state_display_loop()
        self.keep_on_top()
    
    def _force_position(self):
        """Ensure window stays at bottom-left"""
        self.root.geometry(f"{PET_WIDTH}x{PET_HEIGHT}+{self.x}+{self.y}")
    
    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================
    
    def on_left_click(self, event=None):
        """Handle left click - show action menu"""
        if self.menu_visible:
            self._hide_menu()
        else:
            self.bubble._destroy_bubble()
            self._show_action_menu()
    
    def on_right_click(self, event=None):
        """Handle right click - working mode"""
        if self.click_timer:
            self.root.after_cancel(self.click_timer)
        
        if self.state.is_sleeping:
            self.bubble.show_bubble('msg_sleep')
            return
        
        self.state.hunger = max(0, self.state.hunger - 25)
        self.pet.set_animation('working')
        self.bubble.show_bubble('msg_feed')
        
        # Use total_time from registry config, default 5000ms
        working_config = REGISTRY.get('working', {})
        duration = working_config.get('total_time', 5000)
        self.click_timer = self.root.after(duration, lambda: self.pet.set_animation('idle'))
    
    def on_escape(self, event=None):
        """Exit on ESC"""
        self._hide_menu()
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
    
    def state_display_loop(self):
        """Display state-based animations and messages"""
        import time
        current_time = time.time() * 1000
        
        if not self.menu_visible and not self.state.is_sleeping and not self.state.is_eating and self.pet.animation_state == 'idle':
            if current_time - self.last_state_display >= self.state_display_cooldown:
                displayed = False
                if self.state.hunger >= 80:
                    self.pet.set_animation('hungry')
                    self.bubble.show_bubble('hungry', delay=500)
                    self.last_state_display = current_time
                    displayed = True
                elif self.state.happiness >= 90:
                    self.pet.set_animation('happy')
                    self.bubble.show_bubble('happy', delay=500)
                    self.last_state_display = current_time
                    displayed = True
                elif self.state.energy >= 90 and random.random() < 0.3:
                    self.pet.set_animation('aha')
                    self.bubble.show_bubble('aha', delay=500)
                    self.last_state_display = current_time
                    displayed = True
                if displayed:
                    self.root.after(2000, lambda: self.pet.set_animation('idle'))
        self.root.after(3000, self.state_display_loop)
    
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
