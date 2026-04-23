"""Speech bubble system with typing effect and custom font"""

import tkinter as tk
from PIL import Image, ImageTk, ImageFont, ImageDraw

from config import (
    DEFAULT_DISPLAY_TIME, FONT_PATH, DEFAULT_FONT_SIZE,
    PET_WIDTH, BUBBLE_PADDING, BUBBLE_BORDER_RADIUS, BUBBLE_BORDER_COLOR, BUBBLE_BORDER_WIDTH
)
from messages import REGISTRY, DEFAULTS


class BubbleSystem:
    """Manages speech bubble display with typing effect"""
    
    def __init__(self, root, pet_x, pet_y, pet_width):
        self.root = root
        self.pet_x = pet_x
        self.pet_y = pet_y
        self.pet_width = pet_width
        
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
        
        # Load font
        self.pil_font = self._load_font()
    
    def _load_font(self):
        """Load custom font using PIL"""
        try:
            font = ImageFont.truetype(FONT_PATH, DEFAULT_FONT_SIZE)
            print("[FONT] Loaded Cute Font via PIL")
            return font
        except Exception as e:
            print(f"[FONT] Could not load Cute Font: {e}, using Arial")
            return None
    
    def show_bubble(self, message_id_or_text, duration=2000, on_typing_complete=None, delay=0):
        """Show speech bubble with typing effect"""
        if delay > 0:
            self.root.after(delay, lambda: self._show_bubble_impl(message_id_or_text, duration, on_typing_complete))
        else:
            self._show_bubble_impl(message_id_or_text, duration, on_typing_complete)
    
    def _show_bubble_impl(self, message_id_or_text, duration=2000, on_typing_complete=None):
        """Internal bubble display implementation"""
        # Resolve from unified REGISTRY
        if message_id_or_text in REGISTRY:
            msg_id = message_id_or_text
            config = REGISTRY[message_id_or_text]
            text = config.get("text", "")
            self.display_time = config.get("display_time", DEFAULTS.get('display_time', duration))
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
        
        self.bubble_label = tk.Label(bubble_canvas, bg='white', padx=BUBBLE_PADDING, pady=4)
        self.bubble_label.pack()
        
        bubble_x = self.pet_x + self.pet_width // 2
        bubble_y = self.pet_y - 40
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
                
                # Add extra padding for better vertical centering
                padding_x = 12
                padding_y = 6
                
                text_img = Image.new('RGBA', (text_width + padding_x * 2, text_height + padding_y * 2), (255, 255, 255, 0))
                draw = ImageDraw.Draw(text_img)
                # Position text to account for baseline
                draw.text((padding_x, 0), current_text, font=self.pil_font, fill=(0, 0, 0, 255))
                
                self.bubble_photo = ImageTk.PhotoImage(text_img)
                self.bubble_label.configure(image=self.bubble_photo, text="")
            else:
                self.bubble_label.configure(text=current_text, image="")
            
            self.typing_index += 1
            self.bubble.update_idletasks()
            
            label_width = self.bubble_label.winfo_reqwidth()
            label_height = self.bubble_label.winfo_reqheight()
            
            self._draw_rounded_border(self.bubble_canvas, label_width, label_height)
            
            bubble_x = self.pet_x + (self.pet_width - label_width) // 2 + 30
            bubble_y = self.pet_y - label_height - 10
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
        
        radius = BUBBLE_BORDER_RADIUS
        canvas.delete("border")
        
        # Corners
        canvas.create_arc(0, 0, radius*2, radius*2, start=90, extent=90, outline=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        canvas.create_arc(width-radius*2, 0, width, radius*2, start=0, extent=90, outline=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        canvas.create_arc(0, height-radius*2, radius*2, height, start=180, extent=90, outline=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        canvas.create_arc(width-radius*2, height-radius*2, width, height, start=270, extent=90, outline=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        
        # Edges
        canvas.create_line(radius, 0, width-radius, 0, fill=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        canvas.create_line(width, radius, width, height-radius, fill=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        canvas.create_line(radius, height, width-radius, height, fill=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
        canvas.create_line(0, radius, 0, height-radius, fill=BUBBLE_BORDER_COLOR, width=BUBBLE_BORDER_WIDTH, tags="border")
