"""Pet character sprite rendering and animations"""

import tkinter as tk
from PIL import Image, ImageTk
import random

from config import SCALE_FACTOR, PET_WIDTH, PET_HEIGHT, PET_CENTER_X, PET_CENTER_Y
from messages import MESSAGE_REGISTRY


class PetCharacter(tk.Canvas):
    """Renders the pet sprite with animations"""
    
    def __init__(self, parent, state, width=PET_WIDTH, height=PET_HEIGHT):
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
            self.sprite = self.create_image(PET_CENTER_X, PET_CENTER_Y, image=self.frames['idle'][0])
    
    def _load_sprite(self, pet_type, filename, fallback_to_idle=False):
        """Load a single sprite with fallback to idle_0.png"""
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
        img = Image.new('RGBA', (PET_WIDTH, PET_HEIGHT), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)
        
    def set_animation(self, state):
        """Set current animation state"""
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
