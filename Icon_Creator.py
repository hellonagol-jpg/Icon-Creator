# GUI framework imports
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk  # Modern dark-themed GUI widgets

# Image processing imports
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

# Standard library imports
import os
import json
import math
import random
import shutil
import colorsys  # Color space conversions (HSV/RGB)
import datetime
import winsound  # Windows sound playback

# Get the directory where this script is located
# All asset paths are relative to this directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure customtkinter appearance - dark mode with blue theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Icon dimensions and display sizes
WIDTH, HEIGHT = 256, 256  # Final icon output size (SNES icon standard)
RENDER_SIZE = (330, 330)   # Internal rendering size with padding
PREVIEW_SIZE = (460, 460)  # Preview display size in the UI

# Asset directory paths
BG_DIR = os.path.join(SCRIPT_DIR, "Icon Backgrounds")      # Background images for icons
BORDER_DIR = os.path.join(SCRIPT_DIR, "Icon Borders")       # Border/frame overlays
FONT_DIR = os.path.join(SCRIPT_DIR, "Fonts")                # Custom font files (.ttf)
SOUND_DIR = os.path.join(SCRIPT_DIR, "Sounds")              # UI sound effects
IMAGE_DIR = os.path.join(SCRIPT_DIR, "Images")              # Main game images
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "Templates")         # Saved template configurations
DECOR_DIR = os.path.join(SCRIPT_DIR, "Decor")                # Decorative overlay images
STORAGE_DIR = os.path.join(SCRIPT_DIR, "Templates/Storage Icons")  # Original images saved with templates
GENERATED_BG_DIR = os.path.join(SCRIPT_DIR, "Generated Backgrounds")  # Procedurally generated backgrounds


# Main application class for SNES-style icon creation
class SNESIconGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Icon Creator")  # Window title
        
        # Set window size to 1400x900 and center it on screen
        window_width = 1400
        window_height = 900
        
        # Get screen dimensions for centering
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate center position
        center_x = (screen_width - window_width) // 2
        center_y = (screen_height - window_height) // 2
        
        # Set geometry with centered position
        self.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.resizable(True, True)  # Allow window resizing
        
        # Start in normal windowed mode (not fullscreen)
        self.state('normal')

        # Create necessary directories if they don't exist
        os.makedirs(TEMPLATE_DIR, exist_ok=True)
        os.makedirs(DECOR_DIR, exist_ok=True)
        os.makedirs(STORAGE_DIR, exist_ok=True)
        os.makedirs(GENERATED_BG_DIR, exist_ok=True)

        # Load retro-style fonts for UI (VT323 is a pixel-style font)
        self.retro_label_font = ctk.CTkFont(family="VT323", size=20)  # For labels and titles
        self.ui_font = ctk.CTkFont(family="VT323", size=16)            # For general UI text

        # OPTIMIZATION 1: Font cache to avoid reloading fonts repeatedly
        # Key: (font_path, size), Value: ImageFont object
        self.font_cache = {}

        # Default settings dictionary - contains all initial values for icon properties
        # Used as a template for new icons and reset functionality
        self.regular_default = {
            "title_lines": ["Template 1"],
            "line_hues": [0.0, 0.0, 0.0],
            "line_rainbows": [False, False, False],
            "line_outlines": [True, True, True],
            "line_font_size_offsets": [0, 0, 0],
            "line_font_spacing_offsets": [0, 0, 0],
            "line_text_offset_xs": [0, 0, 0],
            "line_text_offset_ys": [0, 0, 0],
            "line_active": [True, True, True],
            "bg_hue": 0.0,
            "bg_brightness": 1.0,
            "zoom_level": 50,
            "offset_x": 0,
            "offset_y": 0,
            "brightness": 0.9,
            "crt_enabled": True,
            "bg_scale": 1.0,
            "bg_offset_x": 0,
            "bg_offset_y": 0,
            "frame_offset_x": 0,
            "frame_offset_y": 0,
            "scanline_alpha": 20,
            "current_bg_index": 0,
            "current_frame_index": 0,
            "current_font_index": 0,
            "line_spacing_offset": -10,      # Vertical spacing between text lines
            "font_position_step": 1,          # Pixel step for font position adjustments
            "decor_enabled": True,            # Whether decoration overlay is visible
            "current_decor_index": 0,         # Index of selected decoration
            "decor_scale": 1.0,               # Scale of decoration overlay
            "decor_offset_x": 0,              # Horizontal offset of decoration
            "decor_offset_y": 0,              # Vertical offset of decoration
            "stretch_x": 1.0,                 # Horizontal stretch of main image
            "stretch_y": 1.0,                 # Vertical stretch of main image
            "glow_enabled": False,            # Whether text glow effect is enabled
            "glow_strength": 1.0,             # Intensity of glow effect
            "glow_color_hue": 0.0,            # Hue of glow color
            "glow_size": 2,                   # Size/radius of glow effect
            "shadow_opacity": 100            # Opacity of shadow overlay (0-255)
        }

        # Initialize icon state variables from defaults
        self.game_img_orig = None           # Original uploaded game image (unscaled)
        self.zoom_level = 50               # Zoom level for main image (0-100)
        self.offset_x = 0                  # Horizontal position of main image
        self.offset_y = 0                  # Vertical position of main image
        self.crt_enabled = True            # Whether CRT scanline effect is enabled
        self.curve_enabled = False         # Whether CRT curve distortion is enabled
        self.scanline_alpha = 20           # Opacity of scanlines (0-255)
        self.brightness = 0.9               # Brightness of main image
        self.bg_brightness = 1.0           # Brightness of background
        self.border_hue = 0.0             # Hue shift for border/frame
        self.bg_hue = 0.0                  # Hue shift for background
        self.bg_scale = 1.0                # Scale of background
        self.bg_offset_x = 0               # Horizontal offset of background
        self.bg_offset_y = 0               # Vertical offset of background
        self.frame_offset_x = 0           # Horizontal offset of frame
        self.frame_offset_y = 0           # Vertical offset of frame
        self.stretch_x = 1.0               # Horizontal stretch of main image
        self.stretch_y = 1.0               # Vertical stretch of main image
        
        # Text line properties (up to 3 lines supported)
        self.title_lines = ["Template 1"]  # Text content for each line
        self.line_active = [True, True, True]  # Whether each line is visible
        self.line_hues = [0.0, 0.0, 0.0]  # Hue color for each line
        self.line_rainbows = [False, False, False]  # Rainbow effect per line
        self.line_outlines = [True, True, True]  # Text outline per line
        self.line_font_size_offsets = [6, 6, 6]  # Font size adjustment per line
        self.line_font_spacing_offsets = [-1, -1, -1]  # Letter spacing per line
        self.line_text_offset_xs = [6, 6, 6]  # Horizontal text position per line
        self.line_text_offset_ys = [6, 6, 6]  # Vertical text position per line
        self.line_spacing_offset = -10     # Vertical spacing between lines
        self.font_position_step = 1        # Pixel step for font adjustments
        self.image_position_step = 1       # Pixel step for image adjustments
        
        # Decoration overlay properties
        self.decor_enabled = True           # Whether decoration is visible
        self.decor_scale = 1.0             # Scale of decoration
        self.decor_offset_x = 0            # Horizontal offset of decoration
        self.decor_offset_y = 0            # Vertical offset of decoration
        
        # Glow effect properties
        self.glow_enabled = False          # Whether glow effect is enabled
        self.glow_strength = 1.0           # Glow intensity
        self.glow_color_hue = 0.0          # Glow color hue
        self.glow_size = 2                 # Glow radius
        
        # Other properties
        self.shadow_opacity = 100          # Shadow overlay opacity
        self.guidelines_enabled = False    # Whether positioning guidelines are shown
        self.decor_files = []              # List of decoration filenames
        self.current_decor_index = 0       # Currently selected decoration

        # Asset lists and indices
        self.bg_files = []                 # List of background filenames
        self.frame_files = []              # List of border/frame filenames
        self.font_files = []               # List of font filenames
        self.current_bg_index = 0          # Currently selected background
        self.current_frame_index = 0       # Currently selected frame
        self.current_font_index = 0        # Currently selected font
        
        # Template system
        self.templates = []                 # List of saved template configurations
        self.template_previews = [None] * 6  # Preview images for 6 template slots
        
        # Utility variables
        self.distortion_map = None         # Precomputed distortion map for CRT effect
        self._update_timer = None          # Timer for debounced preview updates
        self._repeat_id = None             # Timer for repeating button holds

        # Font initialization
        self.font_path = os.path.join(FONT_DIR, "VT323-Regular.ttf")  # Default font path
        self.title_font = None             # Loaded font for title text
        self.small_font = None             # Loaded font for smaller text

        # Load arrow button images for position controls
        self.arrow_left = self._load_arrow("L.png")
        self.arrow_right = self._load_arrow("R.png")
        self.arrow_up = self._load_arrow("U.png")
        self.arrow_down = self._load_arrow("D.png")

        # UI checkbox variables
        self.rainbow_var = ctk.BooleanVar(value=False)  # Rainbow text effect toggle
        self.outline_var = ctk.BooleanVar(value=True)   # Text outline toggle
        self.glow_var = ctk.BooleanVar(value=False)     # Glow effect toggle
        self.glow_controls_frame = None                # Frame containing glow controls
        self.last_slider = None                         # Track last focused slider for keyboard control

        # Image upload behavior
        self.preserve_original_size = True  # Keep original image size when uploading new images

        # Build the user interface and load assets
        self._build_ui()              # Create all UI widgets and layout
        self._load_asset_lists()      # Scan directories for available assets
        self._preload_all_assets()   # Load assets into memory for faster access
        self._load_templates()       # Load saved template configurations
        if self.templates:
            self._load_from_template(0)  # Load first template if available
        self._load_current_fonts()    # Load the current font into memory

        # Set initial step button text
        self.step_button.configure(text="1px")

        # Initialize paragraph text box with current title lines
        if hasattr(self, 'paragraph_entry'):
            initial_text = '\n'.join(self.title_lines[:3])
            self.paragraph_entry.delete("1.0", "end")
            self.paragraph_entry.insert("1.0", initial_text)
            self.paragraph_entry.focus_set()  # Set focus to text input

        # Bind keyboard shortcuts for slider control
        self.bind("<Left>", self._keyboard_slider_left)   # Left arrow decreases slider
        self.bind("<Right>", self._keyboard_slider_right)  # Right arrow increases slider

        # Initialize toggle states for effects
        self._on_curve()           # Apply CRT curve effect state
        self._on_crt()             # Apply CRT scanline effect state
        self._on_decor_toggle()   # Apply decoration visibility state
        
        # Initialize color preview widgets with current hue values
        bg_color = self._get_solid_color(self.bg_hue)
        bg_hex_color = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        self.bg_hue_preview.configure(fg_color=bg_hex_color)
        
        border_color = self._get_solid_color(self.border_hue)
        border_hex_color = f"#{border_color[0]:02x}{border_color[1]:02x}{border_color[2]:02x}"
        self.border_hue_preview.configure(fg_color=border_hex_color)
        
        # Initialize text color RGB entry fields with first active line's color
        active_idx = next((i for i, a in enumerate(self.line_active) if a), 0)
        text_color = self._get_solid_color(self.line_hues[active_idx])
        self.text_r_entry.delete(0, "end")
        self.text_r_entry.insert(0, str(text_color[0]))
        self.text_g_entry.delete(0, "end")
        self.text_g_entry.insert(0, str(text_color[1]))
        self.text_b_entry.delete(0, "end")
        self.text_b_entry.insert(0, str(text_color[2]))

        # Initialize glow color RGB entries
        if hasattr(self, 'glow_color_preview'):
            glow_color = self._get_solid_color(self.glow_color_hue)
            self.glow_color_preview.configure(fg_color=f"#{glow_color[0]:02x}{glow_color[1]:02x}{glow_color[2]:02x}")
        if hasattr(self, 'glow_r_entry'):
            glow_color = self._get_solid_color(self.glow_color_hue)
            self.glow_r_entry.delete(0, "end")
            self.glow_r_entry.insert(0, str(glow_color[0]))
            self.glow_g_entry.delete(0, "end")
            self.glow_g_entry.insert(0, str(glow_color[1]))
            self.glow_b_entry.delete(0, "end")
            self.glow_b_entry.insert(0, str(glow_color[2]))
        
        # Generate initial preview
        self._update_preview()

    # ==================== FAST FONT CACHE ====================
    def _get_font(self, size, font_path=None):
        """Get a font object from cache or load it if not cached.
        
        Args:
            size: Font size in points (clamped between 8-500)
            font_path: Path to font file, uses default if None
            
        Returns:
            ImageFont object for the specified size
        """
        size = max(8, min(500, int(size)))  # Clamp size to reasonable range
        if font_path is None:
            font_path = self.font_path
        key = (font_path, size)  # Cache key combines path and size
        if key not in self.font_cache:
            try:
                self.font_cache[key] = ImageFont.truetype(font_path, size)
            except:
                # Fallback to default font if loading fails
                self.font_cache[key] = ImageFont.load_default()
        return self.font_cache[key]

    def _load_current_fonts(self):
        """Load the currently selected font into memory.
        
        Handles both regular fonts from the Fonts folder and template-specific fonts
        from template storage folders. Clears the font cache and reloads fonts
        at the standard sizes used for rendering.
        """
        # Reset font index if it's out of range (after font deletion)
        if self.font_files and self.current_font_index >= len(self.font_files):
            self.current_font_index = 0
        
        if self.font_files and self.current_font_index < len(self.font_files):
            font_filename = self.font_files[self.current_font_index]
            # Check if this is a template font (saved with a template)
            if font_filename.startswith("template_"):
                # Template font - construct path to template folder
                template_idx = font_filename.split("_")[1]
                template_folder = os.path.join(STORAGE_DIR, f"template_{template_idx}")
                self.font_path = os.path.join(template_folder, "template_font.ttf")
            else:
                # Regular font - use main Fonts folder
                self.font_path = os.path.join(FONT_DIR, font_filename)
        
        # Clear cache to force reload with new font
        self.font_cache.clear()
        
        # Load fonts at standard sizes used for rendering
        try:
            self.title_font = self._get_font(44)  # Large font for main text
            self.small_font = self._get_font(20)  # Small font for secondary text
        except:
            # Fallback to default font if loading fails
            self.title_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

    def _load_arrow(self, filename):
        """Load an arrow button image for position controls.
        
        Args:
            filename: Name of the arrow image file (L.png, R.png, U.png, D.png)
            
        Returns:
            CTkImage object for the arrow, or None if loading fails
        """
        path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                return ctk.CTkImage(light_image=img, size=(26, 26))
            except:
                pass  # Return None if loading fails
        return None

    def _preload_all_assets(self):
        """Initialize asset caches and load essential UI assets.
        
        Uses lazy loading for backgrounds, frames, and decorations - they are
        loaded on demand when first used. Only essential UI assets (CRT effect,
        scanlines, alpha mask, shadow) are loaded at startup.
        """
        # Initialize empty caches for lazy loading
        self.bg_cache = {}      # Background images cache
        self.frame_cache = {}   # Frame/border images cache
        self.decor_cache = {}   # Decoration images cache
        
        # Load essential UI assets at startup
        # CRT background for curve effect
        crt_path = os.path.join(IMAGE_DIR, "CRT.png")
        if os.path.exists(crt_path):
            crt = Image.open(crt_path).convert("RGBA")
            crt = crt.rotate(90, expand=True)  # Rotate for proper orientation
            self.crt_bg_img = crt.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
        else:
            self.crt_bg_img = None

        # Scanline overlay image
        scan_path = os.path.join(IMAGE_DIR, "scanlines.png")
        self.scanlines_img = Image.open(scan_path).convert("RGBA") if os.path.exists(scan_path) else None
        
        # Alpha mask for final icon shape
        alpha_path = os.path.join(IMAGE_DIR, "alpha.png")
        self.alpha_mask_img = Image.open(alpha_path).convert("L").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST) if os.path.exists(alpha_path) else None
        
        # Border shadow overlay
        shadow_path = os.path.join(IMAGE_DIR, "bordershadow.png")
        if os.path.exists(shadow_path):
            self.border_shadow_img = Image.open(shadow_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
        else:
            self.border_shadow_img = None
    
    def _get_bg(self, index, template_data=None):
        """Lazy load a background image on demand.
        
        Handles three cases:
        1. Template preview with embedded background
        2. Custom/generated backgrounds (index >= len(bg_files))
        3. Regular backgrounds from BG_DIR
        
        Args:
            index: Index of the background to load
            template_data: Optional template object with embedded background
            
        Returns:
            PIL Image object or None if loading fails
        """
        # Check if we're rendering a template preview with embedded background
        if template_data and hasattr(template_data, '_template_bg') and template_data._template_bg is not None:
            return template_data._template_bg
        
        # Check if it's a custom background (index >= len(bg_files))
        if index >= len(self.bg_files):
            # Custom background loading from Generated Backgrounds folder
            if index in self.bg_cache:
                return self.bg_cache[index]
            
            # Try to load the custom background
            if hasattr(self, 'custom_bg_files'):
                custom_bg_index = index - len(self.bg_files)
                if 0 <= custom_bg_index < len(self.custom_bg_files):
                    filename = self.custom_bg_files[custom_bg_index]
                    filepath = os.path.join(GENERATED_BG_DIR, filename)
                    if os.path.exists(filepath):
                        try:
                            bg = Image.open(filepath).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                            self.bg_cache[index] = bg
                            return bg
                        except:
                            self.bg_cache[index] = None
                            return None
            return None
        
        # Regular background loading from BG_DIR
        if index >= len(self.bg_files):
            return None
        if index not in self.bg_cache:
            path = os.path.join(BG_DIR, self.bg_files[index])
            if os.path.exists(path):
                self.bg_cache[index] = Image.open(path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
            else:
                self.bg_cache[index] = None
        return self.bg_cache[index]
    
    def _get_frame(self, index):
        """Lazy load a frame/border image on demand.
        
        Loads the frame image and applies an optional alpha mask (alpha2.png)
        to control the frame's transparency pattern.
        
        Args:
            index: Index of the frame to load
            
        Returns:
            PIL Image object or None if loading fails
        """
        if index >= len(self.frame_files):
            return None
        if index not in self.frame_cache:
            path = os.path.join(BORDER_DIR, self.frame_files[index])
            if os.path.exists(path):
                try:
                    frame = Image.open(path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                    # Apply optional alpha mask for frame transparency pattern
                    alpha2_path = os.path.join(IMAGE_DIR, "alpha2.png")
                    if os.path.exists(alpha2_path):
                        alpha2 = Image.open(alpha2_path).convert("L").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                        frame.putalpha(alpha2)
                    self.frame_cache[index] = frame
                except Exception as e:
                    self.frame_cache[index] = None
            else:
                self.frame_cache[index] = None
        return self.frame_cache[index]
    
    def _get_decor(self, index):
        """Lazy load a decoration image on demand.
        
        Decorations are small overlay images (typically 20x20) that can be
        placed over the icon for additional visual flair.
        
        Args:
            index: Index of the decoration to load
            
        Returns:
            PIL Image object or None if loading fails
        """
        if index >= len(self.decor_files):
            return None
        if index not in self.decor_cache:
            path = os.path.join(DECOR_DIR, self.decor_files[index])
            if os.path.exists(path):
                self.decor_cache[index] = Image.open(path).convert("RGBA").resize((20, 20), Image.Resampling.NEAREST)
            else:
                self.decor_cache[index] = None
        return self.decor_cache[index]

    def _load_asset_lists(self):
        """Scan asset directories and build lists of available files.
        
        Loads sorted lists of PNG files for backgrounds, frames, and decorations,
        and TTF files for fonts. Falls back to default files if directories are empty.
        """
        # Scan directories for asset files (case-insensitive extension check)
        self.bg_files = sorted([f for f in os.listdir(BG_DIR) if f.lower().endswith('.png')]) if os.path.exists(BG_DIR) else []
        self.frame_files = sorted([f for f in os.listdir(BORDER_DIR) if f.lower().endswith('.png')]) if os.path.exists(BORDER_DIR) else []
        self.font_files = sorted([f for f in os.listdir(FONT_DIR) if f.lower().endswith('.ttf')]) if os.path.exists(FONT_DIR) else []
        self.decor_files = sorted([f for f in os.listdir(DECOR_DIR) if f.lower().endswith('.png')]) if os.path.exists(DECOR_DIR) else []

        # Fallback to default files if directories are empty but defaults exist
        if not self.bg_files and os.path.exists(os.path.join(BG_DIR, "bg.png")): self.bg_files = ["bg.png"]
        if not self.frame_files and os.path.exists(os.path.join(BORDER_DIR, "border.png")): self.frame_files = ["border.png"]
        if not self.font_files and os.path.exists(os.path.join(FONT_DIR, "VT323-Regular.ttf")): self.font_files = ["VT323-Regular.ttf"]
        if not self.decor_files and os.path.exists(os.path.join(DECOR_DIR, "Chevron.png")): self.decor_files = ["Chevron.png", "Star.png"]

    def _debounced_update(self):
        """Schedule a debounced preview update.
        
        Cancels any pending update and schedules a new one after 16ms.
        This prevents excessive rendering during rapid UI changes.
        """
        if self._update_timer is not None:
            self.after_cancel(self._update_timer)
        self._update_timer = self.after(16, self._full_update)  # ~60fps update rate

    def _full_update(self):
        """Perform a full update of the preview and UI labels.
        
        Called by the debounced update timer to refresh the icon preview
        and update dynamic label values.
        """
        self._update_preview()           # Regenerate the icon preview
        self._update_dynamic_labels()   # Update selection labels
        self._update_debug_labels()     # Update debug/position labels

    def _update_debug_labels(self):
        """Update debug labels with current decoration values.
        
        Updates the labels that show the current scale and offset values
        for the decoration overlay.
        """
        if hasattr(self, 'decor_scale_label'): self.decor_scale_label.configure(text=f"{self.decor_scale:.2f}")
        if hasattr(self, 'decor_offset_x_label'): self.decor_offset_x_label.configure(text=f"{self.decor_offset_x}")
        if hasattr(self, 'decor_offset_y_label'): self.decor_offset_y_label.configure(text=f"{self.decor_offset_y}")

    # ==================== UNIFIED RENDER CORE + FAST TEXT ====================
    def _draw_text_optimized(self, draw, lines, num_lines, start_y_base, use_data):
        """Draw multi-line text with optimized per-character positioning.
        
        This method handles:
        - Dynamic font sizing based on number of lines (1 line = larger, 3 lines = smaller)
        - Horizontal and vertical centering of text
        - Per-character kerning (letter spacing)
        - Rainbow color effect (hue shifts per character)
        - Text outlines and glow effects
        - Direct RGB color overrides vs hue-based colors
        
        Args:
            draw: ImageDraw object to draw on
            lines: List of text strings to draw
            num_lines: Number of text lines (1-3)
            start_y_base: Base Y position for vertical centering
            use_data: Data object containing text properties (self or template data)
        """
        # Calculate line heights based on font size and spacing
        line_heights = []
        for i in range(num_lines):
            # Base size decreases with more lines: 44px for 1 line, 38px for 2, 32px for 3
            base_size = 44 if num_lines == 1 else 38 if num_lines == 2 else 32
            fs = max(20, min(500, base_size + use_data.line_font_size_offsets[i]))
            line_heights.append(fs + 2 + use_data.line_spacing_offset)
        
        # Calculate vertical centering position
        total_height = sum(line_heights)
        start_y = start_y_base - total_height // 2
        cumulative = 0
        
        # Draw each line of text
        for i, txt in enumerate(lines):
            if not txt:
                cumulative += line_heights[i]
                continue
            
            # Get font size and load font
            font_size = max(20, min(500, (44 if num_lines == 1 else 38 if num_lines == 2 else 32) + use_data.line_font_size_offsets[i]))
            # Use template's font_path if available, otherwise use current font
            font_path = getattr(use_data, 'font_path', None)
            title_font = self._get_font(font_size, font_path)
            kerning = use_data.line_font_spacing_offsets[i]
            
            # Pre-compute advance widths for each character using font.getlength()
            # This is more accurate than using a fixed character width
            char_advances = [title_font.getlength(char) for char in txt]
            total_width = sum(char_advances) + kerning * (len(txt) - 1)
            
            # Calculate center position with offset
            center_x = WIDTH // 2 + use_data.line_text_offset_xs[i] + 2
            ty = start_y + cumulative + use_data.line_text_offset_ys[i]
            
            # Start char_x at the left edge so each glyph is placed edge-to-edge
            char_x = center_x - total_width / 2
            
            # Draw characters with rainbow effect if enabled
            if use_data.line_rainbows[i]:
                for char_index, char in enumerate(txt):
                    advance = char_advances[char_index]
                    # Shift hue for each character to create rainbow gradient
                    hue = (use_data.line_hues[i] + char_index * 25) % 360
                    color = self._hue_to_rgb(hue)
                    self._draw_char_effects(draw, char, char_x, ty, title_font, color, use_data, i)
                    char_x += advance + kerning
            else:
                # Draw with uniform color (or direct RGB override)
                color = self._get_text_color(i, use_data)
                for char_index, char in enumerate(txt):
                    advance = char_advances[char_index]
                    # Draw black outline if enabled
                    if use_data.line_outlines[i]:
                        for dx, dy in [(-3,-3),(3,-3),(-3,3),(3,3),(-2,0),(2,0),(0,-2),(0,2)]:
                            draw.text((char_x + dx, ty + dy), char, font=title_font, fill=(0, 0, 0), anchor="lm")
                    # Draw glow effect if enabled
                    if use_data.glow_enabled and use_data.line_active[i]:
                        gc = self._get_glow_color(use_data)
                        alpha = int(80 * use_data.glow_strength)
                        glow_color = (gc[0], gc[1], gc[2], alpha)
                        for dx, dy in [(-use_data.glow_size,0),(use_data.glow_size,0),(0,-use_data.glow_size),(0,use_data.glow_size)]:
                            draw.text((char_x + dx, ty + dy), char, font=title_font, fill=glow_color, anchor="lm")
                    # Draw the main character
                    draw.text((char_x, ty), char, font=title_font, fill=color, anchor="lm")
                    char_x += advance + kerning
            cumulative += line_heights[i]

    def _draw_char_effects(self, draw, char, tx, ty, font, color, use_data, line_idx):
        """Draw a single character with outline and glow effects.
        
        Args:
            draw: ImageDraw object to draw on
            char: Character to draw
            tx: X position to draw at
            ty: Y position to draw at
            font: Font object to use
            color: RGB color tuple for the character
            use_data: Data object containing effect settings
            line_idx: Index of the text line (for per-line settings)
        """
        # Draw black outline if enabled for this line
        if use_data.line_outlines[line_idx]:
            for dx, dy in [(-3,-3),(3,-3),(-3,3),(3,3),(-3,0),(3,0),(0,-3),(0,3)]:
                draw.text((tx + dx, ty + dy), char, font=font, fill=(0, 0, 0), anchor="lm")
        
        # Draw glow effect if enabled and line is active
        if use_data.glow_enabled and use_data.line_active[line_idx]:
            gc = self._get_glow_color(use_data)
            alpha = int(80 * use_data.glow_strength)
            glow_color = (gc[0], gc[1], gc[2], alpha)
            for dx, dy in [(-use_data.glow_size,0),(use_data.glow_size,0),(0,-use_data.glow_size),(0,use_data.glow_size)]:
                draw.text((tx + dx, ty + dy), char, font=font, fill=glow_color, anchor="lm")
        
        # Draw the main character
        draw.text((tx, ty), char, font=font, fill=color, anchor="lm")

    def _render_core(self, for_preview=False, template_data=None):
        """Main rendering function that composes all icon layers.
        
        Renders the complete icon by layering:
        1. Background (with hue shift, brightness, scale, and offset)
        2. Main game image (with zoom, stretch, brightness, and position)
        3. CRT scanlines (if enabled)
        4. Text lines (with outlines, glow, rainbow effects)
        5. Decoration overlay (if enabled)
        6. Frame/border (with hue shift)
        7. Shadow overlay
        8. Alpha mask (for final icon shape)
        
        Args:
            for_preview: If True, returns a resized preview image
            template_data: If provided, uses template data instead of self
            
        Returns:
            PIL Image object (resized if for_preview=True)
        """
        use_data = template_data if template_data is not None else self
        inner = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))  # Create blank canvas

        # Layer 1: Background
        bg = self._get_bg(use_data.current_bg_index, template_data)
        if bg:
            bg = bg.copy()  # Don't modify cached original
            if use_data.bg_hue != 0:
                bg = self._apply_hue_shift(bg, use_data.bg_hue)  # Apply hue shift
            bg = ImageEnhance.Brightness(bg.convert("RGBA")).enhance(use_data.bg_brightness)  # Adjust brightness
            if use_data.bg_scale != 1.0:
                # Scale background
                new_w = int(WIDTH * use_data.bg_scale)
                new_h = int(HEIGHT * use_data.bg_scale)
                bg = bg.resize((new_w, new_h), Image.Resampling.NEAREST)
            # Center and apply offset
            paste_x = (WIDTH - bg.width) // 2 + use_data.bg_offset_x
            paste_y = (HEIGHT - bg.height) // 2 + use_data.bg_offset_y
            # Fix transparency mask - only use mask if image has alpha channel
            if bg.mode == 'RGBA':
                inner.paste(bg, (paste_x, paste_y), bg)
            else:
                inner.paste(bg, (paste_x, paste_y))

        # Layer 2: Main game image (only if not rendering template preview)
        if self.game_img_orig and template_data is None:
            base_scale = self._get_scale()  # Get zoom scale
            scale_x = base_scale * self.stretch_x  # Apply horizontal stretch
            scale_y = base_scale * self.stretch_y  # Apply vertical stretch
            scaled_w = max(1, int(self.game_img_orig.width * scale_x))
            scaled_h = max(1, int(self.game_img_orig.height * scale_y))
            scaled = self.game_img_orig.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)
            scaled = ImageEnhance.Brightness(scaled).enhance(self.brightness)  # Adjust brightness
            # Center and apply offset
            paste_x = (WIDTH - scaled_w) // 2 + self.offset_x
            paste_y = (HEIGHT - scaled_h) // 2 + self.offset_y
                # Fix transparency mask - only use mask if image has alpha channel
            if scaled.mode == 'RGBA':
                inner.paste(scaled, (paste_x, paste_y), scaled)
            else:
                inner.paste(scaled, (paste_x, paste_y))

        # Layer 3: CRT scanlines (if enabled)
        if use_data.crt_enabled and self.scanlines_img:
            scan = self.scanlines_img.copy()
            scanline_alpha = getattr(use_data, 'scanline_alpha', 45)
            if scanline_alpha < 100:
                # Adjust scanline opacity
                factor = scanline_alpha / 100.0
                alpha_layer = scan.split()[3]
                new_alpha = alpha_layer.point(lambda p: int(p * factor))
                scan.putalpha(new_alpha)
            paste_x = (WIDTH - scan.width) // 2
            paste_y = (HEIGHT - scan.height) // 2
            # Fix transparency mask - only use mask if image has alpha channel
            if scan.mode == 'RGBA':
                inner.paste(scan, (paste_x, paste_y), scan)
            else:
                inner.paste(scan, (paste_x, paste_y))

        # Layer 4: Text and decoration (on top of scanlines)
        draw = ImageDraw.Draw(inner)
        lines = [line for line in use_data.title_lines[:3] if line]  # Get non-empty lines
        num_lines = len(lines)
        # Y position varies based on number of lines for optimal centering
        self._draw_text_optimized(draw, lines, num_lines, 228 if num_lines == 1 else 208 if num_lines == 2 else 193, use_data)

        # Layer 5: Decoration overlay (bottom-right corner)
        if use_data.decor_enabled:
            dec = self._get_decor(use_data.current_decor_index)
            if dec:
                dec = dec.copy()
                dec_w = int(20 * use_data.decor_scale)
                dec_h = int(20 * use_data.decor_scale)
                dec = dec.resize((dec_w, dec_h), Image.Resampling.NEAREST)
                margin = 22  # Distance from edge
                paste_x = WIDTH - dec_w - margin + use_data.decor_offset_x
                paste_y = HEIGHT - dec_h - margin + use_data.decor_offset_y
                # Fix transparency mask - only use mask if image has alpha channel
                if dec.mode == 'RGBA':
                    inner.paste(dec, (paste_x, paste_y), dec)
                else:
                    inner.paste(dec, (paste_x, paste_y))

        # Layer 6: Border/frame (on top of everything except shadow)
        frame = self._get_frame(use_data.current_frame_index)
        if frame:
            frame = frame.copy()
            if use_data.border_hue != 0:
                frame = self._apply_hue_shift(frame, use_data.border_hue)  # Apply hue shift
            # Fix transparency mask - only use mask if image has alpha channel
            if frame.mode == 'RGBA':
                inner.paste(frame, (use_data.frame_offset_x, use_data.frame_offset_y), frame)
            else:
                inner.paste(frame, (use_data.frame_offset_x, use_data.frame_offset_y))

        # Layer 7: Border shadow overlay (always on top of border)
        if self.border_shadow_img and hasattr(use_data, 'shadow_opacity'):
            shadow = self.border_shadow_img.copy()
            shadow_opacity = getattr(use_data, 'shadow_opacity', 100)
            if shadow_opacity < 100:
                # Adjust shadow opacity
                factor = shadow_opacity / 100.0
                alpha_layer = shadow.split()[3]
                new_alpha = alpha_layer.point(lambda p: int(p * factor))
                shadow.putalpha(new_alpha)
            inner.paste(shadow, (0, 0), shadow)

        # Layer 8: Apply alpha mask for final icon shape
        if self.alpha_mask_img:
            inner.putalpha(self.alpha_mask_img)

        # Return preview-sized image if requested, otherwise return full-size
        if for_preview:
            large = Image.new("RGBA", RENDER_SIZE, (0, 0, 0, 0))
            offset = (RENDER_SIZE[0] - WIDTH) // 2
            large.paste(inner, (offset, offset))
            return large.resize(PREVIEW_SIZE, Image.Resampling.LANCZOS)
        return inner

    def _composite_image(self, for_preview=False):
        """Wrapper for _render_core for backward compatibility.
        
        Args:
            for_preview: If True, returns a resized preview image
            
        Returns:
            PIL Image object
        """
        return self._render_core(for_preview=for_preview)

    def _update_preview(self):
        """Update the preview label with the current icon rendering.
        
        Renders the icon at preview size and updates the UI preview widget.
        """
        img = self._composite_image(for_preview=True)
        ctk_img = ctk.CTkImage(light_image=img, size=img.size)
        self.preview_label.configure(image=ctk_img)

    def _render_template_preview(self, idx):
        """Render a template preview from its folder structure.
        
        Loads the template's settings and assets from its storage folder
        and renders a small preview image for the template selection UI.
        
        Args:
            idx: Template index (0-5)
            
        Returns:
            CTkImage object for the preview, or a blank placeholder if template doesn't exist
        """
        import json
        
        try:
            template_folder = os.path.join(STORAGE_DIR, f"template_{idx}")
            
            # Check if template folder exists
            if not os.path.exists(template_folder):
                # Return blank preview if template doesn't exist
                blank = Image.new("RGB", (128, 128), (40, 40, 40))
                draw = ImageDraw.Draw(blank)
                draw.text((64, 64), f"Template {idx+1}", fill="white", anchor="mm")
                return ctk.CTkImage(light_image=blank, size=(128, 128))
            
            # Load settings from JSON file
            settings_path = os.path.join(template_folder, "template_settings.txt")
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, 'r') as f:
                        settings = json.load(f)
                except:
                    settings = {}
            else:
                settings = {}
            
            # Load game image from template folder
            game_path = os.path.join(template_folder, "template_game.png")
            game_img = None
            if os.path.exists(game_path):
                try:
                    game_img = Image.open(game_path).convert("RGBA")
                except:
                    game_img = None

            # Create temporary data object to hold template settings
            class TempData: pass
            td = TempData()
            
            # Load all settings from JSON with fallback defaults
            td.title_lines = settings.get("title_lines", ["Template 1"])
            td.line_font_size_offsets = settings.get("line_font_size_offsets", [6,6,6])
            td.line_font_spacing_offsets = settings.get("line_font_spacing_offsets", [-1,-1,-1])
            td.line_text_offset_xs = settings.get("line_text_offset_xs", [0,0,0])
            td.line_text_offset_ys = settings.get("line_text_offset_ys", [4,4,4])
            td.line_spacing_offset = settings.get("line_spacing_offset", -10)
            td.line_rainbows = settings.get("line_rainbows", [False,False,False])
            td.line_outlines = settings.get("line_outlines", [True,True,True])
            td.line_hues = settings.get("line_hues", [0.0,0.0,0.0])
            td.line_active = settings.get("line_active", [True,True,True])
            td.border_hue = settings.get("border_hue", 0.0)
            td.decor_enabled = settings.get("decor_enabled", True)
            td.current_decor_index = settings.get("current_decor_index", 0)
            td.decor_scale = settings.get("decor_scale", 1.0)
            td.decor_offset_x = settings.get("decor_offset_x", 0)
            td.decor_offset_y = settings.get("decor_offset_y", 0)
            td.curve_enabled = False
            td.crt_enabled = settings.get("crt_enabled", True)
            td.scanline_alpha = settings.get("scanline_alpha", 45)
            td.bg_hue = settings.get("bg_hue", 0.0)
            td.bg_brightness = settings.get("bg_brightness", 1.0)
            td.bg_scale = settings.get("bg_scale", 1.0)
            td.bg_offset_x = settings.get("bg_offset_x", 0)
            td.bg_offset_y = settings.get("bg_offset_y", 0)
            td.current_bg_index = settings.get("current_bg_index", 0)
            td.current_frame_index = settings.get("current_frame_index", 0)
            td.current_font_index = settings.get("current_font_index", 0)
            td.frame_offset_x = settings.get("frame_offset_x", 0)
            td.frame_offset_y = settings.get("frame_offset_y", 0)
            td.glow_enabled = settings.get("glow_enabled", False)
            td.glow_strength = settings.get("glow_strength", 1.0)
            td.glow_color_hue = settings.get("glow_color_hue", 0.0)
            td.glow_size = settings.get("glow_size", 2)
            td.shadow_opacity = settings.get("shadow_opacity", 100)
            td.zoom_level = settings.get("zoom_level", 50)
            td.offset_x = settings.get("offset_x", 0)
            td.offset_y = settings.get("offset_y", 0)
            td.stretch_x = settings.get("stretch_x", 1.0)
            td.stretch_y = settings.get("stretch_y", 1.0)
            td.brightness = settings.get("brightness", 0.9)
            
            # Add font_path for template rendering
            if hasattr(self, 'font_files') and self.font_files and td.current_font_index < len(self.font_files):
                td.font_path = os.path.join(FONT_DIR, self.font_files[td.current_font_index])
            else:
                td.font_path = self.font_path
            
            # Add direct RGB data for template preview (for custom RGB color overrides)
            direct_rgb = settings.get("direct_rgb", {})
            if direct_rgb:
                # Convert string keys to integers for template preview
                td._direct_rgb = {int(k): v for k, v in direct_rgb.items()}
            else:
                td._direct_rgb = {}

            # Load template background if it exists (custom background saved with template)
            bg_path = os.path.join(template_folder, "template_bg.png")
            if os.path.exists(bg_path):
                try:
                    td._template_bg = Image.open(bg_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                except:
                    td._template_bg = None
            else:
                td._template_bg = None

            # Render the icon with template settings
            canvas = self._render_core(for_preview=False, template_data=td)

            # Paste the game image onto the canvas (template preview needs manual pasting)
            if game_img:
                base_scale = 0.2 + ((td.zoom_level + 100) / 200.0) * 1.8  # Convert zoom to scale
                stretch_x = td.stretch_x
                stretch_y = td.stretch_y
                scaled_w = max(1, int(game_img.width * base_scale * stretch_x))
                scaled_h = max(1, int(game_img.height * base_scale * stretch_y))
                scaled = game_img.resize((scaled_w, scaled_h), Image.Resampling.NEAREST)
                scaled = ImageEnhance.Brightness(scaled).enhance(td.brightness)
                paste_x = (WIDTH - scaled_w) // 2 + td.offset_x
                paste_y = (HEIGHT - scaled_h) // 2 + td.offset_y
                # Fix transparency mask - only use mask if image has alpha channel
                if scaled.mode == 'RGBA':
                    canvas.paste(scaled, (paste_x, paste_y), scaled)
                else:
                    canvas.paste(scaled, (paste_x, paste_y))

            # Resize to thumbnail size for UI preview
            small = canvas.resize((128, 128), Image.Resampling.LANCZOS)
            return ctk.CTkImage(light_image=small, size=(128, 128))
        except Exception as e:
            # Create a blank preview with error text if rendering fails
            blank = Image.new("RGB", (128, 128), (40, 40, 40))
            draw = ImageDraw.Draw(blank)
            draw.text((64, 64), f"Template {idx+1}", fill="white", anchor="mm")
            return ctk.CTkImage(light_image=blank, size=(128, 128))

    # ==================== MOVEMENT FIX (expanded range) ====================
    def _move_text_left(self):
        """Move all active text lines left by the current step size."""
        for i in range(3):
            if self.line_active[i]:
                self.line_text_offset_xs[i] = max(-140, self.line_text_offset_xs[i] - self.font_position_step)
        self._debounced_update()

    def _move_text_right(self):
        """Move all active text lines right by the current step size."""
        for i in range(3):
            if self.line_active[i]:
                self.line_text_offset_xs[i] = min(140, self.line_text_offset_xs[i] + self.font_position_step)
        self._debounced_update()

    def _reset_to_default(self):
        """Reset all icon settings to their default values.
        
        Restores all sliders, colors, positions, and effects to the initial
        state defined in regular_default. Also clears the loaded game image.
        """
        self._play_sound("delete.wav")
        d = self.regular_default
        self.line_hues = d["line_hues"][:]
        self.line_rainbows = d["line_rainbows"][:]
        self.line_outlines = d["line_outlines"][:]
        self.line_font_size_offsets = d["line_font_size_offsets"][:]
        self.line_font_spacing_offsets = d["line_font_spacing_offsets"][:]
        self.line_text_offset_xs = d["line_text_offset_xs"][:]
        self.line_text_offset_ys = d["line_text_offset_ys"][:]
        self.line_active = d["line_active"][:]
        self.bg_hue = d["bg_hue"]
        self.bg_brightness = d["bg_brightness"]
        self.zoom_level = d["zoom_level"]
        self.offset_x = d["offset_x"]
        self.offset_y = d["offset_y"]
        self.brightness = d["brightness"]
        self.crt_enabled = d["crt_enabled"]
        self.curve_enabled = False
        self.bg_scale = d["bg_scale"]
        self.bg_offset_x = d["bg_offset_x"]
        self.bg_offset_y = d["bg_offset_y"]
        self.frame_offset_x = d["frame_offset_x"]
        self.frame_offset_y = d["frame_offset_y"]
        self.scanline_alpha = d["scanline_alpha"]
        self.current_bg_index = d["current_bg_index"]
        self.current_frame_index = d["current_frame_index"]
        self.current_font_index = d["current_font_index"]
        self.line_spacing_offset = d["line_spacing_offset"]
        self.font_position_step = d["font_position_step"]
        self.decor_enabled = d["decor_enabled"]
        self.current_decor_index = d["current_decor_index"]
        self.decor_scale = d["decor_scale"]
        self.decor_offset_x = d["decor_offset_x"]
        self.decor_offset_y = d["decor_offset_y"]
        self.stretch_x = d["stretch_x"]
        self.stretch_y = d["stretch_y"]
        self.glow_enabled = d.get("glow_enabled", False)
        self.glow_var.set(self.glow_enabled)
        self.glow_strength = d.get("glow_strength", 1.0)
        self.glow_color_hue = d.get("glow_color_hue", 0.0)
        self.glow_size = d.get("glow_size", 2)
        self.shadow_opacity = d.get("shadow_opacity", 100)
        self.game_img_orig = None
        self.crt_var.set(self.crt_enabled)
        self.decor_var.set(self.decor_enabled)
        self._on_crt()
        self._on_decor_toggle()
        self.rainbow_var.set(False)
        self.outline_var.set(True)
        for i in range(3):
            self.line_toggle_buttons[i].configure(fg_color="#00ff00" if self.line_active[i] else "#555555")
        self.zoom_slider.set(self.zoom_level)
        self.x_slider.set(self.offset_x)
        self.y_slider.set(self.offset_y)
        self.stretch_x_slider.set(self.stretch_x)
        self.stretch_y_slider.set(self.stretch_y)
        self.brightness_slider.set(self.brightness)
        self.bg_brightness_slider.set(self.bg_brightness)
        self.opacity_slider.set(self.scanline_alpha)
        if hasattr(self, 'opacity_entry'):
            self.opacity_entry.delete(0, "end")
            self.opacity_entry.insert(0, str(self.scanline_alpha))
        self.hue_slider.set(self.line_hues[0] if self.line_active[0] else 0)
        if hasattr(self, 'glow_strength_slider'): self.glow_strength_slider.set(self.glow_strength)
        if hasattr(self, 'glow_color_slider'): self.glow_color_slider.set(self.glow_color_hue)
        if hasattr(self, 'glow_size_slider'): self.glow_size_slider.set(self.glow_size)
        if hasattr(self, 'shadow_opacity_slider'): self.shadow_opacity_slider.set(self.shadow_opacity)
        if hasattr(self, 'shadow_opacity_entry'):
            self.shadow_opacity_entry.delete(0, "end")
            self.shadow_opacity_entry.insert(0, str(self.shadow_opacity))
        self.step_button.configure(text=f"{self.font_position_step}px")
        self._show_background_selector()
        self._load_current_fonts()
        if hasattr(self, 'color_preview'):
            color = self._get_solid_color(self.line_hues[0] if self.line_active[0] else 0)
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.color_preview.configure(fg_color=hex_color)
        self._debounced_update()
        self.show_save_confirmation("Reset to Default")

    # (All other methods are identical to the version you pasted — only the defaults, movement range, and template defaults were changed)

    def _decrease_font_size(self):
        """Decrease font size for all active text lines."""
        for i in range(3):
            if self.line_active[i]:
                self.line_font_size_offsets[i] = max(-100, self.line_font_size_offsets[i] - 1)
        self._debounced_update()

    def _increase_font_size(self):
        """Increase font size for all active text lines."""
        for i in range(3):
            if self.line_active[i]:
                self.line_font_size_offsets[i] = min(470, self.line_font_size_offsets[i] + 1)
        self._debounced_update()

    def _decrease_font_spacing(self):
        """Decrease letter spacing (kerning) for all active text lines."""
        for i in range(3):
            if self.line_active[i]:
                self.line_font_spacing_offsets[i] = max(-50, self.line_font_spacing_offsets[i] - 1)
        self._debounced_update()

    def _increase_font_spacing(self):
        """Increase letter spacing (kerning) for all active text lines."""
        for i in range(3):
            if self.line_active[i]:
                self.line_font_spacing_offsets[i] = min(500, self.line_font_spacing_offsets[i] + 1)
        self._debounced_update()

    def _decrease_line_spacing(self):
        """Decrease vertical spacing between text lines."""
        self.line_spacing_offset = max(-200, self.line_spacing_offset - 1)
        self._debounced_update()

    def _increase_line_spacing(self):
        """Increase vertical spacing between text lines."""
        self.line_spacing_offset = min(500, self.line_spacing_offset + 1)
        self._debounced_update()

    def _move_text_up(self):
        """Move all active text lines up by the current step size."""
        for i in range(3):
            if self.line_active[i]:
                self.line_text_offset_ys[i] = max(-110, self.line_text_offset_ys[i] - self.font_position_step)
        self._debounced_update()

    def _move_text_down(self):
        """Move all active text lines down by the current step size."""
        for i in range(3):
            if self.line_active[i]:
                self.line_text_offset_ys[i] = min(90, self.line_text_offset_ys[i] + self.font_position_step)
        self._debounced_update()

    def _cycle_position_step(self):
        """Cycle the text position step size between 1-10 pixels."""
        self.font_position_step += 1
        if self.font_position_step > 10:
            self.font_position_step = 1
        self.step_button.configure(text=f"{self.font_position_step}px")
        self._debounced_update()

    def _on_decor_toggle(self):
        """Toggle decoration overlay visibility and show/hide controls."""
        self.decor_enabled = self.decor_var.get()
        if self.decor_var.get():
            self.decor_controls_frame.pack(fill="x", padx=15, pady=(0,12), after=self.decor_checkbox)
        else:
            self.decor_controls_frame.pack_forget()
        self._debounced_update()

    def _toggle_preserve_original_size(self):
        """Toggle preserve original image size when re-uploading."""
        self.preserve_original_size = self.preserve_var.get()

    def _prev_decor(self):
        """Cycle to previous decoration in the list."""
        if self.decor_files:
            self.current_decor_index = (self.current_decor_index - 1) % len(self.decor_files)
            self._debounced_update()

    def _next_decor(self):
        """Cycle to next decoration in the list."""
        if self.decor_files:
            self.current_decor_index = (self.current_decor_index + 1) % len(self.decor_files)
            self._debounced_update()

    def _move_image_left(self):
        """Move the main game image left by the current step size."""
        self.offset_x = max(-140, self.offset_x - self.image_position_step)
        self._debounced_update()

    def _move_image_right(self):
        """Move the main game image right by the current step size."""
        self.offset_x = min(140, self.offset_x + self.image_position_step)
        self._debounced_update()

    def _move_image_up(self):
        """Move the main game image up by the current step size."""
        self.offset_y = max(-140, self.offset_y - self.image_position_step)
        self._debounced_update()

    def _move_image_down(self):
        """Move the main game image down by the current step size."""
        self.offset_y = min(140, self.offset_y + self.image_position_step)
        self._debounced_update()

    def _cycle_image_position_step(self):
        """Cycle the image position step size between 1-10 pixels."""
        self.image_position_step += 1
        if self.image_position_step > 10:
            self.image_position_step = 1
        self.image_step_button.configure(text=f"{self.image_position_step}px")
        self._debounced_update()

    def _on_bg_brightness(self, value):
        """Handle background brightness slider change.
        
        Maps slider value (-100 to 200) to brightness (0.2 to 2.0).
        """
        self.last_slider = self.bg_brightness_slider
        # Map slider value (-100 to 200) to brightness (0.2 to 2.0)
        self.bg_brightness = 0.2 + (float(value) + 100) / 300.0 * 1.8
        # Update entry field
        self.bg_brightness_entry.delete(0, "end")
        self.bg_brightness_entry.insert(0, f"{self.bg_brightness:.2f}")
        self._debounced_update()

    def _on_bg_brightness_mouse_release(self):
        """Snap background brightness to 1.0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.bg_brightness - 1.0) < 0.05:
            self.bg_brightness = 1.0
            # Convert back to slider value
            slider_value = (self.bg_brightness - 0.2) / 1.8 * 300.0 - 100
            self.bg_brightness_slider.set(slider_value)
            self.bg_brightness_entry.delete(0, "end")
            self.bg_brightness_entry.insert(0, f"{self.bg_brightness:.2f}")
            self._debounced_update()

    def _on_bg_brightness_entry_changed(self):
        """Handle background brightness entry field change.
        
        Validates input and clamps to valid range (0.2 to 2.0).
        """
        try:
            value = float(self.bg_brightness_entry.get())
            # Clamp to valid range
            value = max(0.2, min(2.0, value))
            self.bg_brightness = value
            # Convert to slider value
            slider_value = (value - 0.2) / 1.8 * 300.0 - 100
            self.bg_brightness_slider.set(slider_value)
            self.bg_brightness_entry.delete(0, "end")
            self.bg_brightness_entry.insert(0, f"{value:.2f}")
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.bg_brightness_entry.delete(0, "end")
            self.bg_brightness_entry.insert(0, f"{self.bg_brightness:.2f}")

    def _on_bg_hue(self, value):
        """Handle background hue slider change.
        
        Updates the background hue shift and updates the color preview
        and RGB entry fields to reflect the new color.
        """
        self.last_slider = self.bg_hue_slider
        self.bg_hue = float(value)
        # Update color preview and RGB entries
        color = self._get_solid_color(self.bg_hue)
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        self.bg_hue_preview.configure(fg_color=hex_color)
        # Update RGB entries
        self.bg_r_entry.delete(0, "end")
        self.bg_r_entry.insert(0, str(color[0]))
        self.bg_g_entry.delete(0, "end")
        self.bg_g_entry.insert(0, str(color[1]))
        self.bg_b_entry.delete(0, "end")
        self.bg_b_entry.insert(0, str(color[2]))
        self._debounced_update()

    def _on_bg_hue_mouse_release(self):
        """Snap background hue to 0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.bg_hue) < 5:
            self.bg_hue = 0.0
            self.bg_hue_slider.set(0.0)
            color = self._get_solid_color(self.bg_hue)
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.bg_hue_preview.configure(fg_color=hex_color)
            self.bg_r_entry.delete(0, "end")
            self.bg_r_entry.insert(0, str(color[0]))
            self.bg_g_entry.delete(0, "end")
            self.bg_g_entry.insert(0, str(color[1]))
            self.bg_b_entry.delete(0, "end")
            self.bg_b_entry.insert(0, str(color[2]))
            self._debounced_update()

    def _on_bg_rgb_changed(self):
        """Handle background RGB entry field change.
        
        Converts RGB values back to hue and updates the slider and preview.
        """
        try:
            r = int(self.bg_r_entry.get())
            g = int(self.bg_g_entry.get())
            b = int(self.bg_b_entry.get())
            # Clamp to valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Convert RGB to hue
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = h * 360
            
            self.bg_hue = hue
            self.bg_hue_slider.set(hue)
            
            # Update color preview
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_hue_preview.configure(fg_color=hex_color)
            
            # Update entries with clamped values
            self.bg_r_entry.delete(0, "end")
            self.bg_r_entry.insert(0, str(r))
            self.bg_g_entry.delete(0, "end")
            self.bg_g_entry.insert(0, str(g))
            self.bg_b_entry.delete(0, "end")
            self.bg_b_entry.insert(0, str(b))
            
            self._debounced_update()
        except ValueError:
            # Restore previous values if invalid input
            color = self._get_solid_color(self.bg_hue)
            self.bg_r_entry.delete(0, "end")
            self.bg_r_entry.insert(0, str(color[0]))
            self.bg_g_entry.delete(0, "end")
            self.bg_g_entry.insert(0, str(color[1]))
            self.bg_b_entry.delete(0, "end")
            self.bg_b_entry.insert(0, str(color[2]))

    def _on_border_hue(self, value):
        """Handle border/frame hue slider change.
        
        Updates the border hue shift and updates the color preview
        and RGB entry fields to reflect the new color.
        """
        self.last_slider = self.border_hue_slider
        self.border_hue = float(value)
        # Update color preview and RGB entries
        color = self._get_solid_color(self.border_hue)
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        self.border_hue_preview.configure(fg_color=hex_color)
        # Update RGB entries
        self.border_r_entry.delete(0, "end")
        self.border_r_entry.insert(0, str(color[0]))
        self.border_g_entry.delete(0, "end")
        self.border_g_entry.insert(0, str(color[1]))
        self.border_b_entry.delete(0, "end")
        self.border_b_entry.insert(0, str(color[2]))
        self._debounced_update()

    def _on_border_hue_mouse_release(self):
        """Snap border hue to 0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.border_hue) < 5:
            self.border_hue = 0.0
            self.border_hue_slider.set(0.0)
            color = self._get_solid_color(self.border_hue)
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.border_hue_preview.configure(fg_color=hex_color)
            self.border_r_entry.delete(0, "end")
            self.border_r_entry.insert(0, str(color[0]))
            self.border_g_entry.delete(0, "end")
            self.border_g_entry.insert(0, str(color[1]))
            self.border_b_entry.delete(0, "end")
            self.border_b_entry.insert(0, str(color[2]))
            self._debounced_update()

    def _on_border_rgb_changed(self):
        """Handle border RGB entry field change.
        
        Converts RGB values back to hue and updates the slider and preview.
        """
        try:
            r = int(self.border_r_entry.get())
            g = int(self.border_g_entry.get())
            b = int(self.border_b_entry.get())
            # Clamp to valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Convert RGB to hue
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = h * 360
            
            self.border_hue = hue
            self.border_hue_slider.set(hue)
            
            # Update color preview
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.border_hue_preview.configure(fg_color=hex_color)
            
            # Update entries with clamped values
            self.border_r_entry.delete(0, "end")
            self.border_r_entry.insert(0, str(r))
            self.border_g_entry.delete(0, "end")
            self.border_g_entry.insert(0, str(g))
            self.border_b_entry.delete(0, "end")
            self.border_b_entry.insert(0, str(b))
            
            self._debounced_update()
        except ValueError:
            # Restore previous values if invalid input
            color = self._get_solid_color(self.border_hue)
            self.border_r_entry.delete(0, "end")
            self.border_r_entry.insert(0, str(color[0]))
            self.border_g_entry.delete(0, "end")
            self.border_g_entry.insert(0, str(color[1]))
            self.border_b_entry.delete(0, "end")
            self.border_b_entry.insert(0, str(color[2]))

    def _on_shadow_opacity(self, value):
        """Handle shadow opacity slider change."""
        self.last_slider = self.shadow_opacity_slider
        self.shadow_opacity = int(value)
        self.shadow_opacity_entry.delete(0, "end")
        self.shadow_opacity_entry.insert(0, str(self.shadow_opacity))
        self._debounced_update()

    def _on_shadow_opacity_mouse_release(self):
        """Snap shadow opacity to 100 when close to default on mouse release."""
        if abs(self.shadow_opacity - 100) < 5:
            self.shadow_opacity = 100
            self.shadow_opacity_slider.set(100)
            self.shadow_opacity_entry.delete(0, "end")
            self.shadow_opacity_entry.insert(0, "100")
            self._debounced_update()

    def _on_shadow_opacity_entry_changed(self):
        """Handle shadow opacity entry field change.
        
        Validates input and clamps to valid range (0-100).
        """
        try:
            value = int(self.shadow_opacity_entry.get())
            value = max(0, min(100, value))
            self.shadow_opacity = value
            self.shadow_opacity_slider.set(value)
            self.shadow_opacity_entry.delete(0, "end")
            self.shadow_opacity_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            self.shadow_opacity_entry.delete(0, "end")
            self.shadow_opacity_entry.insert(0, str(self.shadow_opacity))

    def _on_outline_toggle(self):
        """Toggle text outline effect for all active text lines."""
        for i in range(3):
            if self.line_active[i]:
                self.line_outlines[i] = self.outline_var.get()
        self._debounced_update()

    def _on_rainbow_toggle(self):
        """Toggle rainbow color effect for all active text lines."""
        for i in range(3):
            if self.line_active[i]:
                self.line_rainbows[i] = self.rainbow_var.get()
        self._debounced_update()

    def _on_glow_toggle(self):
        """Toggle glow effect and show/hide glow controls frame."""
        self.glow_enabled = self.glow_var.get()
        if self.glow_var.get():
            self.glow_controls_frame.pack(fill="x", padx=15, pady=(0,12), after=self.glow_checkbox)
            # Ensure sliders are set to current values when shown
            if hasattr(self, 'glow_strength_slider'):
                self.glow_strength_slider.set(self.glow_strength)
                self.glow_strength_entry.delete(0, "end")
                self.glow_strength_entry.insert(0, f"{self.glow_strength:.2f}")
            if hasattr(self, 'glow_size_slider'):
                self.glow_size_slider.set(self.glow_size)
                self.glow_size_entry.delete(0, "end")
                self.glow_size_entry.insert(0, str(self.glow_size))
            if hasattr(self, 'glow_color_slider'):
                self.glow_color_slider.set(self.glow_color_hue)
        else:
            self.glow_controls_frame.pack_forget()
        self._debounced_update()

    def _on_glow_strength(self, value):
        """Handle glow strength slider change."""
        self.last_slider = self.glow_strength_slider
        self.glow_strength = float(value)
        # Update entry field
        self.glow_strength_entry.delete(0, "end")
        self.glow_strength_entry.insert(0, f"{self.glow_strength:.2f}")
        self._debounced_update()

    def _on_glow_strength_mouse_release(self):
        """Snap glow strength to 1.0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.glow_strength - 1.0) < 0.1:
            self.glow_strength = 1.0
            self.glow_strength_slider.set(1.0)
            self.glow_strength_entry.delete(0, "end")
            self.glow_strength_entry.insert(0, f"{self.glow_strength:.2f}")
            self._debounced_update()

    def _on_glow_strength_entry_changed(self):
        """Handle glow strength entry field change.
        
        Validates input and clamps to valid range (0.0 to 2.0).
        """
        try:
            value = float(self.glow_strength_entry.get())
            # Clamp to valid range
            value = max(0.0, min(2.0, value))
            self.glow_strength = value
            self.glow_strength_slider.set(value)
            self.glow_strength_entry.delete(0, "end")
            self.glow_strength_entry.insert(0, f"{value:.2f}")
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.glow_strength_entry.delete(0, "end")
            self.glow_strength_entry.insert(0,f"{self.glow_strength:.2f}")

    def _on_glow_color(self, value):
        """Handle glow color hue slider change.
        
        Clears any direct RGB override and uses hue-based coloring.
        """
        self.last_slider = self.glow_color_slider
        self.glow_color_hue = float(value)
        # Clear direct RGB override when using hue slider
        if hasattr(self, '_glow_direct_rgb'):
            delattr(self, '_glow_direct_rgb')
        # Update color preview and RGB entries
        color = self._get_solid_color(self.glow_color_hue)
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        self.glow_color_preview.configure(fg_color=hex_color)
        # Update RGB entries
        self.glow_r_entry.delete(0, "end")
        self.glow_r_entry.insert(0, str(color[0]))
        self.glow_g_entry.delete(0, "end")
        self.glow_g_entry.insert(0, str(color[1]))
        self.glow_b_entry.delete(0, "end")
        self.glow_b_entry.insert(0, str(color[2]))
        self._debounced_update()

    def _on_glow_color_mouse_release(self):
        """Snap glow color hue to 0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.glow_color_hue) < 5:
            self.glow_color_hue = 0.0
            self.glow_color_slider.set(0.0)
            color = self._get_solid_color(self.glow_color_hue)
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.glow_color_preview.configure(fg_color=hex_color)
            self.glow_r_entry.delete(0, "end")
            self.glow_r_entry.insert(0, str(color[0]))
            self.glow_g_entry.delete(0, "end")
            self.glow_g_entry.insert(0, str(color[1]))
            self.glow_b_entry.delete(0, "end")
            self.glow_b_entry.insert(0, str(color[2]))
            self._debounced_update()

    def _on_glow_rgb_changed(self):
        """Handle glow RGB entry field change.
        
        Sets direct RGB override for glow color and updates slider display.
        """
        try:
            r = int(self.glow_r_entry.get())
            g = int(self.glow_g_entry.get())
            b = int(self.glow_b_entry.get())
            # Clamp to valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Store direct RGB values for glow
            if not hasattr(self, '_glow_direct_rgb'):
                self._glow_direct_rgb = True
            self.glow_color_hue = -1  # Special flag for direct RGB
            self._glow_rgb = (r, g, b)
            
            # Convert RGB to hue for slider display (but don't use for rendering)
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = h * 360
            
            # Temporarily disconnect callback to prevent overwriting RGB entries
            self.glow_color_slider.configure(command=None)
            self.glow_color_slider.set(hue)
            self.glow_color_slider.configure(command=self._on_glow_color)
            
            # Update color preview with exact RGB
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.glow_color_preview.configure(fg_color=hex_color)
            
            # Update entries with clamped values
            self.glow_r_entry.delete(0, "end")
            self.glow_r_entry.insert(0, str(r))
            self.glow_g_entry.delete(0, "end")
            self.glow_g_entry.insert(0, str(g))
            self.glow_b_entry.delete(0, "end")
            self.glow_b_entry.insert(0, str(b))
            
            self._debounced_update()
        except ValueError:
            # Restore previous values if invalid input
            if hasattr(self, '_glow_rgb'):
                r, g, b = self._glow_rgb
                self.glow_r_entry.delete(0, "end")
                self.glow_r_entry.insert(0, str(r))
                self.glow_g_entry.delete(0, "end")
                self.glow_g_entry.insert(0, str(g))
                self.glow_b_entry.delete(0, "end")
                self.glow_b_entry.insert(0, str(b))
            else:
                color = self._get_solid_color(self.glow_color_hue)
                self.glow_r_entry.delete(0, "end")
                self.glow_r_entry.insert(0, str(color[0]))
                self.glow_g_entry.delete(0, "end")
                self.glow_g_entry.insert(0, str(color[1]))
                self.glow_b_entry.delete(0, "end")
                self.glow_b_entry.insert(0, str(color[2]))

    def _on_glow_size(self, value):
        """Handle glow size/radius slider change."""
        self.last_slider = self.glow_size_slider
        self.glow_size = int(value)
        # Update entry field
        self.glow_size_entry.delete(0, "end")
        self.glow_size_entry.insert(0, str(self.glow_size))
        self._debounced_update()

    def _on_glow_size_mouse_release(self):
        """Snap glow size to 5 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.glow_size - 5) < 1:
            self.glow_size = 5
            self.glow_size_slider.set(5)
            self.glow_size_entry.delete(0, "end")
            self.glow_size_entry.insert(0, str(self.glow_size))
            self._debounced_update()

    def _on_glow_size_entry_changed(self):
        """Handle glow size entry field change.
        
        Validates input and clamps to valid range (1-10).
        """
        try:
            value = int(self.glow_size_entry.get())
            # Clamp to valid range
            value = max(1, min(10, value))
            self.glow_size = value
            self.glow_size_slider.set(value)
            self.glow_size_entry.delete(0, "end")
            self.glow_size_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.glow_size_entry.delete(0, "end")
            self.glow_size_entry.insert(0, str(self.glow_size))

    def _on_zoom(self, value):
        """Handle zoom level slider change."""
        self.last_slider = self.zoom_slider
        self.zoom_level = int(value)
        self._debounced_update()

    def _on_x_offset(self, value):
        """Handle horizontal image offset slider change."""
        self.last_slider = self.x_slider
        self.offset_x = int(value)
        self._debounced_update()

    def _on_y_offset(self, value):
        """Handle vertical image offset slider change."""
        self.last_slider = self.y_slider
        self.offset_y = int(value)
        self._debounced_update()

    def _on_stretch_x(self, value):
        """Handle horizontal stretch slider change."""
        self.last_slider = self.stretch_x_slider
        self.stretch_x = float(value)
        # Update entry field
        self.stretch_x_entry.delete(0, "end")
        self.stretch_x_entry.insert(0, f"{self.stretch_x:.2f}")
        self._debounced_update()

    def _on_stretch_x_mouse_release(self):
        """Snap horizontal stretch to 1.0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.stretch_x - 1.0) < 0.05:
            self.stretch_x = 1.0
            self.stretch_x_slider.set(1.0)
            self.stretch_x_entry.delete(0, "end")
            self.stretch_x_entry.insert(0, f"{self.stretch_x:.2f}")
            self._debounced_update()

    def _on_stretch_x_entry_changed(self):
        """Handle horizontal stretch entry field change.
        
        Validates input and clamps to valid range (0.5 to 2.0).
        """
        try:
            value = float(self.stretch_x_entry.get())
            # Clamp to valid range
            value = max(0.5, min(2.0, value))
            self.stretch_x = value
            self.stretch_x_slider.set(value)
            self.stretch_x_entry.delete(0, "end")
            self.stretch_x_entry.insert(0, f"{value:.2f}")
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.stretch_x_entry.delete(0, "end")
            self.stretch_x_entry.insert(0, f"{self.stretch_x:.2f}")

    def _on_stretch_y(self, value):
        """Handle vertical stretch slider change."""
        self.last_slider = self.stretch_y_slider
        self.stretch_y = float(value)
        # Update entry field
        self.stretch_y_entry.delete(0, "end")
        self.stretch_y_entry.insert(0, f"{self.stretch_y:.2f}")
        self._debounced_update()

    def _on_stretch_y_mouse_release(self):
        """Snap vertical stretch to 1.0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.stretch_y - 1.0) < 0.05:
            self.stretch_y = 1.0
            self.stretch_y_slider.set(1.0)
            self.stretch_y_entry.delete(0, "end")
            self.stretch_y_entry.insert(0, f"{self.stretch_y:.2f}")
            self._debounced_update()

    def _on_stretch_y_entry_changed(self):
        """Handle vertical stretch entry field change.
        
        Validates input and clamps to valid range (0.5 to 2.0).
        """
        try:
            value = float(self.stretch_y_entry.get())
            # Clamp to valid range
            value = max(0.5, min(2.0, value))
            self.stretch_y = value
            self.stretch_y_slider.set(value)
            self.stretch_y_entry.delete(0, "end")
            self.stretch_y_entry.insert(0, f"{value:.2f}")
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.stretch_y_entry.delete(0, "end")
            self.stretch_y_entry.insert(0, f"{self.stretch_y:.2f}")

    def _on_brightness(self, value):
        """Handle main image brightness slider change."""
        self.last_slider = self.brightness_slider
        self.brightness = float(value)
        # Update entry field
        self.brightness_entry.delete(0, "end")
        self.brightness_entry.insert(0, f"{self.brightness:.2f}")
        self._debounced_update()

    def _on_brightness_mouse_release(self):
        """Snap brightness to 0.9 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.brightness - 0.9) < 0.05:
            self.brightness = 0.9
            self.brightness_slider.set(0.9)
            self.brightness_entry.delete(0, "end")
            self.brightness_entry.insert(0, f"{self.brightness:.2f}")
            self._debounced_update()

    def _on_brightness_entry_changed(self):
        """Handle brightness entry field change.
        
        Validates input and clamps to valid range (0.1 to 2.0).
        """
        try:
            value = float(self.brightness_entry.get())
            # Clamp to valid range
            value = max(0.1, min(2.0, value))
            self.brightness = value
            self.brightness_slider.set(value)
            self.brightness_entry.delete(0, "end")
            self.brightness_entry.insert(0, f"{value:.2f}")
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.brightness_entry.delete(0, "end")
            self.brightness_entry.insert(0, f"{self.brightness:.2f}")

    def _on_zoom(self, value):
        """Handle zoom level slider change with entry field update."""
        self.last_slider = self.zoom_slider
        self.zoom_level = int(value)
        # Update entry field
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, str(self.zoom_level))
        self._debounced_update()

    def _on_zoom_mouse_release(self):
        """Snap zoom level to 50 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.zoom_level - 50) < 5:
            self.zoom_level = 50
            self.zoom_slider.set(50)
            self.zoom_entry.delete(0, "end")
            self.zoom_entry.insert(0, str(self.zoom_level))
            self._debounced_update()

    def _on_zoom_entry_changed(self):
        """Handle zoom level entry field change.
        
        Validates input and clamps to valid range (-100 to 200).
        """
        try:
            value = int(self.zoom_entry.get())
            # Clamp to valid range
            value = max(-100, min(200, value))
            self.zoom_level = value
            self.zoom_slider.set(value)
            self.zoom_entry.delete(0, "end")
            self.zoom_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.zoom_entry.delete(0, "end")
            self.zoom_entry.insert(0, str(self.zoom_level))

    def _on_x_offset(self, value):
        """Handle horizontal image offset slider change with entry field update."""
        self.last_slider = self.x_slider
        self.offset_x = int(value)
        # Update entry field
        self.x_entry.delete(0, "end")
        self.x_entry.insert(0, str(self.offset_x))
        self._debounced_update()

    def _on_x_offset_mouse_release(self):
        """Snap horizontal offset to 0 when close to center on mouse release."""
        # Check for snap when mouse is released
        if abs(self.offset_x) < 5:
            self.offset_x = 0
            self.x_slider.set(0)
            self.x_entry.delete(0, "end")
            self.x_entry.insert(0, str(self.offset_x))
            self._debounced_update()

    def _on_x_entry_changed(self):
        """Handle horizontal offset entry field change.
        
        Validates input and clamps to valid range (-140 to 140).
        """
        try:
            value = int(self.x_entry.get())
            # Clamp to valid range
            value = max(-140, min(140, value))
            self.offset_x = value
            self.x_slider.set(value)
            self.x_entry.delete(0, "end")
            self.x_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.x_entry.delete(0, "end")
            self.x_entry.insert(0, str(self.offset_x))

    def _on_y_offset(self, value):
        """Handle vertical image offset slider change with entry field update."""
        self.last_slider = self.y_slider
        self.offset_y = int(value)
        # Update entry field
        self.y_entry.delete(0, "end")
        self.y_entry.insert(0, str(self.offset_y))
        self._debounced_update()

    def _on_y_offset_mouse_release(self):
        """Snap vertical offset to 0 when close to center on mouse release."""
        # Check for snap when mouse is released
        if abs(self.offset_y) < 5:
            self.offset_y = 0
            self.y_slider.set(0)
            self.y_entry.delete(0, "end")
            self.y_entry.insert(0, str(self.offset_y))
            self._debounced_update()

    def _on_y_entry_changed(self):
        """Handle vertical offset entry field change.
        
        Validates input and clamps to valid range (-140 to 140).
        """
        try:
            value = int(self.y_entry.get())
            # Clamp to valid range
            value = max(-140, min(140, value))
            self.offset_y = value
            self.y_slider.set(value)
            self.y_entry.delete(0, "end")
            self.y_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.y_entry.delete(0, "end")
            self.y_entry.insert(0, str(self.offset_y))

    def _on_hue(self, value):
        """Handle text hue slider change for active text lines.
        
        Updates hue for all active lines and clears any direct RGB overrides.
        """
        self.last_slider = self.hue_slider
        for i in range(3):
            if self.line_active[i]:
                self.line_hues[i] = float(value)
                # Clear direct RGB override for this line
                if hasattr(self, '_direct_rgb') and i in self._direct_rgb:
                    del self._direct_rgb[i]
        active_idx = next((i for i, a in enumerate(self.line_active) if a), 0)
        color = self._get_solid_color(self.line_hues[active_idx])
        hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        self.color_preview.configure(fg_color=hex_color)
        # Update RGB entries
        self.text_r_entry.delete(0, "end")
        self.text_r_entry.insert(0, str(color[0]))
        self.text_g_entry.delete(0, "end")
        self.text_g_entry.insert(0, str(color[1]))
        self.text_b_entry.delete(0, "end")
        self.text_b_entry.insert(0, str(color[2]))
        self._debounced_update()

    def _on_text_rgb_changed(self):
        """Handle text RGB entry field change.
        
        Sets direct RGB override for all active text lines.
        """
        try:
            r = int(self.text_r_entry.get())
            g = int(self.text_g_entry.get())
            b = int(self.text_b_entry.get())
            # Clamp to valid range
            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))
            
            # Store exact RGB values in a special override for active lines
            for i in range(3):
                if self.line_active[i]:
                    self.line_hues[i] = -1  # Special flag for direct RGB
                    # Store the RGB values in a temp attribute
                    if not hasattr(self, '_direct_rgb'):
                        self._direct_rgb = {}
                    self._direct_rgb[i] = (r, g, b)
            
            # Convert RGB to hue for slider display (but don't use for rendering)
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = h * 360
            
            # Temporarily disconnect callback to prevent overwriting RGB entries
            self.hue_slider.configure(command=None)
            self.hue_slider.set(hue)
            self.hue_slider.configure(command=self._on_hue)
            
            # Update color preview with exact RGB
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.color_preview.configure(fg_color=hex_color)
            
            # Update entries with clamped values
            self.text_r_entry.delete(0, "end")
            self.text_r_entry.insert(0, str(r))
            self.text_g_entry.delete(0, "end")
            self.text_g_entry.insert(0, str(g))
            self.text_b_entry.delete(0, "end")
            self.text_b_entry.insert(0, str(b))
            
            self._debounced_update()
        except ValueError:
            # Restore previous values if invalid input
            active_idx = next((i for i, a in enumerate(self.line_active) if a), 0)
            color = self._get_solid_color(self.line_hues[active_idx])
            self.text_r_entry.delete(0, "end")
            self.text_r_entry.insert(0, str(color[0]))
            self.text_g_entry.delete(0, "end")
            self.text_g_entry.insert(0, str(color[1]))
            self.text_b_entry.delete(0, "end")
            self.text_b_entry.insert(0, str(color[2]))

    def _on_opacity(self, value):
        """Handle CRT scanline opacity slider change."""
        self.last_slider = self.opacity_slider
        self.scanline_alpha = int(value)
        self.opacity_entry.delete(0, "end")
        self.opacity_entry.insert(0, str(self.scanline_alpha))
        self._debounced_update()

    def _on_opacity_mouse_release(self):
        """Snap scanline opacity to 20 when close to default on mouse release."""
        if abs(self.scanline_alpha - 20) < 5:
            self.scanline_alpha = 20
            self.opacity_slider.set(20)
            self.opacity_entry.delete(0, "end")
            self.opacity_entry.insert(0, "20")
            self._debounced_update()

    def _on_opacity_entry_changed(self):
        """Handle scanline opacity entry field change.
        
        Validates input and clamps to valid range (0-100).
        """
        try:
            value = int(self.opacity_entry.get())
            value = max(0, min(100, value))
            self.scanline_alpha = value
            self.opacity_slider.set(value)
            self.opacity_entry.delete(0, "end")
            self.opacity_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            self.opacity_entry.delete(0, "end")
            self.opacity_entry.insert(0, str(self.scanline_alpha))

    def _on_bg_scale(self, value):
        """Handle background scale slider change."""
        self.last_slider = self.bg_scale_slider
        self.bg_scale = float(value)
        self._debounced_update()

    def _on_bg_offset_x(self, value):
        """Handle background horizontal offset slider change."""
        self.last_slider = self.bg_offset_x_slider
        self.bg_offset_x = int(value)
        self._debounced_update()

    def _on_bg_offset_y(self, value):
        """Handle background vertical offset slider change."""
        self.last_slider = self.bg_offset_y_slider
        self.bg_offset_y = int(value)
        self._debounced_update()

    def _on_frame_offset_x(self, value):
        """Handle frame/border horizontal offset slider change."""
        self.last_slider = self.frame_offset_x_slider
        self.frame_offset_x = int(value)
        self._debounced_update()

    def _on_frame_offset_y(self, value):
        """Handle frame/border vertical offset slider change."""
        self.last_slider = self.frame_offset_y_slider
        self.frame_offset_y = int(value)
        self._debounced_update()

    def _on_decor_scale(self, value):
        """Handle decoration scale slider change."""
        self.last_slider = self.decor_scale_slider
        self.decor_scale = float(value)
        # Update entry field
        self.decor_scale_entry.delete(0, "end")
        self.decor_scale_entry.insert(0, f"{self.decor_scale:.2f}")
        self._debounced_update()

    def _on_decor_scale_mouse_release(self):
        """Snap decoration scale to 1.0 when close to default on mouse release."""
        # Check for snap when mouse is released
        if abs(self.decor_scale - 1.0) < 0.05:
            self.decor_scale = 1.0
            self.decor_scale_slider.set(1.0)
            self.decor_scale_entry.delete(0, "end")
            self.decor_scale_entry.insert(0, f"{self.decor_scale:.2f}")
            self._debounced_update()

    def _on_decor_scale_entry_changed(self):
        """Handle decoration scale entry field change.
        
        Validates input and clamps to valid range (0.5 to 2.0).
        """
        try:
            value = float(self.decor_scale_entry.get())
            # Clamp to valid range
            value = max(0.5, min(2.0, value))
            self.decor_scale = value
            self.decor_scale_slider.set(value)
            self.decor_scale_entry.delete(0, "end")
            self.decor_scale_entry.insert(0, f"{value:.2f}")
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.decor_scale_entry.delete(0, "end")
            self.decor_scale_entry.insert(0, f"{self.decor_scale:.2f}")

    def _on_decor_pos_x(self, value):
        """Handle decoration horizontal position slider change."""
        self.last_slider = self.decor_offset_x_slider
        self.decor_offset_x = int(value)
        # Update entry field
        self.decor_offset_x_entry.delete(0, "end")
        self.decor_offset_x_entry.insert(0, str(self.decor_offset_x))
        self._debounced_update()

    def _on_decor_pos_x_mouse_release(self):
        """Snap decoration horizontal position to 0 when close to center on mouse release."""
        # Check for snap when mouse is released
        if abs(self.decor_offset_x) < 2:
            self.decor_offset_x = 0
            self.decor_offset_x_slider.set(0)
            self.decor_offset_x_entry.delete(0, "end")
            self.decor_offset_x_entry.insert(0, str(self.decor_offset_x))
            self._debounced_update()

    def _on_decor_pos_x_entry_changed(self):
        """Handle decoration horizontal position entry field change.
        
        Validates input and clamps to valid range (-30 to 30).
        """
        try:
            value = int(self.decor_offset_x_entry.get())
            # Clamp to valid range
            value = max(-30, min(30, value))
            self.decor_offset_x = value
            self.decor_offset_x_slider.set(value)
            self.decor_offset_x_entry.delete(0, "end")
            self.decor_offset_x_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.decor_offset_x_entry.delete(0, "end")
            self.decor_offset_x_entry.insert(0, str(self.decor_offset_x))

    def _on_decor_pos_y(self, value):
        """Handle decoration vertical position slider change."""
        self.last_slider = self.decor_offset_y_slider
        self.decor_offset_y = int(value)
        # Update entry field
        self.decor_offset_y_entry.delete(0, "end")
        self.decor_offset_y_entry.insert(0, str(self.decor_offset_y))
        self._debounced_update()

    def _on_decor_pos_y_mouse_release(self):
        """Snap decoration vertical position to 0 when close to center on mouse release."""
        # Check for snap when mouse is released
        if abs(self.decor_offset_y) < 2:
            self.decor_offset_y = 0
            self.decor_offset_y_slider.set(0)
            self.decor_offset_y_entry.delete(0, "end")
            self.decor_offset_y_entry.insert(0, str(self.decor_offset_y))
            self._debounced_update()

    def _on_decor_pos_y_entry_changed(self):
        """Handle decoration vertical position entry field change.
        
        Validates input and clamps to valid range (-30 to 30).
        """
        try:
            value = int(self.decor_offset_y_entry.get())
            # Clamp to valid range
            value = max(-30, min(30, value))
            self.decor_offset_y = value
            self.decor_offset_y_slider.set(value)
            self.decor_offset_y_entry.delete(0, "end")
            self.decor_offset_y_entry.insert(0, str(value))
            self._debounced_update()
        except ValueError:
            # Restore previous value if invalid input
            self.decor_offset_y_entry.delete(0, "end")
            self.decor_offset_y_entry.insert(0, str(self.decor_offset_y))

    def _keyboard_slider_left(self, event=None):
        """Decrease the last-used slider by one step using keyboard.
        
        Allows keyboard control of sliders for accessibility.
        """
        if self.last_slider is None: return
        val = self.last_slider.get()
        from_val = self.last_slider.cget("from_")
        to_val = self.last_slider.cget("to")
        steps = self.last_slider.cget("number_of_steps") or 1
        step = (to_val - from_val) / steps
        new_val = max(from_val, val - step)
        self.last_slider.set(new_val)
        cmd = self.last_slider.cget("command")
        if callable(cmd): cmd(new_val)

    def _keyboard_slider_right(self, event=None):
        """Increase the last-used slider by one step using keyboard.
        
        Allows keyboard control of sliders for accessibility.
        """
        if self.last_slider is None: return
        val = self.last_slider.get()
        from_val = self.last_slider.cget("from_")
        to_val = self.last_slider.cget("to")
        steps = self.last_slider.cget("number_of_steps") or 1
        step = (to_val - from_val) / steps
        new_val = min(to_val, val + step)
        self.last_slider.set(new_val)
        cmd = self.last_slider.cget("command")
        if callable(cmd): cmd(new_val)

    def _on_curve(self):
        """Handle curve toggle (currently disabled/not implemented)."""
        self.curve_enabled = False
        self._debounced_update()

    def _on_crt(self):
        """Toggle CRT scanline effect and show/hide controls."""
        self.crt_enabled = self.crt_var.get()
        if self.crt_var.get():
            if hasattr(self, 'scanline_controls_frame'):
                self.scanline_controls_frame.pack(fill="x", padx=15, pady=(0,12), after=self.crt_checkbox)
        else:
            if hasattr(self, 'scanline_controls_frame'):
                self.scanline_controls_frame.pack_forget()
        if hasattr(self, 'opacity_slider'):
            self.opacity_slider.configure(state="normal" if self.crt_enabled else "disabled")
        self._debounced_update()

    def _hide_background_selector(self):
        """Hide the background navigation arrows and label."""
        self.bg_left_arrow.grid_remove()
        self.bg_label.grid_remove()
        self.bg_right_arrow.grid_remove()

    def _show_background_selector(self):
        """Show the background navigation arrows and label."""
        self.bg_left_arrow.grid()
        self.bg_label.grid()
        self.bg_right_arrow.grid()

    def _get_text_color(self, line_idx, use_data=None):
        """Get text color for a specific line, checking for direct RGB override.
        
        Args:
            line_idx: Index of the text line (0-2)
            use_data: Data object containing color settings (self or template data)
            
        Returns:
            RGB color tuple for the text
        """
        if use_data is None:
            use_data = self
        
        # Check if we have direct RGB values for this line (main app or template data)
        if hasattr(use_data, '_direct_rgb') and line_idx in use_data._direct_rgb:
            rgb = use_data._direct_rgb[line_idx]
            # Ensure RGB values are integers and in valid range
            return tuple(max(0, min(255, int(c))) for c in rgb)
        # Otherwise use hue-based color
        return self._get_solid_color(use_data.line_hues[line_idx])

    def _get_glow_color(self, use_data=None):
        """Get glow color, checking for direct RGB override.
        
        Args:
            use_data: Data object containing glow color settings (self or template data)
            
        Returns:
            RGB color tuple for the glow effect
        """
        if use_data is None:
            use_data = self
        
        # Check if we have direct RGB values for glow (only for main app)
        if use_data is self and hasattr(self, '_glow_direct_rgb') and hasattr(self, '_glow_rgb'):
            return tuple(max(0, min(255, int(c))) for c in self._glow_rgb)
        # Otherwise use hue-based color
        return self._get_solid_color(use_data.glow_color_hue)

    def _get_solid_color(self, value):
        """Convert a hue value (0-360) to an RGB color tuple.
        
        Uses a custom color palette with vibrant colors for text and effects.
        The palette transitions through yellow, orange, red, magenta, blue, cyan, and gray.
        
        Args:
            value: Hue value in degrees (0-360)
            
        Returns:
            RGB color tuple (r, g, b) with values 0-255
        """
        t = max(0.0, min(1.0, value / 360.0))
        if t < 0.25:
            tt = t / 0.25
            return (255, max(0, min(255, int(255 * (1 - tt * 0.6)))), max(0, min(255, int(255 * (1 - tt * 0.15)))))
        elif t < 0.45:
            tt = (t - 0.25) / 0.20
            return (255, max(0, min(255, int(153 * (1 - tt)))), max(0, min(255, int(204 * (1 - tt)))))
        elif t < 0.65:
            tt = (t - 0.45) / 0.20
            return (255, max(0, min(255, int(tt * 255))), 0)
        elif t < 0.80:
            tt = (t - 0.65) / 0.15
            return (max(0, min(255, int(255 * (1 - tt)))), 255, max(0, min(255, int(tt * 255))))
        elif t < 0.90:
            tt = (t - 0.80) / 0.10
            return (max(0, min(255, int(255 * (1 - tt * 2)))), max(0, min(255, int(255 * (1 - tt * 1.5)))), 255)
        else:
            tt = (t - 0.90) / 0.10
            gray = max(0, min(255, int(200 * (1 - tt))))
            return (gray, gray, gray)

    def _hue_to_rgb(self, hue):
        """Convert a hue value (0-360) to an RGB color tuple using standard HSV to RGB.
        
        Uses the standard 6-segment HSV color wheel conversion.
        
        Args:
            hue: Hue value in degrees (0-360)
            
        Returns:
            RGB color tuple (r, g, b) with values 0-255
        """
        h = hue / 360.0
        i = int(h * 6)
        f = h * 6 - i
        if i == 0: return (255, int(255*f), 0)
        if i == 1: return (int(255*(1-f)), 255, 0)
        if i == 2: return (0, 255, int(255*f))
        if i == 3: return (0, int(255*(1-f)), 255)
        if i == 4: return (int(255*f), 0, 255)
        return (255, 0, int(255*(1-f)))

    def _get_scale(self):
        """Convert zoom level to image scale factor.
        
        Maps zoom level (-100 to 200) to scale factor (0.2 to 2.0).
        
        Returns:
            Scale factor as a float
        """
        return 0.2 + ((self.zoom_level + 100) / 200.0) * 1.8

    def _precompute_distortion_map(self):
        """Precompute a radial distortion map for image warping effects.
        
        Creates a lookup table mapping each pixel to its source position
        based on radial distance from the distortion center. Used for
        barrel/pincushion distortion effects.
        """
        distortion_map = []
        sx = self.curve_strength_x
        sy = self.curve_strength_y
        cx = self.distortion_center_x
        cy = self.distortion_center_y
        for y in range(HEIGHT):
            row = []
            for x in range(WIDTH):
                dx = (x - WIDTH * cx) / (WIDTH / 2)
                dy = (y - HEIGHT * cy) / (HEIGHT / 2)
                r = math.sqrt(dx * dx + dy * dy)
                factor_x = 1 + sx * r * r
                factor_y = 1 + sy * r * r
                src_x = max(0, min(WIDTH - 1, int(WIDTH * cx + dx * factor_x * (WIDTH / 2))))
                src_y = max(0, min(HEIGHT - 1, int(HEIGHT * cy + dy * factor_y * (HEIGHT / 2))))
                row.append((src_x, src_y))
            distortion_map.append(row)
        self.distortion_map = distortion_map

    def _apply_fast_distortion(self, img):
        """Apply the precomputed distortion map to an image.
        
        Uses the distortion map lookup table to warp the image pixels.
        
        Args:
            img: PIL Image to distort
            
        Returns:
            Distorted PIL Image
        """
        result = Image.new("RGBA", img.size, (0, 0, 0, 0))
        w, h = img.size
        pixels = img.load()
        out = result.load()
        for y in range(h):
            for x in range(w):
                sx, sy = self.distortion_map[y % HEIGHT][x % WIDTH]
                sx = max(0, min(w - 1, sx))
                sy = max(0, min(h - 1, sy))
                out[x, y] = pixels[sx, sy]
        return result

    def _build_ui(self):
        # More compact and responsive UI
        main = ctk.CTkFrame(self, fg_color="#1a1a1a")
        main.pack(fill="both", expand=True, padx=5, pady=5)
        main.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=0)

        left = ctk.CTkFrame(main, fg_color="#1a1a1a")
        left.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="nsew")

        self.status_label = ctk.CTkLabel(left, text="", font=("Arial", 14, "bold"), text_color="#2ecc71")
        self.status_label.pack(pady=(0, 8))

        preview_box = ctk.CTkFrame(left, fg_color="#1a1a1a")
        preview_box.pack(pady=5)
        self.preview_label = ctk.CTkLabel(preview_box, text="")
        self.preview_label.grid(row=0, column=0, padx=(0, 10))

        button_stack = ctk.CTkFrame(preview_box, fg_color="#1a1a1a")
        button_stack.grid(row=0, column=1, sticky="n")

        ctk.CTkButton(button_stack, text="Upload Image", fg_color="#3498db", hover_color="#2980b9", height=40, corner_radius=8, font=("Arial", 12, "bold"), command=self._load_image).pack(pady=(0, 6), fill="x")
        ctk.CTkButton(button_stack, text="Save", fg_color="#2ecc71", hover_color="#27ae60", height=40, corner_radius=8, font=("Arial", 12, "bold"), command=self._save_image).pack(pady=(0, 6), fill="x")
        ctk.CTkButton(button_stack, text="Templates", fg_color="#3498db", hover_color="#2980b9", height=40, corner_radius=8, font=("Arial", 12, "bold"), command=self._open_template_popup).pack(pady=(0, 6), fill="x")
        ctk.CTkButton(button_stack, text="Reset", fg_color="#e74c3c", hover_color="#c0392b", height=40, corner_radius=8, font=("Arial", 12, "bold"), command=self._reset_to_default).pack(fill="x")
        ctk.CTkButton(button_stack, text="Randomize", fg_color="#ff69b4", hover_color="#ff1493", height=40, corner_radius=8, font=("Arial", 12, "bold"), command=self._randomize_settings).pack(fill="x", pady=(6,0))
        # Preserve original size checkbox
        self.preserve_var = ctk.BooleanVar(value=True)
        self.preserve_checkbox = ctk.CTkCheckBox(
            button_stack, 
            text="Preserve Original Size on Re-upload",
            variable=self.preserve_var,
            command=lambda: setattr(self, 'preserve_original_size', self.preserve_var.get()),
            font=("Arial", 11)
        )
        self.preserve_checkbox.pack(pady=(8, 0), anchor="w")
        # Search functionality
        search_frame = ctk.CTkFrame(button_stack, fg_color="#1a1a1a")
        search_frame.pack(fill="x", pady=(10, 0))
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search keyword...", height=30, font=("Arial", 10))
        self.search_entry.pack(fill="x", pady=(0, 5))
        
        search_btn_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_btn_frame.pack(fill="x")
        
        ctk.CTkButton(search_btn_frame, text="Search For Img", fg_color="#3498db", hover_color="#2980b9", height=30, corner_radius=6, font=("Arial", 10, "bold"), command=self._search_for_image).pack(fill="x")

        # Text input box moved here - right under search functionality
        text_box_frame = ctk.CTkFrame(button_stack, fg_color="#1a1a1a")
        text_box_frame.pack(fill="x", pady=(10, 0))
        
        # Single paragraph text box - smaller
        self.paragraph_entry = ctk.CTkTextbox(text_box_frame, width=110, height=65, font=("Arial", 12), 
                                          border_width=2, border_color="#3498db", corner_radius=6,
                                          fg_color="#2b2b2b", text_color="#ffffff",
                                          scrollbar_button_color="#3498db", scrollbar_button_hover_color="#2980b9")
        self.paragraph_entry.pack(fill="x", expand=True)
        self.paragraph_entry.bind("<KeyRelease>", self._on_paragraph_change)
        self.paragraph_entry.bind("<KeyPress>", self._on_paragraph_key_press)
        self.paragraph_entry.bind("<Return>", self._on_paragraph_enter)

        # Keep the line toggle buttons for controlling individual lines - smaller
        self.line_toggle_buttons = []
        toggle_frame = ctk.CTkFrame(text_box_frame, fg_color="transparent")
        toggle_frame.pack(fill="x", pady=2)
        for i in range(3):
            toggle = ctk.CTkButton(toggle_frame, text=f"L{i+1}", width=22, height=22, corner_radius=3, fg_color="#00ff00" if self.line_active[i] else "#555555", hover_color="#00cc00", command=lambda idx=i: self._toggle_line(idx))
            toggle.pack(side="left", padx=1)
            self.line_toggle_buttons.append(toggle)

        # Background Generator button
        ctk.CTkButton(button_stack, text="Background Generator", fg_color="#9b59b6", hover_color="#8e44ad", height=40, corner_radius=8, font=("Arial", 12, "bold"), command=self._open_background_generator).pack(fill="x", pady=(10, 0))

        arrows_frame = ctk.CTkFrame(left, fg_color="#1a1a1a")
        arrows_frame.pack(pady=5)
        control_frame = ctk.CTkFrame(arrows_frame, fg_color="#1a1a1a")
        control_frame.pack(side="left", padx=(0, 15))
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        control_frame.columnconfigure(2, weight=1)
        self.bg_left_arrow = self._create_repeatable_arrow(control_frame, self.arrow_left, self._prev_background, 0, 0)
        self.bg_label = ctk.CTkLabel(control_frame, text="Background: 1", font=("Arial", 10))
        self.bg_label.grid(row=0, column=1, padx=8, pady=2)
        self.bg_right_arrow = self._create_repeatable_arrow(control_frame, self.arrow_right, self._next_background, 0, 2)
        self._create_repeatable_arrow(control_frame, self.arrow_left, self._prev_frame, 1, 0)
        self.frame_label = ctk.CTkLabel(control_frame, text="Frame: 1", font=("Arial", 10))
        self.frame_label.grid(row=1, column=1, padx=8, pady=2)
        self._create_repeatable_arrow(control_frame, self.arrow_right, self._next_frame, 1, 2)
        self._create_repeatable_arrow(control_frame, self.arrow_left, self._prev_font, 2, 0)
        self.font_label = ctk.CTkLabel(control_frame, text="Font: VT323-Regular", font=("Arial", 10))
        self.font_label.grid(row=2, column=1, padx=8, pady=2)
        self._create_repeatable_arrow(control_frame, self.arrow_right, self._next_font, 2, 2)
        self._create_repeatable_arrow(control_frame, self.arrow_left, self._decrease_font_size, 3, 0)
        self.font_size_label = ctk.CTkLabel(control_frame, text="Font Size: 44px", font=("Arial", 10))
        self.font_size_label.grid(row=3, column=1, padx=8, pady=2)
        self._create_repeatable_arrow(control_frame, self.arrow_right, self._increase_font_size, 3, 2)
        self._create_repeatable_arrow(control_frame, self.arrow_left, self._decrease_font_spacing, 4, 0)
        self.font_spacing_label = ctk.CTkLabel(control_frame, text="Font Spacing: 0px", font=("Arial", 10))
        self.font_spacing_label.grid(row=4, column=1, padx=8, pady=2)
        self._create_repeatable_arrow(control_frame, self.arrow_right, self._increase_font_spacing, 4, 2)
        self._create_repeatable_arrow(control_frame, self.arrow_left, self._decrease_line_spacing, 5, 0)
        self.line_spacing_label = ctk.CTkLabel(control_frame, text="Line Spacing: 0px", font=("Arial", 10))
        self.line_spacing_label.grid(row=5, column=1, padx=8, pady=2)
        self._create_repeatable_arrow(control_frame, self.arrow_right, self._increase_line_spacing, 5, 2)

        font_pos_frame = ctk.CTkFrame(arrows_frame, fg_color="#1a1a1a")
        font_pos_frame.pack(side="left")
        ctk.CTkLabel(font_pos_frame, text="Font Position", font=("Arial", 10)).pack(pady=(0, 2))
        arrow_container = ctk.CTkFrame(font_pos_frame, fg_color="#1a1a1a")
        arrow_container.pack()
        arrow_container.columnconfigure((0,1,2), weight=1)
        arrow_container.rowconfigure((0,1,2), weight=1)
        self._create_repeatable_arrow(arrow_container, self.arrow_left, self._move_text_left, 1, 0, width=25, height=25, padx=1, pady=1)
        self._create_repeatable_arrow(arrow_container, self.arrow_up, self._move_text_up, 0, 1, width=25, height=25, padx=1, pady=1)
        self._create_repeatable_arrow(arrow_container, self.arrow_down, self._move_text_down, 2, 1, width=25, height=25, padx=1, pady=1)
        self._create_repeatable_arrow(arrow_container, self.arrow_right, self._move_text_right, 1, 2, width=25, height=25, padx=1, pady=1)
        self.step_button = ctk.CTkButton(arrow_container, text="Step", width=45, height=28, fg_color="#e74c3c", hover_color="#c0392b", font=ctk.CTkFont(family="VT323", size=12, weight="bold"), command=self._cycle_position_step)
        self.step_button.grid(row=1, column=1, padx=1, pady=1)

        img_pos_frame = ctk.CTkFrame(arrows_frame, fg_color="#1a1a1a")
        img_pos_frame.pack(side="left", padx=(15, 0))
        ctk.CTkLabel(img_pos_frame, text="Image Position", font=("Arial", 10)).pack(pady=(0, 2))
        img_arrow_container = ctk.CTkFrame(img_pos_frame, fg_color="#1a1a1a")
        img_arrow_container.pack()
        img_arrow_container.columnconfigure((0,1,2), weight=1)
        img_arrow_container.rowconfigure((0,1,2), weight=1)
        self._create_repeatable_arrow(img_arrow_container, self.arrow_left, self._move_image_left, 1, 0, width=25, height=25, padx=1, pady=1)
        self._create_repeatable_arrow(img_arrow_container, self.arrow_up, self._move_image_up, 0, 1, width=25, height=25, padx=1, pady=1)
        self._create_repeatable_arrow(img_arrow_container, self.arrow_down, self._move_image_down, 2, 1, width=25, height=25, padx=1, pady=1)
        self._create_repeatable_arrow(img_arrow_container, self.arrow_right, self._move_image_right, 1, 2, width=25, height=25, padx=1, pady=1)
        self.image_step_button = ctk.CTkButton(img_arrow_container, text="1px", width=45, height=28, fg_color="#3498db", hover_color="#2980b9", font=ctk.CTkFont(family="VT323", size=12, weight="bold"), command=self._cycle_image_position_step)
        self.image_step_button.grid(row=1, column=1, padx=1, pady=1)

        # Create right panel with single column - more compact with scrollable frame
        right_container = ctk.CTkFrame(main, fg_color="#1a1a1a")
        right_container.grid(row=0, column=1, padx=(5, 5), pady=5, sticky="nsew")
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)

        # Single scrollable frame for all settings
        right_panel = ctk.CTkScrollableFrame(right_container, fg_color="#2d2d2d", scrollbar_button_color="#3498db", scrollbar_button_hover_color="#2980b9", width=340)
        right_panel.grid(row=0, column=0, sticky="nsew")
        right_panel.rowconfigure(0, weight=1)

        def add_header(text, color="#3498db"):
            header_frame = ctk.CTkFrame(right_panel, fg_color=color, corner_radius=8)
            header_frame.pack(fill="x", padx=10, pady=(12, 8))
            lbl = ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(size=13, weight="bold"), text_color="white")
            lbl.pack(padx=10, pady=8)

        add_header("Image Settings", color="#3498db")
        # Image Brightness - more compact
        img_bright_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        img_bright_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(img_bright_frame, text="Brightness", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.brightness_slider = ctk.CTkSlider(img_bright_frame, from_=0.1, to=2.0, number_of_steps=190, command=self._on_brightness, progress_color="#3498db")
        self.brightness_slider.set(0.9)
        self.brightness_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.brightness_slider.bind("<ButtonRelease-1>", lambda e: self._on_brightness_mouse_release())
        self.brightness_entry = ctk.CTkEntry(img_bright_frame, width=50, justify="center", font=("Arial", 9))
        self.brightness_entry.grid(row=1, column=1, sticky="e")
        self.brightness_entry.insert(0, "0.90")
        self.brightness_entry.bind("<Return>", lambda e: self._on_brightness_entry_changed())
        self.brightness_entry.bind("<FocusOut>", lambda e: self._on_brightness_entry_changed())
        img_bright_frame.columnconfigure(0, weight=1)

        # Image Zoom - more compact
        img_zoom_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        img_zoom_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(img_zoom_frame, text="Zoom", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.zoom_slider = ctk.CTkSlider(img_zoom_frame, from_=-100, to=200, number_of_steps=300, command=self._on_zoom, progress_color="#e74c3c")
        self.zoom_slider.set(50)
        self.zoom_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.zoom_slider.bind("<ButtonRelease-1>", lambda e: self._on_zoom_mouse_release())
        self.zoom_entry = ctk.CTkEntry(img_zoom_frame, width=50, justify="center", font=("Arial", 9))
        self.zoom_entry.grid(row=1, column=1, sticky="e")
        self.zoom_entry.insert(0, "50")
        self.zoom_entry.bind("<Return>", lambda e: self._on_zoom_entry_changed())
        self.zoom_entry.bind("<FocusOut>", lambda e: self._on_zoom_entry_changed())
        img_zoom_frame.columnconfigure(0, weight=1)

        # Image X Offset - more compact
        img_x_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        img_x_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(img_x_frame, text="X Offset", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.x_slider = ctk.CTkSlider(img_x_frame, from_=-140, to=140, number_of_steps=280, command=self._on_x_offset, progress_color="#2ecc71")
        self.x_slider.set(0)
        self.x_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.x_slider.bind("<ButtonRelease-1>", lambda e: self._on_x_offset_mouse_release())
        self.x_entry = ctk.CTkEntry(img_x_frame, width=50, justify="center", font=("Arial", 9))
        self.x_entry.grid(row=1, column=1, sticky="e")
        self.x_entry.insert(0, "0")
        self.x_entry.bind("<Return>", lambda e: self._on_x_entry_changed())
        self.x_entry.bind("<FocusOut>", lambda e: self._on_x_entry_changed())
        img_x_frame.columnconfigure(0, weight=1)

        # Image Y Offset - more compact
        img_y_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        img_y_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(img_y_frame, text="Y Offset", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.y_slider = ctk.CTkSlider(img_y_frame, from_=-140, to=140, number_of_steps=280, command=self._on_y_offset, progress_color="#2ecc71")
        self.y_slider.set(0)
        self.y_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.y_slider.bind("<ButtonRelease-1>", lambda e: self._on_y_offset_mouse_release())
        self.y_entry = ctk.CTkEntry(img_y_frame, width=50, justify="center", font=("Arial", 9))
        self.y_entry.grid(row=1, column=1, sticky="e")
        self.y_entry.insert(0, "0")
        self.y_entry.bind("<Return>", lambda e: self._on_y_entry_changed())
        self.y_entry.bind("<FocusOut>", lambda e: self._on_y_entry_changed())
        img_y_frame.columnconfigure(0, weight=1)

        # Image Stretch X - more compact
        stretch_x_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        stretch_x_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(stretch_x_frame, text="Stretch X", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.stretch_x_slider = ctk.CTkSlider(stretch_x_frame, from_=0.5, to=2.0, number_of_steps=150, command=self._on_stretch_x, progress_color="#f39c12")
        self.stretch_x_slider.set(1.0)
        self.stretch_x_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.stretch_x_slider.bind("<ButtonRelease-1>", lambda e: self._on_stretch_x_mouse_release())
        self.stretch_x_entry = ctk.CTkEntry(stretch_x_frame, width=50, justify="center", font=("Arial", 9))
        self.stretch_x_entry.grid(row=1, column=1, sticky="e")
        self.stretch_x_entry.insert(0, "1.00")
        self.stretch_x_entry.bind("<Return>", lambda e: self._on_stretch_x_entry_changed())
        self.stretch_x_entry.bind("<FocusOut>", lambda e: self._on_stretch_x_entry_changed())
        stretch_x_frame.columnconfigure(0, weight=1)

        # Image Stretch Y - more compact
        stretch_y_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        stretch_y_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(stretch_y_frame, text="Stretch Y", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.stretch_y_slider = ctk.CTkSlider(stretch_y_frame, from_=0.5, to=2.0, number_of_steps=150, command=self._on_stretch_y, progress_color="#f39c12")
        self.stretch_y_slider.set(1.0)
        self.stretch_y_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.stretch_y_slider.bind("<ButtonRelease-1>", lambda e: self._on_stretch_y_mouse_release())
        self.stretch_y_entry = ctk.CTkEntry(stretch_y_frame, width=50, justify="center", font=("Arial", 9))
        self.stretch_y_entry.grid(row=1, column=1, sticky="e")
        self.stretch_y_entry.insert(0, "1.00")
        self.stretch_y_entry.bind("<Return>", lambda e: self._on_stretch_y_entry_changed())
        self.stretch_y_entry.bind("<FocusOut>", lambda e: self._on_stretch_y_entry_changed())
        stretch_y_frame.columnconfigure(0, weight=1)

        add_header("Background & Border", color="#e67e22")
        
        # Background Brightness - more compact
        bg_bright_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        bg_bright_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(bg_bright_frame, text="BG Brightness", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.bg_brightness_slider = ctk.CTkSlider(bg_bright_frame, from_=-100, to=200, number_of_steps=300, command=self._on_bg_brightness, progress_color="#9b59b6")
        self.bg_brightness_slider.set(0)
        self.bg_brightness_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.bg_brightness_slider.bind("<ButtonRelease-1>", lambda e: self._on_bg_brightness_mouse_release())
        self.bg_brightness_entry = ctk.CTkEntry(bg_bright_frame, width=50, justify="center", font=("Arial", 9))
        self.bg_brightness_entry.grid(row=1, column=1, sticky="e")
        self.bg_brightness_entry.insert(0, "1.00")
        self.bg_brightness_entry.bind("<Return>", lambda e: self._on_bg_brightness_entry_changed())
        self.bg_brightness_entry.bind("<FocusOut>", lambda e: self._on_bg_brightness_entry_changed())
        bg_bright_frame.columnconfigure(0, weight=1)

        # Background Hue - more compact
        bg_hue_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        bg_hue_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(bg_hue_frame, text="BG Hue", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        
        # Create slider row with color preview - smaller
        bg_hue_slider_row = ctk.CTkFrame(bg_hue_frame, fg_color="transparent")
        bg_hue_slider_row.grid(row=1, column=0, sticky="ew", padx=(0,55))
        bg_hue_slider_row.columnconfigure(0, weight=1)
        
        self.bg_hue_slider = ctk.CTkSlider(bg_hue_slider_row, from_=0, to=360, number_of_steps=360, command=self._on_bg_hue, progress_color="#e67e22")
        self.bg_hue_slider.set(0)
        self.bg_hue_slider.grid(row=0, column=0, sticky="ew", padx=(0,6))
        self.bg_hue_slider.bind("<ButtonRelease-1>", lambda e: self._on_bg_hue_mouse_release())
        
        self.bg_hue_preview = ctk.CTkLabel(bg_hue_slider_row, text="", width=25, height=25, corner_radius=6)
        self.bg_hue_preview.grid(row=0, column=1, padx=(0,6))
        
        # RGB entry fields for background - smaller
        bg_rgb_frame = ctk.CTkFrame(bg_hue_frame, fg_color="transparent")
        bg_rgb_frame.grid(row=1, column=1, sticky="e")
        
        self.bg_r_entry = ctk.CTkEntry(bg_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.bg_r_entry.grid(row=0, column=0, padx=1)
        self.bg_r_entry.insert(0, "255")
        self.bg_r_entry.bind("<Return>", lambda e: self._on_bg_rgb_changed())
        self.bg_r_entry.bind("<FocusOut>", lambda e: self._on_bg_rgb_changed())
        
        self.bg_g_entry = ctk.CTkEntry(bg_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.bg_g_entry.grid(row=0, column=1, padx=1)
        self.bg_g_entry.insert(0, "255")
        self.bg_g_entry.bind("<Return>", lambda e: self._on_bg_rgb_changed())
        self.bg_g_entry.bind("<FocusOut>", lambda e: self._on_bg_rgb_changed())
        
        self.bg_b_entry = ctk.CTkEntry(bg_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.bg_b_entry.grid(row=0, column=2, padx=1)
        self.bg_b_entry.insert(0, "255")
        self.bg_b_entry.bind("<Return>", lambda e: self._on_bg_rgb_changed())
        self.bg_b_entry.bind("<FocusOut>", lambda e: self._on_bg_rgb_changed())
        
        bg_hue_frame.columnconfigure(0, weight=1)

        # Border Hue - more compact
        border_hue_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        border_hue_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(border_hue_frame, text="Border Hue", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        
        # Create slider row with color preview - smaller
        border_hue_slider_row = ctk.CTkFrame(border_hue_frame, fg_color="transparent")
        border_hue_slider_row.grid(row=1, column=0, sticky="ew", padx=(0,55))
        border_hue_slider_row.columnconfigure(0, weight=1)
        
        self.border_hue_slider = ctk.CTkSlider(border_hue_slider_row, from_=0, to=360, number_of_steps=360, command=self._on_border_hue, progress_color="#95a5a6")
        self.border_hue_slider.set(0)
        self.border_hue_slider.grid(row=0, column=0, sticky="ew", padx=(0,6))
        self.border_hue_slider.bind("<ButtonRelease-1>", lambda e: self._on_border_hue_mouse_release())
        
        self.border_hue_preview = ctk.CTkLabel(border_hue_slider_row, text="", width=25, height=25, corner_radius=6)
        self.border_hue_preview.grid(row=0, column=1, padx=(0,6))
        
        # RGB entry fields for border - smaller
        border_rgb_frame = ctk.CTkFrame(border_hue_frame, fg_color="transparent")
        border_rgb_frame.grid(row=1, column=1, sticky="e")
        
        self.border_r_entry = ctk.CTkEntry(border_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.border_r_entry.grid(row=0, column=0, padx=1)
        self.border_r_entry.insert(0, "255")
        self.border_r_entry.bind("<Return>", lambda e: self._on_border_rgb_changed())
        self.border_r_entry.bind("<FocusOut>", lambda e: self._on_border_rgb_changed())
        
        self.border_g_entry = ctk.CTkEntry(border_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.border_g_entry.grid(row=0, column=1, padx=1)
        self.border_g_entry.insert(0, "255")
        self.border_g_entry.bind("<Return>", lambda e: self._on_border_rgb_changed())
        self.border_g_entry.bind("<FocusOut>", lambda e: self._on_border_rgb_changed())
        
        self.border_b_entry = ctk.CTkEntry(border_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.border_b_entry.grid(row=0, column=2, padx=1)
        self.border_b_entry.insert(0, "255")
        self.border_b_entry.bind("<Return>", lambda e: self._on_border_rgb_changed())
        self.border_b_entry.bind("<FocusOut>", lambda e: self._on_border_rgb_changed())
        
        border_hue_frame.columnconfigure(0, weight=1)

        # Shadow Opacity - more compact
        shadow_opacity_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        shadow_opacity_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(shadow_opacity_frame, text="Shadow Opacity", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.shadow_opacity_slider = ctk.CTkSlider(shadow_opacity_frame, from_=0, to=100, number_of_steps=100, command=self._on_shadow_opacity, progress_color="#34495e")
        self.shadow_opacity_slider.set(100)
        self.shadow_opacity_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.shadow_opacity_slider.bind("<ButtonRelease-1>", lambda e: self._on_shadow_opacity_mouse_release())
        self.shadow_opacity_entry = ctk.CTkEntry(shadow_opacity_frame, width=50, justify="center", font=("Arial", 9))
        self.shadow_opacity_entry.grid(row=1, column=1, sticky="e")
        self.shadow_opacity_entry.insert(0, "100")
        self.shadow_opacity_entry.bind("<Return>", lambda e: self._on_shadow_opacity_entry_changed())
        self.shadow_opacity_entry.bind("<FocusOut>", lambda e: self._on_shadow_opacity_entry_changed())
        shadow_opacity_frame.columnconfigure(0, weight=1)

        add_header("Text Settings", color="#e74c3c")
        hue_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        hue_frame.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(hue_frame, text="Text Color", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        
        # Create slider row with color preview - smaller
        hue_slider_row = ctk.CTkFrame(hue_frame, fg_color="transparent")
        hue_slider_row.grid(row=1, column=0, sticky="ew", padx=(0,55))
        hue_slider_row.columnconfigure(0, weight=1)
        
        self.hue_slider = ctk.CTkSlider(hue_slider_row, from_=0, to=360, number_of_steps=360, command=self._on_hue, progress_color="#3498db")
        self.hue_slider.set(0)
        self.hue_slider.grid(row=0, column=0, sticky="ew", padx=(0,6))
        
        self.color_preview = ctk.CTkLabel(hue_slider_row, text="", width=25, height=25, corner_radius=6)
        self.color_preview.grid(row=0, column=1, padx=(0,6))
        
        # RGB entry fields for text color - smaller
        text_rgb_frame = ctk.CTkFrame(hue_frame, fg_color="transparent")
        text_rgb_frame.grid(row=1, column=1, sticky="e")
        
        self.text_r_entry = ctk.CTkEntry(text_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.text_r_entry.grid(row=0, column=0, padx=1)
        self.text_r_entry.insert(0, "255")
        self.text_r_entry.bind("<Return>", lambda e: self._on_text_rgb_changed())
        self.text_r_entry.bind("<FocusOut>", lambda e: self._on_text_rgb_changed())
        
        self.text_g_entry = ctk.CTkEntry(text_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.text_g_entry.grid(row=0, column=1, padx=1)
        self.text_g_entry.insert(0, "255")
        self.text_g_entry.bind("<Return>", lambda e: self._on_text_rgb_changed())
        self.text_g_entry.bind("<FocusOut>", lambda e: self._on_text_rgb_changed())
        
        self.text_b_entry = ctk.CTkEntry(text_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.text_b_entry.grid(row=0, column=2, padx=1)
        self.text_b_entry.insert(0, "255")
        self.text_b_entry.bind("<Return>", lambda e: self._on_text_rgb_changed())
        self.text_b_entry.bind("<FocusOut>", lambda e: self._on_text_rgb_changed())
        
        hue_frame.columnconfigure(0, weight=1)

        ctk.CTkCheckBox(right_panel, text="Rainbow Text", variable=self.rainbow_var, command=self._on_rainbow_toggle, font=("Arial", 9)).pack(anchor="w", padx=10, pady=1)
        ctk.CTkCheckBox(right_panel, text="Text Outline", variable=self.outline_var, command=self._on_outline_toggle, font=("Arial", 9)).pack(anchor="w", padx=10, pady=1)
        self.glow_checkbox = ctk.CTkCheckBox(right_panel, text="Glow Text", variable=self.glow_var, command=self._on_glow_toggle, font=("Arial", 9))
        self.glow_checkbox.pack(anchor="w", padx=10, pady=1)
        self.glow_controls_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a1a")
        self.glow_controls_frame.pack(fill="x", padx=10, pady=(0,8))
        self.glow_controls_frame.columnconfigure(0, weight=1)
        # Glow Strength - more compact
        glow_strength_frame = ctk.CTkFrame(self.glow_controls_frame, fg_color="transparent")
        glow_strength_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,3))
        ctk.CTkLabel(glow_strength_frame, text="Glow Strength", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.glow_strength_slider = ctk.CTkSlider(glow_strength_frame, from_=0.0, to=2.0, number_of_steps=40, command=self._on_glow_strength, progress_color="#ff69b4")
        self.glow_strength_slider.set(self.glow_strength)
        self.glow_strength_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.glow_strength_slider.bind("<ButtonRelease-1>", lambda e: self._on_glow_strength_mouse_release())
        self.glow_strength_entry = ctk.CTkEntry(glow_strength_frame, width=50, justify="center", font=("Arial", 9))
        self.glow_strength_entry.grid(row=1, column=1, sticky="e")
        self.glow_strength_entry.insert(0, f"{self.glow_strength:.2f}")
        self.glow_strength_entry.bind("<Return>", lambda e: self._on_glow_strength_entry_changed())
        self.glow_strength_entry.bind("<FocusOut>", lambda e: self._on_glow_strength_entry_changed())
        glow_strength_frame.columnconfigure(0, weight=1)

        # Glow Color - more compact
        glow_color_frame = ctk.CTkFrame(self.glow_controls_frame, fg_color="transparent")
        glow_color_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0,3))
        ctk.CTkLabel(glow_color_frame, text="Glow Color", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        
        # Create slider row with color preview - smaller
        glow_color_slider_row = ctk.CTkFrame(glow_color_frame, fg_color="transparent")
        glow_color_slider_row.grid(row=1, column=0, sticky="ew", padx=(0,55))
        glow_color_slider_row.columnconfigure(0, weight=1)
        
        self.glow_color_slider = ctk.CTkSlider(glow_color_slider_row, from_=0, to=360, number_of_steps=360, command=self._on_glow_color, progress_color="#ff1493")
        self.glow_color_slider.set(self.glow_color_hue)
        self.glow_color_slider.grid(row=0, column=0, sticky="ew", padx=(0,6))
        
        self.glow_color_preview = ctk.CTkLabel(glow_color_slider_row, text="", width=25, height=25, corner_radius=6)
        self.glow_color_preview.grid(row=0, column=1, padx=(0,6))
        
        # RGB entry fields for glow color - smaller
        glow_rgb_frame = ctk.CTkFrame(glow_color_frame, fg_color="transparent")
        glow_rgb_frame.grid(row=1, column=1, sticky="e")
        
        self.glow_r_entry = ctk.CTkEntry(glow_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.glow_r_entry.grid(row=0, column=0, padx=1)
        self.glow_r_entry.insert(0, "255")
        self.glow_r_entry.bind("<Return>", lambda e: self._on_glow_rgb_changed())
        self.glow_r_entry.bind("<FocusOut>", lambda e: self._on_glow_rgb_changed())
        
        self.glow_g_entry = ctk.CTkEntry(glow_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.glow_g_entry.grid(row=0, column=1, padx=1)
        self.glow_g_entry.insert(0, "255")
        self.glow_g_entry.bind("<Return>", lambda e: self._on_glow_rgb_changed())
        self.glow_g_entry.bind("<FocusOut>", lambda e: self._on_glow_rgb_changed())
        
        self.glow_b_entry = ctk.CTkEntry(glow_rgb_frame, width=28, justify="center", font=("Arial", 8))
        self.glow_b_entry.grid(row=0, column=2, padx=1)
        self.glow_b_entry.insert(0, "255")
        self.glow_b_entry.bind("<Return>", lambda e: self._on_glow_rgb_changed())
        self.glow_b_entry.bind("<FocusOut>", lambda e: self._on_glow_rgb_changed())
        
        glow_color_frame.columnconfigure(0, weight=1)

        # Glow Size - more compact
        glow_size_frame = ctk.CTkFrame(self.glow_controls_frame, fg_color="transparent")
        glow_size_frame.grid(row=5, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(glow_size_frame, text="Glow Size", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.glow_size_slider = ctk.CTkSlider(glow_size_frame, from_=1, to=10, number_of_steps=10, command=self._on_glow_size, progress_color="#ff69b4")
        self.glow_size_slider.set(self.glow_size)
        self.glow_size_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.glow_size_slider.bind("<ButtonRelease-1>", lambda e: self._on_glow_size_mouse_release())
        self.glow_size_entry = ctk.CTkEntry(glow_size_frame, width=50, justify="center", font=("Arial", 9))
        self.glow_size_entry.grid(row=1, column=1, sticky="e")
        self.glow_size_entry.insert(0, str(self.glow_size))
        self.glow_size_entry.bind("<Return>", lambda e: self._on_glow_size_entry_changed())
        self.glow_size_entry.bind("<FocusOut>", lambda e: self._on_glow_size_entry_changed())
        glow_size_frame.columnconfigure(0, weight=1)
        self.glow_controls_frame.pack_forget()

        
        add_header("CRT Effects", color="#16a085")
        self.crt_var = ctk.BooleanVar(value=True)
        self.crt_checkbox = ctk.CTkCheckBox(right_panel, text="CRT Scanlines", variable=self.crt_var, command=self._on_crt, font=("Arial", 9))
        self.crt_checkbox.pack(anchor="w", padx=10, pady=2)
        self.scanline_controls_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a1a")
        self.scanline_controls_frame.columnconfigure(0, weight=1)
        self.scanline_controls_frame.pack(fill="x", padx=10, pady=(0,8))
        
        # Scanline Opacity
        scan_opacity_frame = ctk.CTkFrame(self.scanline_controls_frame, fg_color="transparent")
        scan_opacity_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        ctk.CTkLabel(scan_opacity_frame, text="Opacity", font=("Arial", 9)).grid(row=0, column=0, sticky="w")
        self.opacity_slider = ctk.CTkSlider(scan_opacity_frame, from_=0, to=100, number_of_steps=100, command=self._on_opacity, progress_color="#16a085")
        self.opacity_slider.set(20)
        self.opacity_slider.grid(row=1, column=0, sticky="ew", padx=(0,55))
        self.opacity_slider.bind("<ButtonRelease-1>", lambda e: self._on_opacity_mouse_release())
        self.opacity_entry = ctk.CTkEntry(scan_opacity_frame, width=50, justify="center", font=("Arial", 9))
        self.opacity_entry.grid(row=1, column=1, sticky="e")
        self.opacity_entry.insert(0, "20")
        self.opacity_entry.bind("<Return>", lambda e: self._on_opacity_entry_changed())
        self.opacity_entry.bind("<FocusOut>", lambda e: self._on_opacity_entry_changed())
        scan_opacity_frame.columnconfigure(0, weight=1)
        self.scanline_controls_frame.pack_forget()
        self.curve_var = ctk.BooleanVar(value=False)

        add_header("Decoration Settings", color="#27ae60")
        self.decor_var = ctk.BooleanVar(value=True)
        self.decor_checkbox = ctk.CTkCheckBox(right_panel, text="Show Decoration (Bottom Right)", variable=self.decor_var, command=self._on_decor_toggle, font=("Arial", 9))
        self.decor_checkbox.pack(anchor="w", padx=10, pady=2)
        
        self.decor_controls_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a1a")
        self.decor_controls_frame.columnconfigure(0, weight=1)
        self.decor_controls_frame.columnconfigure(1, weight=1)
        self.decor_controls_frame.columnconfigure(2, weight=1)
        
        self._create_repeatable_arrow(self.decor_controls_frame, self.arrow_left, self._prev_decor, 0, 0, width=40, height=28, padx=4)
        self.decor_label = ctk.CTkLabel(self.decor_controls_frame, text="Decor: 1", font=self.retro_label_font)
        self.decor_label.grid(row=0, column=1, padx=8)
        self._create_repeatable_arrow(self.decor_controls_frame, self.arrow_right, self._next_decor, 0, 2, width=40, height=28, padx=4)
        
        ctk.CTkLabel(self.decor_controls_frame, text="Decor Scale", font=("Arial", 9)).grid(row=1, column=0, sticky="w", columnspan=3, pady=(8,0))
        
        # Decor Scale - updated to match new style
        decor_scale_frame = ctk.CTkFrame(self.decor_controls_frame, fg_color="transparent")
        decor_scale_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,8))
        decor_scale_frame.columnconfigure(0, weight=1)
        self.decor_scale_slider = ctk.CTkSlider(decor_scale_frame, from_=0.5, to=2.0, number_of_steps=150, command=self._on_decor_scale, progress_color="#27ae60")
        self.decor_scale_slider.set(1.0)
        self.decor_scale_slider.grid(row=0, column=0, sticky="ew", padx=(0,55))
        self.decor_scale_slider.bind("<ButtonRelease-1>", lambda e: self._on_decor_scale_mouse_release())
        self.decor_scale_entry = ctk.CTkEntry(decor_scale_frame, width=50, justify="center", font=("Arial", 9))
        self.decor_scale_entry.grid(row=0, column=1, sticky="e")
        self.decor_scale_entry.insert(0, "1.00")
        self.decor_scale_entry.bind("<Return>", lambda e: self._on_decor_scale_entry_changed())
        self.decor_scale_entry.bind("<FocusOut>", lambda e: self._on_decor_scale_entry_changed())
        
        ctk.CTkLabel(self.decor_controls_frame, text="Decor Position X", font=("Arial", 9)).grid(row=3, column=0, sticky="w", columnspan=3)
        
        # Decor Position X - updated to match new style
        decor_pos_x_frame = ctk.CTkFrame(self.decor_controls_frame, fg_color="transparent")
        decor_pos_x_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,8))
        decor_pos_x_frame.columnconfigure(0, weight=1)
        self.decor_offset_x_slider = ctk.CTkSlider(decor_pos_x_frame, from_=-30, to=30, number_of_steps=60, command=self._on_decor_pos_x, progress_color="#27ae60")
        self.decor_offset_x_slider.set(0)
        self.decor_offset_x_slider.grid(row=0, column=0, sticky="ew", padx=(0,55))
        self.decor_offset_x_slider.bind("<ButtonRelease-1>", lambda e: self._on_decor_pos_x_mouse_release())
        self.decor_offset_x_entry = ctk.CTkEntry(decor_pos_x_frame, width=50, justify="center", font=("Arial", 9))
        self.decor_offset_x_entry.grid(row=0, column=1, sticky="e")
        self.decor_offset_x_entry.insert(0, "0")
        self.decor_offset_x_entry.bind("<Return>", lambda e: self._on_decor_pos_x_entry_changed())
        self.decor_offset_x_entry.bind("<FocusOut>", lambda e: self._on_decor_pos_x_entry_changed())
        
        ctk.CTkLabel(self.decor_controls_frame, text="Decor Position Y", font=("Arial", 9)).grid(row=5, column=0, sticky="w", columnspan=3)
        
        # Decor Position Y - updated to match new style
        decor_pos_y_frame = ctk.CTkFrame(self.decor_controls_frame, fg_color="transparent")
        decor_pos_y_frame.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=(0,8))
        decor_pos_y_frame.columnconfigure(0, weight=1)
        self.decor_offset_y_slider = ctk.CTkSlider(decor_pos_y_frame, from_=-30, to=30, number_of_steps=60, command=self._on_decor_pos_y, progress_color="#27ae60")
        self.decor_offset_y_slider.set(0)
        self.decor_offset_y_slider.grid(row=0, column=0, sticky="ew", padx=(0,55))
        self.decor_offset_y_slider.bind("<ButtonRelease-1>", lambda e: self._on_decor_pos_y_mouse_release())
        self.decor_offset_y_entry = ctk.CTkEntry(decor_pos_y_frame, width=50, justify="center", font=("Arial", 9))
        self.decor_offset_y_entry.grid(row=0, column=1, sticky="e")
        self.decor_offset_y_entry.insert(0, "0")
        self.decor_offset_y_entry.bind("<Return>", lambda e: self._on_decor_pos_y_entry_changed())
        self.decor_offset_y_entry.bind("<FocusOut>", lambda e: self._on_decor_pos_y_entry_changed())
        
        self.decor_controls_frame.pack_forget()

    def _update_dynamic_labels(self):
        """Update UI labels to show current asset selections and font settings."""
        self.bg_label.configure(text=f"Background: {self.current_bg_index + 1}")
        self.frame_label.configure(text=f"Frame: {self.current_frame_index + 1}")
        if self.font_files:
            name = os.path.splitext(self.font_files[self.current_font_index])[0]
            self.font_label.configure(text=f"Font: {name}")
        else:
            self.font_label.configure(text="Font: Default")
        if self.decor_files:
            name = os.path.splitext(self.decor_files[self.current_decor_index])[0]
            self.decor_label.configure(text=f"Decor: {self.current_decor_index + 1} ({name})")
        else:
            self.decor_label.configure(text="Decor: None")
        num_lines = len([l for l in self.title_lines if l])
        base_size = 44 if num_lines == 1 else 38 if num_lines == 2 else 32
        px = max(20, min(500, base_size + self.line_font_size_offsets[0]))
        self.font_size_label.configure(text=f"Font Size: {px}px")
        self.font_spacing_label.configure(text=f"Font Spacing: {self.line_font_spacing_offsets[0]}px")
        self.line_spacing_label.configure(text=f"Line Spacing: {self.line_spacing_offset}px")

    def _toggle_line(self, idx):
        """Toggle visibility of a specific text line.
        
        Args:
            idx: Line index (0-2)
        """
        self.line_active[idx] = not self.line_active[idx]
        self.line_toggle_buttons[idx].configure(fg_color="#00ff00" if self.line_active[idx] else "#555555")
        self._debounced_update()

    def _get_filename_base(self):
        """Generate a safe filename base from the text lines.
        
        Returns:
            Sanitized filename string with only alphanumeric characters and underscores
        """
        lines = [l.strip() for l in self.title_lines if l.strip()]
        if not lines:
            return "snes-icon"
        raw = "_".join(lines)
        return "".join(c for c in raw if c.isalnum() or c in "_-") or "snes-icon"

    def _save_image(self):
        """Save the current icon as PNG or ICO.
        
        Renders the final image and shows a popup with save options.
        """
        try:
            # Render the final image
            final_img = self._composite_image(for_preview=False)
            
            # Generate a base name from all active text lines
            active_lines = [line.strip() for line in self.title_lines if line.strip()]
            if active_lines:
                # Join all active lines with underscore
                base_name = "_".join(active_lines)
            else:
                base_name = "Icon"
            
            # Clean up the filename to remove invalid characters
            base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            base_name = base_name.replace(' ', '_')
            if not base_name:
                base_name = "Icon"
            
            # Don't check for duplicates here - let the individual save functions handle it
            # This way PNG and ICO can have different duplicate logic
            
            # Show the save popup
            self._show_save_popup(final_img, base_name)
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save image: {str(e)}")

    def _show_save_popup(self, final_img, base_name):
        """Show the save options popup with image preview.
        
        Args:
            final_img: The rendered PIL Image to save
            base_name: Base filename for the saved file
        """
        try:
            # Create a completely new image copy to avoid reference issues
            new_img = Image.new("RGBA", final_img.size, (0, 0, 0, 0))
            new_img.paste(final_img)
            
            # Create popup after a short delay to avoid UI conflicts
            self.after(100, lambda: self._create_save_popup(new_img, base_name))
            
        except Exception as e:
            # Fallback to simple messagebox
            try:
                choice = messagebox.askyesno("Save Options", "Save as PNG only? (Yes=PNG, No=PNG+ICO)")
                if choice:
                    self._save_png_only(final_img, base_name, None)
                else:
                    self._save_as_icon(final_img, base_name, None)
            except:
                pass

    def _create_save_popup(self, final_img, base_name):
        """Create and display the save options popup window.
        
        Shows a preview of the icon and buttons to save as PNG or ICO.
        """
        try:
            popup = ctk.CTkToplevel(self)
            popup.title("Save Options")
            popup.geometry("500x450")
            popup.resizable(False, False)
            popup.transient(self)
            popup.lift()
            popup.focus_force()
            popup.grab_set()
            
            # Center the popup on screen
            popup.update_idletasks()
            width = popup.winfo_width()
            height = popup.winfo_height()
            x = (popup.winfo_screenwidth() // 2) - (width // 2)
            y = (popup.winfo_screenheight() // 2) - (height // 2)
            popup.geometry(f'{width}x{height}+{x}+{y}')

            # Add message
            message_label = ctk.CTkLabel(popup, text=f"Save '{base_name}' as:", font=("Arial", 14))
            message_label.pack(pady=20)

            # Add preview image with fresh CTkImage
            preview_size = (150, 150)
            preview_img = final_img.resize(preview_size, Image.Resampling.LANCZOS)
            preview_ctk = ctk.CTkImage(light_image=preview_img, size=preview_size)
            img_label = ctk.CTkLabel(popup, image=preview_ctk, text="")
            img_label.pack(pady=10)

            # Button frame with more padding
            btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
            btn_frame.pack(pady=30)

            def save_png():
                self._save_png_only(final_img, base_name, popup)

            def save_icon():
                self._save_as_icon(final_img, base_name, popup)

            def cancel():
                popup.destroy()

            # Create buttons with specific text and more spacing
            ctk.CTkButton(btn_frame, text="Save as PNG", fg_color="#2ecc71", hover_color="#27ae60", 
                         width=150, height=45, font=("Arial", 12, "bold"), command=save_png).pack(pady=8)
            
            ctk.CTkButton(btn_frame, text="Save as Icon", fg_color="#9b59b6", hover_color="#8e44ad", 
                         width=150, height=45, font=("Arial", 12, "bold"), command=save_icon).pack(pady=8)
            
            ctk.CTkButton(btn_frame, text="Cancel", fg_color="#e74c3c", hover_color="#c0392b", 
                         width=150, height=45, font=("Arial", 12, "bold"), command=cancel).pack(pady=8)

        except Exception as e:
            # Fallback to direct save
            self._save_png_only(final_img, base_name, None)

    def _save_png_only(self, final_img, base_name, popup):
        """Save as PNG only and open folder"""
        self._play_sound("keep.wav")
        try:
            icons_dir = os.path.join(SCRIPT_DIR, "Icons")
            os.makedirs(icons_dir, exist_ok=True)
            
            # Check for PNG duplicate and add Copy# if needed
            png_path = os.path.join(icons_dir, f"{base_name}.png")
            if os.path.exists(png_path):
                # Find next available copy number for PNG
                copy_num = 1
                while True:
                    test_name = f"{base_name}_Copy{copy_num}"
                    test_path = os.path.join(icons_dir, f"{test_name}.png")
                    if not os.path.exists(test_path):
                        base_name = test_name
                        break
                    copy_num += 1
                png_path = os.path.join(icons_dir, f"{base_name}.png")
            
            final_img.save(png_path, "PNG")
            
            # Open the folder
            import subprocess
            import platform
            if platform.system() == "Windows":
                subprocess.run(["explorer", icons_dir])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", icons_dir])
            else:  # Linux
                subprocess.run(["xdg-open", icons_dir])
            
            # Also save original image to storage if exists
            if self.game_img_orig is not None:
                today_str = datetime.date.today().strftime("%Y%m%d")
                storage_filename = f"{base_name}_{today_str}.png"
                storage_path = os.path.join(STORAGE_DIR, storage_filename)
                img_to_save = self.game_img_orig.copy()
                if max(img_to_save.size) > 512:
                    img_to_save.thumbnail((512, 512), Image.Resampling.LANCZOS)
                img_to_save.save(storage_path, "PNG")
                for f in os.listdir(STORAGE_DIR):
                    if f.startswith(base_name + "_") and f.endswith(".png") and f != storage_filename:
                        try:
                            os.remove(os.path.join(STORAGE_DIR, f))
                        except:
                            pass
            
            original_color = self.cget("fg_color")
            self.configure(fg_color="#ffffcc")
            self.after(80, lambda: self.configure(fg_color=original_color))
            self.show_save_confirmation(base_name)
            if popup:
                popup.destroy()
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save PNG: {str(e)}")

    def _save_as_icon(self, final_img, base_name, popup):
        """Save as ICO file with multiple sizes and open folder.
        
        Creates an ICO file with resolutions from 16x16 to 256x256 for
        Windows icon compatibility. Also saves the original image to storage.
        """
        self._play_sound("keep.wav")
        try:
            icons_dir = os.path.join(SCRIPT_DIR, "Icons")
            os.makedirs(icons_dir, exist_ok=True)
            
            # Check for ICO duplicate and add Copy# if needed
            ico_path = os.path.join(icons_dir, f"{base_name}.ico")
            ico_base_name = base_name
            if os.path.exists(ico_path):
                # Find next available copy number for ICO
                copy_num = 1
                while True:
                    test_name = f"{base_name}_Copy{copy_num}"
                    test_path = os.path.join(icons_dir, f"{test_name}.ico")
                    if not os.path.exists(test_path):
                        ico_base_name = test_name
                        break
                    copy_num += 1
                ico_path = os.path.join(icons_dir, f"{ico_base_name}.ico")
            
            # Create .ico file with multiple sizes for Windows 11
            sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
            icon_images = []
            
            for size in sizes:
                # Resize image maintaining quality
                resized_img = final_img.resize(size, Image.Resampling.LANCZOS)
                icon_images.append(resized_img)
            
            # Save as .ico with all sizes
            icon_images[0].save(ico_path, format="ICO", sizes=sizes)
            
            # Open the folder
            import subprocess
            import platform
            if platform.system() == "Windows":
                subprocess.run(["explorer", icons_dir])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", icons_dir])
            else:  # Linux
                subprocess.run(["xdg-open", icons_dir])
            
            # Also save original image to storage if exists
            if self.game_img_orig is not None:
                today_str = datetime.date.today().strftime("%Y%m%d")
                storage_filename = f"{base_name}_{today_str}.png"
                storage_path = os.path.join(STORAGE_DIR, storage_filename)
                img_to_save = self.game_img_orig.copy()
                if max(img_to_save.size) > 512:
                    img_to_save.thumbnail((512, 512), Image.Resampling.LANCZOS)
                img_to_save.save(storage_path, "PNG")
                for f in os.listdir(STORAGE_DIR):
                    if f.startswith(base_name + "_") and f.endswith(".png") and f != storage_filename:
                        try:
                            os.remove(os.path.join(STORAGE_DIR, f))
                        except:
                            pass
            
            original_color = self.cget("fg_color")
            self.configure(fg_color="#ffffcc")
            self.after(80, lambda: self.configure(fg_color=original_color))
            self.show_save_confirmation(f"{ico_base_name} (.ico)")
            if popup:
                popup.destroy()
            
        except Exception as e:
            messagebox.showerror("Icon Save Error", f"Failed to save .ico file: {str(e)}")

    def show_save_confirmation(self, name):
        """Display a confirmation message in the status label.
        
        Args:
            name: Name of the saved file to display
        """
        self.status_label.configure(text=f"{name}\n✅", text_color="#2ecc71")
        self.after(3000, self.clear_status)

    def clear_status(self):
        """Clear the status label text."""
        self.status_label.configure(text="")

    def _play_sound(self, filename):
        """Play a sound effect from the sounds directory.
        
        Args:
            filename: Name of the sound file to play
        """
        path = os.path.join(SOUND_DIR, filename)
        if os.path.exists(path):
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                pass

    def _prev_background(self):
        """Cycle to previous background in the list."""
        if self.bg_files and not self.curve_enabled:
            # If currently using a custom background (index >= len(bg_files)), reset to first background
            if self.current_bg_index >= len(self.bg_files):
                self.current_bg_index = len(self.bg_files) - 1
            else:
                self.current_bg_index = (self.current_bg_index - 1) % len(self.bg_files)
            self._debounced_update()

    def _search_for_image(self):
        """Open a web browser to search for transparent PNG images.
        
        Uses pngaaa.com as the image source.
        """
        search_term = self.search_entry.get().strip()
        if search_term:
            # URL encode the search term
            import urllib.parse
            encoded_term = urllib.parse.quote(search_term)
            url = f"https://www.pngaaa.com/search/{encoded_term}/"
            
            # Open the URL in the default web browser
            import webbrowser
            webbrowser.open(url)
        else:
            # If no search term, just open the main site
            import webbrowser
            webbrowser.open("https://www.pngaaa.com/")

    def _randomize_settings(self):
        """Randomize background, frame, and color settings.
        
        Randomly selects backgrounds, frames, and hue values for variety.
        """
        if self.bg_files and not self.curve_enabled:
            self.current_bg_index = random.randrange(len(self.bg_files))
        if self.frame_files and not self.curve_enabled:
            self.current_frame_index = random.randrange(len(self.frame_files))
        # Only randomize hues for active lines
        for i in range(3):
            if self.line_active[i]:
                self.line_hues[i] = random.uniform(0, 360)
        self.bg_hue = random.uniform(0, 360)
        self.border_hue = random.uniform(0, 360)
        try:
            self.bg_hue_slider.set(self.bg_hue)
            self.border_hue_slider.set(self.border_hue)
            # Set hue slider to first active line's hue
            for i in range(3):
                if self.line_active[i]:
                    self.hue_slider.set(self.line_hues[i])
                    break
        except:
            pass
        
        # Update background color preview
        bg_color = self._get_solid_color(self.bg_hue)
        bg_hex_color = f"#{bg_color[0]:02x}{bg_color[1]:02x}{bg_color[2]:02x}"
        if hasattr(self, 'bg_hue_preview'):
            self.bg_hue_preview.configure(fg_color=bg_hex_color)
        
        # Update border color preview  
        border_color = self._get_solid_color(self.border_hue)
        border_hex_color = f"#{border_color[0]:02x}{border_color[1]:02x}{border_color[2]:02x}"
        if hasattr(self, 'border_hue_preview'):
            self.border_hue_preview.configure(fg_color=border_hex_color)
        
        # Update RGB entries for background
        if hasattr(self, 'bg_r_entry'):
            self.bg_r_entry.delete(0, "end")
            self.bg_r_entry.insert(0, str(bg_color[0]))
            self.bg_g_entry.delete(0, "end")
            self.bg_g_entry.insert(0, str(bg_color[1]))
            self.bg_b_entry.delete(0, "end")
            self.bg_b_entry.insert(0, str(bg_color[2]))
        
        # Update RGB entries for border
        if hasattr(self, 'border_r_entry'):
            self.border_r_entry.delete(0, "end")
            self.border_r_entry.insert(0, str(border_color[0]))
            self.border_g_entry.delete(0, "end")
            self.border_g_entry.insert(0, str(border_color[1]))
            self.border_b_entry.delete(0, "end")
            self.border_b_entry.insert(0, str(border_color[2]))
        
        # Update RGB entries for text (first active line)
        for i in range(3):
            if self.line_active[i]:
                text_color = self._get_solid_color(self.line_hues[i])
                if hasattr(self, 'text_r_entry'):
                    self.text_r_entry.delete(0, "end")
                    self.text_r_entry.insert(0, str(text_color[0]))
                    self.text_g_entry.delete(0, "end")
                    self.text_g_entry.insert(0, str(text_color[1]))
                    self.text_b_entry.delete(0, "end")
                    self.text_b_entry.insert(0, str(text_color[2]))
                break
        
        if hasattr(self, 'color_preview'):
            # Update color preview to first active line's color
            for i in range(3):
                if self.line_active[i]:
                    color = self._get_solid_color(self.line_hues[i])
                    hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                    self.color_preview.configure(fg_color=hex_color)
                    break
        
        self.rainbow_var.set(False)
        self.outline_var.set(True)
        self._debounced_update()

    def _next_background(self):
        """Cycle to next background in the list."""
        if self.bg_files and not self.curve_enabled:
            # If currently using a custom background (index >= len(bg_files)), reset to first background
            if self.current_bg_index >= len(self.bg_files):
                self.current_bg_index = 0
            else:
                self.current_bg_index = (self.current_bg_index + 1) % len(self.bg_files)
            self._debounced_update()

    def _prev_frame(self):
        """Cycle to previous frame/border in the list."""
        if self.frame_files and not self.curve_enabled:
            self.current_frame_index = (self.current_frame_index - 1) % len(self.frame_files)
            self._debounced_update()

    def _next_frame(self):
        """Cycle to next frame/border in the list."""
        if self.frame_files and not self.curve_enabled:
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frame_files)
            self._debounced_update()

    def _prev_font(self):
        """Cycle to previous font, skipping template fonts."""
        if self.font_files:
            start = self.current_font_index
            while True:
                self.current_font_index = (self.current_font_index - 1) % len(self.font_files)
                if not self.font_files[self.current_font_index].startswith("template_"):
                    break
                if self.current_font_index == start:
                    break
            self._load_current_fonts()
            self._debounced_update()

    def _next_font(self):
        """Cycle to next font, skipping template fonts."""
        if self.font_files:
            start = self.current_font_index
            while True:
                self.current_font_index = (self.current_font_index + 1) % len(self.font_files)
                if not self.font_files[self.current_font_index].startswith("template_"):
                    break
                if self.current_font_index == start:
                    break
            self._load_current_fonts()
            self._debounced_update()

    def _on_paragraph_change(self, event=None):
        """Handle text input changes with automatic word wrapping.
        
        Wraps text at 12 characters per line and limits to 3 lines maximum.
        """
        text = self.paragraph_entry.get("1.0", "end-1c")
        
        # Handle word wrapping at 12 characters
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= 12:
                wrapped_lines.append(line)
            else:
                # Split line into words and wrap properly
                words = line.split(' ')
                current_line = ""
                
                for i, word in enumerate(words):
                    # Check if adding this word would exceed 12 chars
                    test_line = current_line.rstrip() + ('' if i == 0 else ' ') + word
                    if len(test_line) > 12:
                        if current_line.rstrip():
                            wrapped_lines.append(current_line.rstrip())
                            current_line = word + " "
                        else:
                            # Single word longer than 12 chars, split it
                            while len(word) > 12:
                                wrapped_lines.append(word[:12])
                                word = word[12:]
                            current_line = word + " "
                    else:
                        if i == 0:
                            current_line = word + " "
                        else:
                            current_line += word + " "
                
                if current_line.rstrip():
                    wrapped_lines.append(current_line.rstrip())
        
        # Limit to exactly 3 lines
        wrapped_lines = wrapped_lines[:3]
        
        # Update textbox if wrapping was needed
        new_text = '\n'.join(wrapped_lines)
        if text != new_text:
            cursor_pos = self.paragraph_entry.index(tk.INSERT)
            self.paragraph_entry.delete("1.0", "end")
            self.paragraph_entry.insert("1.0", new_text)
            # Move cursor to end of text
            try:
                self.paragraph_entry.mark_set(tk.INSERT, "end")
            except:
                pass
        
        # Update title_lines with the wrapped content
        self.title_lines = []
        for line in wrapped_lines:
            line = line.strip()
            if line:
                self.title_lines.append(line)
        
        # Ensure we have at least 1 line
        if not self.title_lines:
            self.title_lines = ["Template 1"]
        
        self._debounced_update()

    def _on_paragraph_key_press(self, event):
        """Handle key presses in the text entry with line and character limits.
        
        Prevents typing beyond 3 lines and 36 total characters.
        """
        # Get current text and cursor position
        text = self.paragraph_entry.get("1.0", "end-1c")
        lines = text.split('\n')
        cursor_pos = self.paragraph_entry.index(tk.INSERT)
        cursor_line = int(cursor_pos.split('.')[0]) - 1
        cursor_col = int(cursor_pos.split('.')[1])
        
        # Prevent typing on 4th line or beyond
        if cursor_line >= 3:
            return "break"
        
        # Check if we're at the absolute limit (36 characters total)
        total_chars = len('\n'.join(lines))
        if total_chars >= 36:
            # Allow backspace and delete even at limits
            if event.keysym not in ['BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down']:
                return "break"
        
        # Prevent creating 4th line with Enter
        if event.keysym == 'Return' and len(lines) >= 3:
            return "break"
        
        return None

    def _on_paragraph_enter(self, event=None):
        """Handle Enter key - limit to 3 lines."""
        # Handle Enter key - limit to 3 lines
        text = self.paragraph_entry.get("1.0", "end-1c")
        lines = text.split('\n')
        
        # If we already have 3 lines, prevent creating more
        if len(lines) >= 3:
            return "break"
        
        # Allow Enter to create new lines
        return None

    def _on_title_change(self, event=None):
        """Placeholder for backward compatibility with templates."""
        # Keep this for backward compatibility with templates
        pass

    def _on_enter_pressed(self, event):
        """Placeholder for backward compatibility."""
        # Keep this for backward compatibility
        return "break"

    def _load_image(self):
        """Load an image file to use as the main game image.
        
        Opens a file dialog and loads the selected image. If preserve mode
        is enabled, keeps current position settings.
        """
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tiff")]
        )
        if not path:
            return

        try:
            new_img = Image.open(path).convert("RGBA")
            
            if self.game_img_orig is not None and self.preserve_original_size:
                # === PRESERVE ORIGINAL SIZE + KEEP CURRENT POSITION ===
                self.game_img_orig = new_img
                
                # Keep the current X and Y offset (this is what you wanted)
                # Do NOT reset offset_x / offset_y
                
                # Optional: reset stretch (recommended when preserving size)
                self.stretch_x = 1.0
                self.stretch_y = 1.0
                
                # You can choose to keep current zoom or reset it.
                # Most people prefer to keep zoom when preserving size:
                # self.zoom_level = 50   # ← Uncomment this line if you want to reset zoom
                
            else:
                # First image upload or preserve mode is OFF → normal behavior
                self.game_img_orig = new_img

            self._update_preview()
            self.show_save_confirmation("Image Loaded!")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load image:\n{str(e)}")

    def _update_slider_values(self):
        """Update all slider values and entries after image upload.
        
        Syncs the UI sliders and entry fields with the current internal values.
        """
        # Update stretch sliders
        self.stretch_x_slider.set(self.stretch_x)
        self.stretch_x_entry.delete(0, "end")
        self.stretch_x_entry.insert(0, f"{self.stretch_x:.2f}")
        
        self.stretch_y_slider.set(self.stretch_y)
        self.stretch_y_entry.delete(0, "end")
        self.stretch_y_entry.insert(0, f"{self.stretch_y:.2f}")
        
        # Update offset sliders
        self.x_slider.set(self.offset_x)
        self.x_entry.delete(0, "end")
        self.x_entry.insert(0, str(self.offset_x))
        
        self.y_slider.set(self.offset_y)
        self.y_entry.delete(0, "end")
        self.y_entry.insert(0, str(self.offset_y))
        
        # Update zoom slider
        self.zoom_slider.set(self.zoom_level)
        self.zoom_entry.delete(0, "end")
        self.zoom_entry.insert(0, str(self.zoom_level))

    def _load_template_image(self):
        """Load an image from the storage directory for use as game image.
        
        Automatically calculates optimal stretch and position to fit the icon.
        """
        self._play_sound("upload.wav")
        path = filedialog.askopenfilename(initialdir=STORAGE_DIR, title="Select Template Image", filetypes=[("PNG Images", "*.png")])
        if path:
            try:
                self.game_img_orig = Image.open(path).convert("RGBA")
                
                # First, resize large images to a manageable size
                if max(self.game_img_orig.size) > 512:
                    self.game_img_orig.thumbnail((512, 512), Image.Resampling.LANCZOS)
                
                # Get image dimensions
                img_width, img_height = self.game_img_orig.size
                
                # Calculate smart stretching to fit the icon
                icon_width, icon_height = 256, 256
                target_width, target_height = 235, 235  # Leave some margin
                
                # Calculate optimal stretch factors
                stretch_x = target_width / img_width
                stretch_y = target_height / img_height
                
                # Apply smart stretching
                self.stretch_x = stretch_x
                self.stretch_y = stretch_y
                
                # Center the image
                self.offset_x = 0
                self.offset_y = 0
                
                # Set zoom to fit properly
                self.zoom_level = 50  # Default zoom
                
                # Update all sliders and entries with calculated values
                self._update_slider_values()
                
                self._debounced_update()
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

    def _open_template_popup(self):
        """Open the template save/load popup window.
        
        Shows 6 template slots with previews and save/load buttons.
        """
        self._load_asset_lists()
        self._load_current_fonts()
        popup = ctk.CTkToplevel(self)
        popup.title("SNES Icon Templates")
        popup.geometry("860x680")
        popup.grab_set()
        popup.resizable(False, False)
        ctk.CTkLabel(popup, text="Save / Load Templates (6 slots)", font=self.retro_label_font).pack(pady=15)
        grid = ctk.CTkFrame(popup, fg_color="#1a1a1a")
        grid.pack(pady=10, padx=20)
        for i in range(6):
            slot = ctk.CTkFrame(grid, fg_color="#222222", corner_radius=8)
            slot.grid(row=i//3, column=i%3, padx=15, pady=15, sticky="n")
            preview_img = self._render_template_preview(i)
            self.template_previews[i] = preview_img
            lbl = ctk.CTkLabel(slot, image=preview_img, text="")
            lbl.pack(pady=8)
            btn_row = ctk.CTkFrame(slot, fg_color="#222222")
            btn_row.pack(pady=5)
            ctk.CTkButton(btn_row, text="Save", width=80, fg_color="#e67e22", hover_color="#d35400", command=lambda x=i: self._save_to_template(x, popup)).pack(side="left", padx=6)
            ctk.CTkButton(btn_row, text="Load", width=80, fg_color="#3498db", hover_color="#2980b9", command=lambda x=i: self._load_from_template(x, popup)).pack(side="left", padx=6)

    def _save_to_template(self, idx, popup=None):
        """Save current icon settings and assets to a template slot.
        
        Saves all settings to JSON and copies assets (game image, background,
        frame, font) to the template folder.
        
        Args:
            idx: Template slot index (0-5)
            popup: Popup window to close after saving
        """
        import json
        import shutil
        
        # Create template folder
        template_folder = os.path.join(STORAGE_DIR, f"template_{idx}")
        os.makedirs(template_folder, exist_ok=True)
        
        # Save game image if exists
        game_path = os.path.join(template_folder, "template_game.png")
        if self.game_img_orig:
            try:
                self.game_img_orig.save(game_path)
            except:
                pass
        elif os.path.exists(game_path):
            try:
                os.remove(game_path)
            except:
                pass
        
        # Save background (both regular and custom backgrounds)
        bg_target_path = os.path.join(template_folder, "template_bg.png")
        
        if self.current_bg_index >= len(self.bg_files) and hasattr(self, 'custom_bg_files'):
            # Custom background
            custom_bg_index = self.current_bg_index - len(self.bg_files)
            if 0 <= custom_bg_index < len(self.custom_bg_files):
                bg_filename = self.custom_bg_files[custom_bg_index]
                bg_source_path = os.path.join(GENERATED_BG_DIR, bg_filename)
                if os.path.exists(bg_source_path):
                    try:
                        shutil.copy2(bg_source_path, bg_target_path)
                    except:
                        pass
        elif self.current_bg_index < len(self.bg_files):
            # Regular background
            bg_filename = self.bg_files[self.current_bg_index]
            bg_source_path = os.path.join(BG_DIR, bg_filename)
            if os.path.exists(bg_source_path):
                try:
                    shutil.copy2(bg_source_path, bg_target_path)
                except:
                    pass
        
        # Save frame if it exists
        if self.current_frame_index < len(self.frame_files):
            frame_filename = self.frame_files[self.current_frame_index]
            frame_source_path = os.path.join(BORDER_DIR, frame_filename)
            frame_target_path = os.path.join(template_folder, "template_frame.png")
            if os.path.exists(frame_source_path):
                try:
                    shutil.copy2(frame_source_path, frame_target_path)
                except:
                    pass
        
        # Save font if it exists
        if self.current_font_index < len(self.font_files):
            font_filename = self.font_files[self.current_font_index]
            font_source_path = os.path.join(FONT_DIR, font_filename)
            font_target_path = os.path.join(template_folder, "template_font.ttf")
            if os.path.exists(font_source_path):
                try:
                    shutil.copy2(font_source_path, font_target_path)
                except:
                    pass
        
        # Create a copy of line_hues and mark lines with direct RGB overrides
        line_hues_copy = self.line_hues[:]
        if hasattr(self, '_direct_rgb'):
            for line_idx in self._direct_rgb:
                line_idx_int = int(line_idx)  # Convert to int
                if 0 <= line_idx_int < len(line_hues_copy):
                    line_hues_copy[line_idx_int] = -1  # Mark as direct RGB override

        # Save all settings to JSON file
        settings = {
            "title_lines": self.title_lines[:],
            "line_hues": line_hues_copy,
            "line_rainbows": self.line_rainbows[:],
            "line_outlines": self.line_outlines[:],
            "line_font_size_offsets": self.line_font_size_offsets[:],
            "line_font_spacing_offsets": self.line_font_spacing_offsets[:],
            "line_text_offset_xs": self.line_text_offset_xs[:],
            "line_text_offset_ys": self.line_text_offset_ys[:],
            "line_active": self.line_active[:],
            "bg_hue": self.bg_hue,
            "bg_brightness": self.bg_brightness,
            "border_hue": self.border_hue,
            "zoom_level": self.zoom_level,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "stretch_x": self.stretch_x,
            "stretch_y": self.stretch_y,
            "brightness": self.brightness,
            "crt_enabled": self.crt_enabled,
            "bg_scale": self.bg_scale,
            "bg_offset_x": self.bg_offset_x,
            "bg_offset_y": self.bg_offset_y,
            "frame_offset_x": self.frame_offset_x,
            "frame_offset_y": self.frame_offset_y,
            "scanline_alpha": self.scanline_alpha,
            "current_bg_index": self.current_bg_index,
            "current_frame_index": self.current_frame_index,
            "current_font_index": self.current_font_index,
            "line_spacing_offset": self.line_spacing_offset,
            "font_position_step": self.font_position_step,
            "decor_enabled": self.decor_enabled,
            "current_decor_index": self.current_decor_index,
            "decor_scale": self.decor_scale,
            "decor_offset_x": self.decor_offset_x,
            "decor_offset_y": self.decor_offset_y,
            "glow_enabled": self.glow_var.get(),
            "glow_strength": self.glow_strength,
            "glow_color_hue": self.glow_color_hue,
            "glow_size": self.glow_size,
            "shadow_opacity": self.shadow_opacity,
            "direct_rgb": getattr(self, '_direct_rgb', {}),
            "glow_rgb": getattr(self, '_glow_rgb', None),
            "glow_direct_rgb": hasattr(self, '_glow_direct_rgb'),
            # Store original filenames for reference
            "original_bg_filename": self.bg_files[self.current_bg_index] if self.current_bg_index < len(self.bg_files) else None,
            "original_frame_filename": self.frame_files[self.current_frame_index] if self.current_frame_index < len(self.frame_files) else None,
            "original_font_filename": self.font_files[self.current_font_index] if self.current_font_index < len(self.font_files) else None,
            "custom_bg_filename": self.custom_bg_files[self.current_bg_index - len(self.bg_files)] if (self.current_bg_index >= len(self.bg_files) and hasattr(self, 'custom_bg_files') and 0 <= self.current_bg_index - len(self.bg_files) < len(self.custom_bg_files)) else None
        }
        
        # Save settings to JSON file
        settings_path = os.path.join(template_folder, "template_settings.txt")
        try:
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
        except:
            pass
        
        if popup: popup.destroy()
        self._update_preview()
        self.show_save_confirmation(f"Template {idx+1} Saved!")

    def _load_from_template(self, idx, popup=None):
        """Load template settings and assets from a template slot.
        
        Loads settings from JSON and restores assets (game image, background,
        frame, font). Handles both regular and custom backgrounds.
        
        Args:
            idx: Template slot index (0-5)
            popup: Popup window to close after loading
        """
        import json
        
        template_folder = os.path.join(STORAGE_DIR, f"template_{idx}")
        
        # Check if template folder exists
        if not os.path.exists(template_folder):
            messagebox.showerror("Error", f"Template {idx+1} not found")
            return
        
        # Load settings from JSON file
        settings_path = os.path.join(template_folder, "template_settings.txt")
        if not os.path.exists(settings_path):
            messagebox.showerror("Error", f"Template {idx+1} settings not found")
            return
        
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load template settings: {e}")
            return
        
        # Load game image if exists
        game_path = os.path.join(template_folder, "template_game.png")
        if os.path.exists(game_path):
            try:
                self.game_img_orig = Image.open(game_path).convert("RGBA")
            except:
                self.game_img_orig = None
        else:
            self.game_img_orig = None
        
        # Load background if exists
        bg_path = os.path.join(template_folder, "template_bg.png")
        if os.path.exists(bg_path):
            try:
                # Check if this was originally a regular background
                original_bg_filename = settings.get("original_bg_filename")
                original_bg_index = settings.get("current_bg_index", 0)
                
                if original_bg_filename and original_bg_index < len(self.bg_files):
                    # This was a regular background - find it in the bg_files list
                    if original_bg_filename in self.bg_files:
                        self.current_bg_index = self.bg_files.index(original_bg_filename)
                    else:
                        # Original background not found, treat as custom
                        bg_img = Image.open(bg_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                        
                        if not hasattr(self, 'custom_bg_files'):
                            self.custom_bg_files = []
                        
                        template_bg_filename = f"template_{idx}_bg.png"
                        template_bg_path = os.path.join(GENERATED_BG_DIR, template_bg_filename)
                        
                        if not os.path.exists(template_bg_path):
                            import shutil
                            shutil.copy2(bg_path, template_bg_path)
                        
                        if template_bg_filename not in self.custom_bg_files:
                            self.custom_bg_files.append(template_bg_filename)
                        
                        custom_index = len(self.bg_files) + self.custom_bg_files.index(template_bg_filename)
                        self.bg_cache[custom_index] = bg_img
                        self.current_bg_index = custom_index
                else:
                    # This was a custom background
                    bg_img = Image.open(bg_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                    
                    if not hasattr(self, 'custom_bg_files'):
                        self.custom_bg_files = []
                    
                    template_bg_filename = f"template_{idx}_bg.png"
                    template_bg_path = os.path.join(GENERATED_BG_DIR, template_bg_filename)
                    
                    if not os.path.exists(template_bg_path):
                        import shutil
                        shutil.copy2(bg_path, template_bg_path)
                    
                    if template_bg_filename not in self.custom_bg_files:
                        self.custom_bg_files.append(template_bg_filename)
                    
                    custom_index = len(self.bg_files) + self.custom_bg_files.index(template_bg_filename)
                    self.bg_cache[custom_index] = bg_img
                    self.current_bg_index = custom_index
                
            except:
                pass
        
        # Load frame if exists
        frame_path = os.path.join(template_folder, "template_frame.png")
        if os.path.exists(frame_path):
            try:
                frame_img = Image.open(frame_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
                
                # Create a unique filename for this template's frame
                template_frame_filename = f"template_{idx}_frame.png"
                template_frame_path = os.path.join(BORDER_DIR, template_frame_filename)
                
                # Copy to frames folder if not already there
                if not os.path.exists(template_frame_path):
                    import shutil
                    shutil.copy2(frame_path, template_frame_path)
                
                # Add to frame_files if not already there
                if template_frame_filename not in self.frame_files:
                    self.frame_files.append(template_frame_filename)
                
                # Set current frame index
                self.current_frame_index = self.frame_files.index(template_frame_filename)
                self.frame_cache[self.current_frame_index] = frame_img
                
            except:
                pass
        
        # Load font if exists
        font_path = os.path.join(template_folder, "template_font.ttf")
        if os.path.exists(font_path):
            try:
                # Load font directly from template folder - don't copy to main Fonts folder
                template_font_filename = f"template_{idx}_font.ttf"
                
                # Add to font_files if not already there (using template folder path)
                if template_font_filename not in self.font_files:
                    self.font_files.append(template_font_filename)
                
                # Set current font index
                self.current_font_index = self.font_files.index(template_font_filename)
                
            except:
                pass
        
        # Load all settings
        self.title_lines = settings.get("title_lines", ["Template 1"])[:]
        self.line_hues = settings.get("line_hues", [0.0, 0.0, 0.0])[:]
        self.line_rainbows = settings.get("line_rainbows", [False, False, False])[:]
        self.line_outlines = settings.get("line_outlines", [True, True, True])[:]
        self.line_font_size_offsets = settings.get("line_font_size_offsets", [6, 6, 6])[:]
        self.line_font_spacing_offsets = settings.get("line_font_spacing_offsets", [-1, -1, -1])[:]
        self.line_text_offset_xs = settings.get("line_text_offset_xs", [0, 0, 0])[:]
        self.line_text_offset_ys = settings.get("line_text_offset_ys", [4, 4, 4])[:]
        self.line_active = settings.get("line_active", [True, True, True])[:]

        self.bg_hue = settings.get("bg_hue", 0.0)
        self.bg_brightness = settings.get("bg_brightness", 1.0)
        self.border_hue = settings.get("border_hue", 0.0)
        self.zoom_level = settings.get("zoom_level", 50)
        self.offset_x = settings.get("offset_x", 0)
        self.offset_y = settings.get("offset_y", 0)
        self.stretch_x = settings.get("stretch_x", 1.0)
        self.stretch_y = settings.get("stretch_y", 1.0)
        self.brightness = settings.get("brightness", 0.9)
        self.crt_enabled = settings.get("crt_enabled", True)
        self.curve_enabled = False
        self.bg_scale = settings.get("bg_scale", 1.0)
        self.bg_offset_x = settings.get("bg_offset_x", 0)
        self.bg_offset_y = settings.get("bg_offset_y", 0)
        self.frame_offset_x = settings.get("frame_offset_x", 0)
        self.frame_offset_y = settings.get("frame_offset_y", 0)
        self.scanline_alpha = settings.get("scanline_alpha", 45)
        self.current_frame_index = settings.get("current_frame_index", 0)
        self.current_font_index = settings.get("current_font_index", 0)
        self.line_spacing_offset = settings.get("line_spacing_offset", -10)
        self.font_position_step = settings.get("font_position_step", 1)
        self.decor_enabled = settings.get("decor_enabled", True)
        self.current_decor_index = settings.get("current_decor_index", 0)
        self.decor_scale = settings.get("decor_scale", 1.0)
        self.decor_offset_x = settings.get("decor_offset_x", 0)
        self.decor_offset_y = settings.get("decor_offset_y", 0)
        self.glow_enabled = settings.get("glow_enabled", False)
        self.glow_var.set(self.glow_enabled)
        self.glow_strength = settings.get("glow_strength", 1.0)
        self.glow_color_hue = settings.get("glow_color_hue", 0.0)
        self.glow_size = settings.get("glow_size", 2)
        self.shadow_opacity = settings.get("shadow_opacity", 100)
        
        # Load direct RGB values if present
        direct_rgb = settings.get("direct_rgb", {})
        if direct_rgb:
            # Convert string keys to integers (JSON converts keys to strings)
            self._direct_rgb = {int(k): v for k, v in direct_rgb.items()}
        else:
            self._direct_rgb = {}

        # Load glow RGB values if present
        glow_rgb = settings.get("glow_rgb")
        glow_direct_rgb = settings.get("glow_direct_rgb", False)
        if glow_rgb is not None and glow_direct_rgb:
            self._glow_rgb = tuple(glow_rgb)
            self._glow_direct_rgb = True
            self.glow_color_hue = -1  # Mark as direct RGB
        else:
            # Clear any existing glow RGB overrides
            if hasattr(self, '_glow_direct_rgb'):
                delattr(self, '_glow_direct_rgb')
            if hasattr(self, '_glow_rgb'):
                delattr(self, '_glow_rgb')

        # Update UI elements
        for i in range(3):
            self.line_toggle_buttons[i].configure(fg_color="#00ff00" if self.line_active[i] else "#555555")
        self.rainbow_var.set(any(self.line_rainbows))
        self.outline_var.set(any(self.line_outlines))
        self.crt_var.set(self.crt_enabled)
        self.decor_var.set(self.decor_enabled)
        self._on_crt()
        self._on_decor_toggle()

        # Update sliders
        self.zoom_slider.set(self.zoom_level)
        self.stretch_x_slider.set(self.stretch_x)
        self.stretch_y_slider.set(self.stretch_y)
        self.brightness_slider.set(self.brightness)
        self.bg_brightness_slider.set(self.bg_brightness)
        self.opacity_slider.set(self.scanline_alpha)
        
        # Update hue slider and color preview for first active line
        active_idx = next((i for i, a in enumerate(self.line_active) if a), 0)
        if self.line_hues[active_idx] == -1 and hasattr(self, '_direct_rgb') and active_idx in self._direct_rgb:
            # Use direct RGB values
            r, g, b = self._direct_rgb[active_idx]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            # Convert RGB to hue for slider display
            import colorsys
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            hue = h * 360
            self.hue_slider.set(hue)
            # Update RGB entries
            self.text_r_entry.delete(0, "end")
            self.text_r_entry.insert(0, str(r))
            self.text_g_entry.delete(0, "end")
            self.text_g_entry.insert(0, str(g))
            self.text_b_entry.delete(0, "end")
            self.text_b_entry.insert(0, str(b))
        else:
            # Use hue-based color
            hue = self.line_hues[active_idx] if self.line_hues[active_idx] != -1 else 0
            self.hue_slider.set(hue)
            # Update RGB entries to reflect hue-based color
            color = self._get_solid_color(hue)
            self.text_r_entry.delete(0, "end")
            self.text_r_entry.insert(0, str(color[0]))
            self.text_g_entry.delete(0, "end")
            self.text_g_entry.insert(0, str(color[1]))
            self.text_b_entry.delete(0, "end")
            self.text_b_entry.insert(0, str(color[2]))

        if hasattr(self, 'color_preview'):
            color = self._get_text_color(active_idx)
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            self.color_preview.configure(fg_color=hex_color)

        if hasattr(self, 'border_hue_slider'):
            self.border_hue_slider.set(self.border_hue)
            border_color = self._get_solid_color(self.border_hue)
            border_hex = f"#{border_color[0]:02x}{border_color[1]:02x}{border_color[2]:02x}"
            self.border_hue_preview.configure(fg_color=border_hex)
            self.border_r_entry.delete(0, "end")
            self.border_r_entry.insert(0, str(border_color[0]))
            self.border_g_entry.delete(0, "end")
            self.border_g_entry.insert(0, str(border_color[1]))
            self.border_b_entry.delete(0, "end")
            self.border_b_entry.insert(0, str(border_color[2]))

        if hasattr(self, 'decor_scale_slider'): self.decor_scale_slider.set(self.decor_scale)
        if hasattr(self, 'decor_offset_x_slider'): self.decor_offset_x_slider.set(self.decor_offset_x)
        if hasattr(self, 'decor_offset_y_slider'): self.decor_offset_y_slider.set(self.decor_offset_y)
        
        if hasattr(self, 'shadow_opacity_slider'): 
            self.shadow_opacity_slider.set(self.shadow_opacity)
        if hasattr(self, 'shadow_opacity_entry'):
            self.shadow_opacity_entry.delete(0, "end")
            self.shadow_opacity_entry.insert(0, str(self.shadow_opacity))

        # Update glow color slider and RGB entries
        if hasattr(self, 'glow_color_slider'):
            # Check if we have direct RGB values for glow
            if hasattr(self, '_glow_direct_rgb') and hasattr(self, '_glow_rgb'):
                # Use direct RGB values
                r, g, b = self._glow_rgb
                glow_hex = f"#{r:02x}{g:02x}{b:02x}"
                self.glow_color_preview.configure(fg_color=glow_hex)
                # Convert RGB to hue for slider display
                import colorsys
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                hue = h * 360
                self.glow_color_slider.set(hue)
                # Update RGB entries
                self.glow_r_entry.delete(0, "end")
                self.glow_r_entry.insert(0, str(r))
                self.glow_g_entry.delete(0, "end")
                self.glow_g_entry.insert(0, str(g))
                self.glow_b_entry.delete(0, "end")
                self.glow_b_entry.insert(0, str(b))
            else:
                # Use hue-based color
                self.glow_color_slider.set(self.glow_color_hue)
                glow_color = self._get_solid_color(self.glow_color_hue)
                glow_hex = f"#{glow_color[0]:02x}{glow_color[1]:02x}{glow_color[2]:02x}"
                self.glow_color_preview.configure(fg_color=glow_hex)
                if hasattr(self, 'glow_r_entry'):
                    self.glow_r_entry.delete(0, "end")
                    self.glow_r_entry.insert(0, str(glow_color[0]))
                    self.glow_g_entry.delete(0, "end")
                    self.glow_g_entry.insert(0, str(glow_color[1]))
                    self.glow_b_entry.delete(0, "end")
                    self.glow_b_entry.insert(0, str(glow_color[2]))

        self.step_button.configure(text=f"{self.font_position_step}px")
        self._show_background_selector()
        self._load_current_fonts()
        
        if popup: popup.destroy()
        self._update_preview()
        self.show_save_confirmation(f"Template {idx+1} Loaded!")

    def _start_repeat(self, func):
        """Start repeating a function when a button is held down.
        
        Args:
            func: The function to repeat
        """
        func()
        self._repeat_id = self.after(250, lambda f=func: self._do_repeat(f))

    def _do_repeat(self, func):
        """Continue repeating a function at a faster rate.
        
        Args:
            func: The function to repeat
        """
        func()
        self._repeat_id = self.after(60, lambda f=func: self._do_repeat(f))

    def _stop_repeat(self):
        """Stop the repeating function."""
        if self._repeat_id is not None:
            self.after_cancel(self._repeat_id)
            self._repeat_id = None

    def _create_repeatable_arrow(self, parent, image, command, row, column, width=50, height=32, padx=8, pady=4):
        """Create a button with repeat functionality for arrow navigation.
        
        When held down, the button will repeatedly trigger the command.
        
        Args:
            parent: Parent widget
            image: Button image
            command: Function to execute on click/hold
            row: Grid row position
            column: Grid column position
            width: Button width
            height: Button height
            padx: Horizontal padding
            pady: Vertical padding
            
        Returns:
            The created button widget
        """
        btn = ctk.CTkButton(parent, image=image, text="", width=width, height=height)
        btn.grid(row=row, column=column, padx=padx, pady=pady)
        btn.bind("<ButtonPress-1>", lambda e, f=command: self._start_repeat(f))
        btn.bind("<ButtonRelease-1>", lambda e: self._stop_repeat())
        return btn

    def _load_templates(self):
        """Load template metadata from JSON file.
        
        Loads the template list from storage or creates defaults if not found.
        """
        template_path = os.path.join(TEMPLATE_DIR, "templatesaves.txt")
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # Accept any number of templates, don't require exactly 6
                if len(loaded) >= 1:
                    self.templates = loaded
                else:
                    self.templates = self._create_default_templates()
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not load templates:\n{str(e)}\nUsing defaults.")
                self.templates = self._create_default_templates()
        else:
            self.templates = self._create_default_templates()
        self._save_templates()

    def _save_templates(self):
        """Save template metadata to JSON file."""
        template_path = os.path.join(TEMPLATE_DIR, "templatesaves.txt")
        try:
            with open(template_path, "w", encoding="utf-8") as f:
                json.dump(self.templates, f, indent=2)
            self.show_save_confirmation("Templates Saved!")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save templates:\n{str(e)}")

    def _generate_earthbound_background(self):
        """Generate a background using Earthbound-style mathematical patterns.
        
        Creates psychedelic, retro-style backgrounds with vibrant colors
        and geometric patterns inspired by the Earthbound/Mother RPG series.
        
        Returns:
            PIL Image with the generated background pattern
        """
        # Earthbound-style pattern names
        pattern_names = [
            "Distorted Checkerboard",
            "Wavy Vertical Stripes", 
            "Shimmering Honeycomb",
            "Liquid Marble Swirls",
            "Psychedelic Polka Dots",
            "Wobbling Hexagon Grid",
            "Fluid Diamond Pattern",
            "Pulsating Square Matrix",
            "Undulating Triangle Field",
            "Shifting Circle Maze",
            "Flowing Wave Interference",
            "Glitching Pixel Grid",
            "Rotating Star Burst",
            "Melting Square Tiles",
            "Breathing Diamond Mesh",
            "Oscillating Line Pattern",
            "Swirling Color Vortex",
            "Popping Bubble Matrix",
            "Dancing Geometric Shapes",
            "Flowing Organic Forms",
            "Shimmering Diagonal Waves",
            "Pulsating Circle Grid",
            "Warping Square Pattern",
            "Liquid Triangle Flow",
            "Glitching Hexagon Field",
            "Shifting Diamond Array",
            "Flowing Color Rivers",
            "Popping Geometric Bubbles",
            "Wobbling Line Matrix",
            "Swirling Pattern Storm",
            "Pulsating Geometric Field",
            "Shimmering Color Waves",
            "Distorted Shape Grid",
            "Flowing Pattern Stream",
            "Warping Geometric Mesh",
            "Liquid Color Flow",
            "Popping Shape Matrix",
            "Shifting Pattern Waves",
            "Wobbling Color Field",
            "Swirling Geometric Flow",
            "Pulsating Pattern Grid",
            "Shimmering Shape Array",
            "Flowing Geometric Storm",
            "Warping Color Matrix",
            "Liquid Pattern Flow",
            "Popping Geometric Grid",
            "Shifting Color Waves",
            "Wobbling Pattern Field",
            "Swirling Color Matrix",
            # Magicant-inspired patterns (25 new)
            "Floating Magicant Islands",
            "Psychedelic Sea of Stars",
            "Dreamlike Flying Man",
            "Warping Reality Ripples",
            "Magicant's Twisted Trees",
            "Cosmic Mushroom Fields",
            "Surreal Cloud Spirals",
            "Mystical Statues Garden",
            "Flying Man's Sanctuary",
            "Magicant's Color Rain",
            "Distorted Flying Carpets",
            "Psychedelic Bird Patterns",
            "Magicant's Melting Ground",
            "Surreal Star Constellations",
            "Dreamscape Water Ripples",
            "Magicant's Floating Rocks",
            "Cosmic Energy Fields",
            "Psychedelic Flower Spirals",
            "Magicant's Twisted Reality",
            "Surreal Moon Patterns",
            "Flying Man's Dream Path",
            "Magicant's Color Waves",
            "Cosmic Dust Particles",
            "Psychedelic Sky Bubbles",
            "Magicant's Mystical Maze",
            "Dreamlike Energy Flows"
        ]
        
        # 75 Earthbound-style patterns (including 25 Magicant-inspired) - ensure within bounds
        pattern_type = random.randint(0, len(pattern_names) - 1)
        
        self.current_pattern_name = pattern_names[pattern_type]
        
        # Earthbound-style vibrant color palettes
        color_palettes = [
            # Neon triadic schemes
            [(255, 0, 128), (128, 0, 255), (0, 255, 128), (255, 255, 0)],  # Hot pink, purple, lime, yellow
            [(255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 255, 0)],  # Magenta, cyan, orange, lime
            [(255, 50, 150), (150, 50, 255), (50, 255, 150), (255, 200, 50)],  # Neon variations
            [(0, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 0)],  # Green, magenta, cyan, yellow
            
            # Electric schemes
            [(200, 0, 255), (255, 0, 200), (0, 200, 255), (255, 200, 0)],  # Electric purple/pink/blue/yellow
            [(255, 100, 0), (0, 255, 100), (100, 0, 255), (255, 0, 100)],  # Electric orange/green/pink
            
            # Psychedelic schemes
            [(255, 20, 147), (138, 43, 226), (0, 191, 255), (50, 205, 50)],  # Deep pink, violet, sky blue, lime
            [(255, 69, 0), (255, 215, 0), (64, 224, 208), (255, 105, 180)],  # Red orange, gold, turquoise, hot pink
            
            # Acid schemes
            [(255, 0, 100), (100, 255, 0), (0, 100, 255), (255, 255, 100)],  # Acid red, green, blue, yellow
            [(255, 128, 0), (128, 255, 0), (0, 128, 255), (255, 0, 128)],  # Acid orange, green, blue, pink
        ]
        
        colors = random.choice(color_palettes)
        
        # Random vibrant background color
        bg_colors = [
            (255, 0, 128), (128, 0, 255), (0, 255, 128), (255, 255, 0),
            (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 255, 0),
            (200, 0, 255), (255, 0, 200), (0, 200, 255), (255, 200, 0),
            (255, 20, 147), (138, 43, 226), (0, 191, 255), (50, 205, 50),
        ]
        bg_color = random.choice(bg_colors)
        
        img = Image.new("RGB", (256, 256), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Apply horizontal sine-wave distortion function
        def apply_horizontal_warp(x, y, amplitude=10, frequency=0.05):
            warped_x = x + int(amplitude * math.sin(y * frequency))
            return max(0, min(255, warped_x)), y
        
        if pattern_type == 0:
            # Distorted Checkerboard
            cell_size = 16
            for y in range(0, 256, cell_size):
                for x in range(0, 256, cell_size):
                    color = colors[((x//cell_size + y//cell_size) % len(colors))]
                    # Apply sine-wave distortion to each cell
                    warped_x, warped_y = apply_horizontal_warp(x, y, amplitude=8, frequency=0.1)
                    draw.rectangle([warped_x, warped_y, warped_x+cell_size-1, warped_y+cell_size-1], fill=color)
        
        elif pattern_type == 1:
            # Wavy Vertical Stripes
            stripe_width = 20
            for x in range(0, 256, stripe_width):
                color = colors[(x // stripe_width) % len(colors)]
                for y in range(256):
                    # Apply varying warp to create wavy effect
                    warped_x = x + int(10 * math.sin(y * 0.05 + x * 0.02))
                    if 0 <= warped_x < 256:
                        draw.line([(warped_x, y), (warped_x + stripe_width-1, y)], fill=color, width=1)
        
        elif pattern_type == 2:
            # Shimmering Honeycomb
            hex_size = 20
            for row in range(-2, 15):
                for col in range(-2, 15):
                    x = col * hex_size * 1.5 + (row % 2) * hex_size * 0.75
                    y = row * hex_size * 0.866
                    if -hex_size < x < 276 and -hex_size < y < 276:
                        color = colors[((row + col) % len(colors))]
                        # Apply shimmer effect
                        shimmer_offset = int(5 * math.sin(x * 0.1 + y * 0.1))
                        points = []
                        for i in range(6):
                            angle = i * math.pi / 3
                            px = x + shimmer_offset + int(hex_size * 0.5 * math.cos(angle))
                            py = y + int(hex_size * 0.5 * math.sin(angle))
                            points.append((px, py))
                        if len(points) > 2:
                            draw.polygon(points, fill=color)
        
        elif pattern_type == 3:
            # Liquid Marble Swirls
            for _ in range(15):
                cx = random.randint(30, 226)
                cy = random.randint(30, 226)
                for radius in range(5, 60, 5):
                    color = colors[(radius // 15) % len(colors)]
                    # Create liquid marble effect with distortion
                    points = []
                    for angle in range(0, 360, 30):
                        wobble = int(8 * math.sin(angle * 0.1 + radius * 0.05))
                        x = cx + int((radius + wobble) * math.cos(math.radians(angle)))
                        y = cy + int((radius + wobble) * math.sin(math.radians(angle)))
                        points.append((x, y))
                    if len(points) > 2:
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 4:
            # Psychedelic Polka Dots
            dot_size = 12
            spacing = 20
            for y in range(0, 256, spacing):
                for x in range(0, 256, spacing):
                    color = colors[((x//spacing + y//spacing) % len(colors))]
                    # Apply pulsating effect
                    pulse = int(3 * math.sin(x * 0.1 + y * 0.1))
                    warped_x, warped_y = apply_horizontal_warp(x, y, amplitude=5, frequency=0.08)
                    draw.ellipse([warped_x-pulse, warped_y-pulse, warped_x+dot_size+pulse, warped_y+dot_size+pulse], fill=color)
        
        elif pattern_type == 5:
            # Wobbling Hexagon Grid
            hex_size = 16
            for row in range(-2, 18):
                for col in range(-2, 18):
                    x = col * hex_size * 1.5 + (row % 2) * hex_size * 0.75
                    y = row * hex_size * 0.866
                    if -hex_size < x < 276 and -hex_size < y < 276:
                        color = colors[((row + col) % len(colors))]
                        # Apply wobble effect
                        wobble_x = int(4 * math.sin(y * 0.1))
                        wobble_y = int(4 * math.cos(x * 0.1))
                        points = []
                        for i in range(6):
                            angle = i * math.pi / 3
                            px = x + wobble_x + int(hex_size * 0.5 * math.cos(angle))
                            py = y + wobble_y + int(hex_size * 0.5 * math.sin(angle))
                            points.append((px, py))
                        if len(points) > 2:
                            draw.polygon(points, fill=color)
        
        elif pattern_type == 6:
            # Fluid Diamond Pattern
            diamond_size = 24
            for y in range(0, 256, diamond_size//2):
                for x in range(0, 256, diamond_size//2):
                    color = colors[((x//(diamond_size//2) + y//(diamond_size//2)) % len(colors))]
                    # Create fluid diamond with distortion
                    flow_offset = int(6 * math.sin(x * 0.05 + y * 0.05))
                    points = [
                        (x + diamond_size//2 + flow_offset, y),
                        (x + diamond_size + flow_offset, y + diamond_size//2),
                        (x + diamond_size//2 + flow_offset, y + diamond_size),
                        (x + flow_offset, y + diamond_size//2)
                    ]
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 7:
            # Pulsating Square Matrix
            square_size = 20
            for y in range(0, 256, square_size):
                for x in range(0, 256, square_size):
                    color = colors[((x//square_size + y//square_size) % len(colors))]
                    # Apply pulsating effect
                    pulse = int(4 * math.sin(x * 0.1 + y * 0.1))
                    draw.rectangle([x-pulse, y-pulse, x+square_size+pulse, y+square_size+pulse], fill=color)
        
        elif pattern_type == 8:
            # Undulating Triangle Field
            tri_size = 30
            for row in range(0, 10):
                for col in range(0, 10):
                    x = col * tri_size + (row % 2) * tri_size//2
                    y = row * tri_size * 0.866
                    if x < 256 and y < 256:
                        color = colors[((row + col) % len(colors))]
                        # Create undulating effect
                        undulation = int(5 * math.sin(x * 0.08 + y * 0.08))
                        points = [
                            (x + tri_size//2, y + undulation),
                            (x + tri_size + undulation, y + tri_size),
                            (x + undulation, y + tri_size)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 9:
            # Shifting Circle Maze
            circle_size = 16
            for y in range(0, 256, circle_size):
                for x in range(0, 256, circle_size):
                    color = colors[((x//circle_size + y//circle_size) % len(colors))]
                    # Apply shifting effect
                    shift_x = int(6 * math.cos(y * 0.1))
                    shift_y = int(6 * math.sin(x * 0.1))
                    draw.ellipse([x+shift_x-circle_size//2, y+shift_y-circle_size//2, 
                                x+shift_x+circle_size//2, y+shift_y+circle_size//2], fill=color)
        
        elif pattern_type == 10:
            # Flowing Wave Interference
            for y in range(0, 256, 4):
                for x in range(0, 256, 4):
                    # Create complex wave interference
                    wave1 = math.sin(x * 0.08) * 20
                    wave2 = math.sin(y * 0.06) * 15
                    wave3 = math.sin((x + y) * 0.04) * 10
                    total_wave = wave1 + wave2 + wave3
                    color_idx = int((x + y + total_wave) / 30) % len(colors)
                    # Apply flowing effect
                    flow_x = x + int(total_wave * 0.3)
                    if 0 <= flow_x < 256:
                        draw.rectangle([flow_x, y, flow_x+4, y+4], fill=colors[color_idx])
        
        elif pattern_type == 11:
            # Glitching Pixel Grid
            pixel_size = 8
            for y in range(0, 256, pixel_size):
                for x in range(0, 256, pixel_size):
                    color = colors[((x//pixel_size + y//pixel_size) % len(colors))]
                    # Apply glitch effect
                    if random.random() > 0.8:
                        glitch_offset = random.randint(-pixel_size, pixel_size)
                        draw.rectangle([x+glitch_offset, y, x+pixel_size+glitch_offset, y+pixel_size], fill=color)
                    else:
                        draw.rectangle([x, y, x+pixel_size, y+pixel_size], fill=color)
        
        elif pattern_type == 12:
            # Rotating Star Burst
            cx, cy = 128, 128
            for burst in range(3):
                angle_offset = burst * math.pi / 3
                for angle in range(0, 360, 15):
                    color = colors[(angle // 60) % len(colors)]
                    for r in range(10, 120, 15):
                        # Apply rotation effect
                        rotated_angle = angle + angle_offset + int(10 * math.sin(r * 0.05))
                        x1 = cx + int(r * math.cos(math.radians(rotated_angle)))
                        y1 = cy + int(r * math.sin(math.radians(rotated_angle)))
                        x2 = cx + int((r + 10) * math.cos(math.radians(rotated_angle)))
                        y2 = cy + int((r + 10) * math.sin(math.radians(rotated_angle)))
                        if 0 <= x1 < 256 and 0 <= y1 < 256 and 0 <= x2 < 256 and 0 <= y2 < 256:
                            draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
        
        elif pattern_type == 13:
            # Melting Square Tiles
            tile_size = 20
            for y in range(0, 256, tile_size):
                for x in range(0, 256, tile_size):
                    color = colors[((x//tile_size + y//tile_size) % len(colors))]
                    # Create melting effect
                    melt_offset = int(8 * math.sin(x * 0.05 + y * 0.05))
                    points = [
                        (x, y + melt_offset),
                        (x + tile_size, y + melt_offset),
                        (x + tile_size - melt_offset//2, y + tile_size),
                        (x + melt_offset//2, y + tile_size)
                    ]
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 14:
            # Breathing Diamond Mesh
            diamond_size = 18
            for y in range(0, 256, diamond_size//2):
                for x in range(0, 256, diamond_size//2):
                    color = colors[((x//(diamond_size//2) + y//(diamond_size//2)) % len(colors))]
                    # Create breathing effect
                    breathe = int(3 * math.sin(x * 0.03 + y * 0.03))
                    points = [
                        (x + diamond_size//2, y + breathe),
                        (x + diamond_size + breathe, y + diamond_size//2),
                        (x + diamond_size//2, y + diamond_size - breathe),
                        (x + breathe, y + diamond_size//2)
                    ]
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 15:
            # Oscillating Line Pattern
            line_spacing = 8
            for y in range(0, 256, line_spacing):
                color = colors[(y // line_spacing) % len(colors)]
                points = []
                for x in range(0, 257, 5):
                    # Create oscillating wave
                    wave_y = y + int(10 * math.sin(x * 0.05 + y * 0.02))
                    points.append((x, wave_y))
                # Draw oscillating line
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 16:
            # Swirling Color Vortex
            cx, cy = 128, 128
            for angle in range(0, 360, 10):
                color = colors[(angle // 45) % len(colors)]
                for r in range(10, 120, 10):
                    # Create swirling effect
                    swirl_angle = angle + r * 0.05
                    x1 = cx + int(r * math.cos(swirl_angle))
                    y1 = cy + int(r * math.sin(swirl_angle))
                    x2 = cx + int((r + 8) * math.cos(swirl_angle + 0.2))
                    y2 = cy + int((r + 8) * math.sin(swirl_angle + 0.2))
                    if 0 <= x1 < 256 and 0 <= y1 < 256 and 0 <= x2 < 256 and 0 <= y2 < 256:
                        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        
        elif pattern_type == 17:
            # Popping Bubble Matrix
            bubble_size = 12
            for y in range(0, 256, bubble_size):
                for x in range(0, 256, bubble_size):
                    color = colors[((x//bubble_size + y//bubble_size) % len(colors))]
                    # Create popping effect
                    pop = int(4 * math.sin(x * 0.1 + y * 0.1))
                    draw.ellipse([x-pop, y-pop, x+bubble_size+pop, y+bubble_size+pop], fill=color)
        
        elif pattern_type == 18:
            # Dancing Geometric Shapes
            shape_size = 20
            for y in range(0, 256, shape_size):
                for x in range(0, 256, shape_size):
                    color = colors[((x//shape_size + y//shape_size) % len(colors))]
                    # Create dancing effect
                    dance_x = int(5 * math.sin(y * 0.1))
                    dance_y = int(5 * math.cos(x * 0.1))
                    shape_type = (x//shape_size + y//shape_size) % 3
                    if shape_type == 0:
                        draw.rectangle([x+dance_x, y+dance_y, x+shape_size+dance_x, y+shape_size+dance_y], fill=color)
                    elif shape_type == 1:
                        draw.ellipse([x+dance_x, y+dance_y, x+shape_size+dance_x, y+shape_size+dance_y], fill=color)
                    else:
                        points = [
                            (x+shape_size//2+dance_x, y+dance_y),
                            (x+shape_size+dance_x, y+shape_size+dance_y),
                            (x+dance_x, y+shape_size+dance_y)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 19:
            # Flowing Organic Forms
            for _ in range(20):
                start_x = random.randint(0, 255)
                start_y = random.randint(0, 255)
                color = random.choice(colors)
                points = []
                for i in range(10):
                    flow_x = start_x + int(30 * math.sin(i * 0.5))
                    flow_y = start_y + i * 25
                    if 0 <= flow_x < 256 and 0 <= flow_y < 256:
                        points.append((flow_x, flow_y))
                # Draw flowing curve
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=4)
        
        elif pattern_type == 20:
            # Shimmering Diagonal Waves
            for i in range(-256, 512):
                color = colors[i % len(colors)]
                points = []
                for y in range(0, 256, 8):
                    # Create shimmering diagonal wave
                    wave_x = i + int(15 * math.sin(y * 0.05 + i * 0.02))
                    if 0 <= wave_x < 256:
                        points.append((wave_x, y))
                # Draw shimmering wave
                for j in range(len(points)-1):
                    draw.line([points[j], points[j+1]], fill=color, width=3)
        
        elif pattern_type == 21:
            # Pulsating Circle Grid
            circle_size = 20
            for y in range(0, 256, circle_size):
                for x in range(0, 256, circle_size):
                    color = colors[((x//circle_size + y//circle_size) % len(colors))]
                    # Create pulsating effect
                    pulse = int(4 * math.sin(x * 0.1 + y * 0.1))
                    draw.ellipse([x-pulse, y-pulse, x+circle_size+pulse, y+circle_size+pulse], fill=color)
        
        elif pattern_type == 22:
            # Warping Square Pattern
            square_size = 24
            for y in range(0, 256, square_size):
                for x in range(0, 256, square_size):
                    color = colors[((x//square_size + y//square_size) % len(colors))]
                    # Create warping effect
                    warp_x = int(6 * math.sin(y * 0.08))
                    warp_y = int(6 * math.cos(x * 0.08))
                    points = [
                        (x + warp_x, y + warp_y),
                        (x + square_size + warp_x, y + warp_y),
                        (x + square_size + warp_x, y + square_size + warp_y),
                        (x + warp_x, y + square_size + warp_y)
                    ]
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 23:
            # Liquid Triangle Flow
            tri_size = 25
            for row in range(0, 12):
                for col in range(0, 12):
                    x = col * tri_size + (row % 2) * tri_size//2
                    y = row * tri_size * 0.866
                    if x < 256 and y < 256:
                        color = colors[((row + col) % len(colors))]
                        # Create liquid flow effect
                        flow_offset = int(8 * math.sin(x * 0.06 + y * 0.06))
                        points = [
                            (x + tri_size//2, y + flow_offset),
                            (x + tri_size + flow_offset, y + tri_size),
                            (x + flow_offset, y + tri_size)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 24:
            # Glitching Hexagon Field
            hex_size = 18
            for row in range(-2, 18):
                for col in range(-2, 18):
                    x = col * hex_size * 1.5 + (row % 2) * hex_size * 0.75
                    y = row * hex_size * 0.866
                    if -hex_size < x < 276 and -hex_size < y < 276:
                        color = colors[((row + col) % len(colors))]
                        # Apply glitch effect
                        if random.random() > 0.7:
                            glitch_offset = random.randint(-5, 5)
                            x += glitch_offset
                        points = []
                        for i in range(6):
                            angle = i * math.pi / 3
                            px = x + int(hex_size * 0.5 * math.cos(angle))
                            py = y + int(hex_size * 0.5 * math.sin(angle))
                            points.append((px, py))
                        if len(points) > 2:
                            draw.polygon(points, fill=color)
        
        elif pattern_type == 25:
            # Shifting Diamond Array
            diamond_size = 20
            for y in range(0, 256, diamond_size//2):
                for x in range(0, 256, diamond_size//2):
                    color = colors[((x//(diamond_size//2) + y//(diamond_size//2)) % len(colors))]
                    # Create shifting effect
                    shift_x = int(5 * math.sin(y * 0.1))
                    shift_y = int(5 * math.cos(x * 0.1))
                    points = [
                        (x + diamond_size//2 + shift_x, y + shift_y),
                        (x + diamond_size + shift_x, y + diamond_size//2 + shift_y),
                        (x + diamond_size//2 + shift_x, y + diamond_size + shift_y),
                        (x + shift_x, y + diamond_size//2 + shift_y)
                    ]
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 26:
            # Flowing Color Rivers
            for river in range(8):
                color = colors[river % len(colors)]
                start_x = random.randint(0, 255)
                points = []
                for y in range(0, 256, 4):
                    # Create flowing river effect
                    flow_x = start_x + int(40 * math.sin(y * 0.02 + river))
                    if 0 <= flow_x < 256:
                        points.append((flow_x, y))
                # Draw flowing river
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=6)
        
        elif pattern_type == 27:
            # Popping Geometric Bubbles
            bubble_size = 16
            for y in range(0, 256, bubble_size):
                for x in range(0, 256, bubble_size):
                    color = colors[((x//bubble_size + y//bubble_size) % len(colors))]
                    # Create popping bubble effect
                    pop_size = bubble_size + int(6 * math.sin(x * 0.1 + y * 0.1))
                    bubble_type = (x//bubble_size + y//bubble_size) % 2
                    if bubble_type == 0:
                        draw.ellipse([x, y, x+pop_size, y+pop_size], fill=color)
                    else:
                        points = [
                            (x + pop_size//2, y),
                            (x + pop_size, y + pop_size//2),
                            (x + pop_size//2, y + pop_size),
                            (x, y + pop_size//2)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 28:
            # Wobbling Line Matrix
            line_spacing = 12
            for y in range(0, 256, line_spacing):
                color = colors[(y // line_spacing) % len(colors)]
                points = []
                for x in range(0, 257, 6):
                    # Create wobbling effect
                    wobble_y = y + int(8 * math.sin(x * 0.08 + y * 0.03))
                    points.append((x, wobble_y))
                # Draw wobbling line
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 29:
            # Swirling Pattern Storm
            cx, cy = 128, 128
            for spiral in range(5):
                color = colors[spiral % len(colors)]
                points = []
                for i in range(50):
                    angle = i * 0.2 + spiral * math.pi / 2.5
                    r = i * 3
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw swirling pattern
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=2)
        
        elif pattern_type == 30:
            # Pulsating Geometric Field
            field_size = 22
            for y in range(0, 256, field_size):
                for x in range(0, 256, field_size):
                    color = colors[((x//field_size + y//field_size) % len(colors))]
                    # Create pulsating field effect
                    pulse = int(5 * math.sin(x * 0.08 + y * 0.08))
                    shape_type = (x//field_size + y//field_size) % 4
                    if shape_type == 0:
                        draw.rectangle([x-pulse, y-pulse, x+field_size+pulse, y+field_size+pulse], fill=color)
                    elif shape_type == 1:
                        draw.ellipse([x-pulse, y-pulse, x+field_size+pulse, y+field_size+pulse], fill=color)
                    elif shape_type == 2:
                        points = [
                            (x+field_size//2, y-pulse),
                            (x+field_size+pulse, y+field_size//2),
                            (x+field_size//2, y+field_size+pulse),
                            (x-pulse, y+field_size//2)
                        ]
                        draw.polygon(points, fill=color)
                    else:
                        points = [
                            (x+field_size//2, y-pulse),
                            (x+field_size+pulse, y+field_size),
                            (x-pulse, y+field_size)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 31:
            # Shimmering Color Waves
            for wave in range(8):
                color = colors[wave % len(colors)]
                points = []
                for x in range(0, 257, 4):
                    # Create shimmering wave effect
                    wave_y = 128 + int(60 * math.sin(x * 0.03 + wave * math.pi / 4))
                    points.append((x, wave_y))
                # Draw shimmering wave
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=4)
        
        elif pattern_type == 32:
            # Distorted Shape Grid
            grid_size = 20
            for y in range(0, 256, grid_size):
                for x in range(0, 256, grid_size):
                    color = colors[((x//grid_size + y//grid_size) % len(colors))]
                    # Create distortion effect
                    distort_x = int(6 * math.sin(y * 0.1))
                    distort_y = int(6 * math.cos(x * 0.1))
                    shape_type = (x//grid_size + y//grid_size) % 3
                    if shape_type == 0:
                        draw.rectangle([x+distort_x, y+distort_y, x+grid_size+distort_x, y+grid_size+distort_y], fill=color)
                    elif shape_type == 1:
                        draw.ellipse([x+distort_x, y+distort_y, x+grid_size+distort_x, y+grid_size+distort_y], fill=color)
                    else:
                        points = [
                            (x+grid_size//2+distort_x, y+distort_y),
                            (x+grid_size+distort_x, y+grid_size//2+distort_y),
                            (x+grid_size//2+distort_x, y+grid_size+distort_y),
                            (x+distort_x, y+grid_size//2+distort_y)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 33:
            # Flowing Pattern Stream
            for stream in range(6):
                color = colors[stream % len(colors)]
                points = []
                for i in range(60):
                    # Create flowing stream effect
                    x = i * 4 + int(20 * math.sin(i * 0.1 + stream))
                    y = 128 + int(40 * math.cos(i * 0.08 + stream))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw flowing stream
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=5)
        
        elif pattern_type == 34:
            # Warping Geometric Mesh
            mesh_size = 18
            for y in range(0, 256, mesh_size):
                for x in range(0, 256, mesh_size):
                    color = colors[((x//mesh_size + y//mesh_size) % len(colors))]
                    # Create warping effect
                    warp_x = int(8 * math.sin(y * 0.06 + x * 0.04))
                    warp_y = int(8 * math.cos(x * 0.06 + y * 0.04))
                    points = [
                        (x + warp_x, y + warp_y),
                        (x + mesh_size + warp_x, y + warp_y),
                        (x + mesh_size + warp_x, y + mesh_size + warp_y),
                        (x + warp_x, y + mesh_size + warp_y)
                    ]
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 35:
            # Liquid Color Flow
            for flow in range(10):
                color = colors[flow % len(colors)]
                points = []
                for i in range(80):
                    # Create liquid flow effect
                    x = i * 3 + int(30 * math.sin(i * 0.05 + flow))
                    y = flow * 25 + int(20 * math.cos(i * 0.03 + flow))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw liquid flow
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 36:
            # Popping Shape Matrix
            shape_size = 18
            for y in range(0, 256, shape_size):
                for x in range(0, 256, shape_size):
                    color = colors[((x//shape_size + y//shape_size) % len(colors))]
                    # Create popping effect
                    pop = int(6 * math.sin(x * 0.12 + y * 0.12))
                    shape_type = (x//shape_size + y//shape_size) % 3
                    if shape_type == 0:
                        draw.rectangle([x-pop, y-pop, x+shape_size+pop, y+shape_size+pop], fill=color)
                    elif shape_type == 1:
                        draw.ellipse([x-pop, y-pop, x+shape_size+pop, y+shape_size+pop], fill=color)
                    else:
                        points = [
                            (x+shape_size//2, y-pop),
                            (x+shape_size+pop, y+shape_size//2),
                            (x+shape_size//2, y+shape_size+pop),
                            (x-pop, y+shape_size//2)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 37:
            # Shifting Pattern Waves
            for wave in range(10):
                color = colors[wave % len(colors)]
                points = []
                for x in range(0, 257, 5):
                    # Create shifting wave effect
                    wave_y = wave * 25 + int(30 * math.sin(x * 0.04 + wave * 0.5))
                    if 0 <= wave_y < 256:
                        points.append((x, wave_y))
                # Draw shifting wave
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 38:
            # Wobbling Color Field
            field_size = 16
            for y in range(0, 256, field_size):
                for x in range(0, 256, field_size):
                    color = colors[((x//field_size + y//field_size) % len(colors))]
                    # Create wobbling field effect
                    wobble_x = int(4 * math.sin(y * 0.15))
                    wobble_y = int(4 * math.cos(x * 0.15))
                    draw.rectangle([x+wobble_x, y+wobble_y, x+field_size+wobble_x, y+field_size+wobble_y], fill=color)
        
        elif pattern_type == 39:
            # Swirling Geometric Flow
            cx, cy = 128, 128
            for flow in range(8):
                color = colors[flow % len(colors)]
                points = []
                for i in range(70):
                    angle = i * 0.15 + flow * math.pi / 4
                    r = i * 2.5
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw swirling flow
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=2)
        
        elif pattern_type == 40:
            # Pulsating Pattern Grid
            grid_size = 20
            for y in range(0, 256, grid_size):
                for x in range(0, 256, grid_size):
                    color = colors[((x//grid_size + y//grid_size) % len(colors))]
                    # Create pulsating effect
                    pulse = int(4 * math.sin(x * 0.1 + y * 0.1))
                    draw.rectangle([x-pulse, y-pulse, x+grid_size+pulse, y+grid_size+pulse], fill=color)
        
        elif pattern_type == 41:
            # Shimmering Shape Array
            shape_size = 22
            for y in range(0, 256, shape_size):
                for x in range(0, 256, shape_size):
                    color = colors[((x//shape_size + y//shape_size) % len(colors))]
                    # Create shimmering effect
                    shimmer = int(3 * math.sin(x * 0.1 + y * 0.1))
                    shape_type = (x//shape_size + y//shape_size) % 2
                    if shape_type == 0:
                        draw.rectangle([x-shimmer, y-shimmer, x+shape_size+shimmer, y+shape_size+shimmer], fill=color)
                    else:
                        draw.ellipse([x-shimmer, y-shimmer, x+shape_size+shimmer, y+shape_size+shimmer], fill=color)
        
        elif pattern_type == 42:
            # Flowing Geometric Storm
            cx, cy = 128, 128
            for storm in range(12):
                color = colors[storm % len(colors)]
                points = []
                for i in range(40):
                    angle = i * 0.3 + storm * math.pi / 6
                    r = i * 4 + int(10 * math.sin(i * 0.1))
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw flowing storm
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=2)
        
        elif pattern_type == 43:
            # Warping Color Matrix
            matrix_size = 15
            for y in range(0, 256, matrix_size):
                for x in range(0, 256, matrix_size):
                    color = colors[((x//matrix_size + y//matrix_size) % len(colors))]
                    # Create warping effect
                    warp_x = int(5 * math.sin(y * 0.2 + x * 0.1))
                    warp_y = int(5 * math.cos(x * 0.2 + y * 0.1))
                    draw.rectangle([x+warp_x, y+warp_y, x+matrix_size+warp_x, y+matrix_size+warp_y], fill=color)
        
        elif pattern_type == 44:
            # Liquid Pattern Flow
            for flow in range(15):
                color = colors[flow % len(colors)]
                points = []
                for i in range(60):
                    # Create liquid pattern flow
                    x = i * 4 + int(25 * math.sin(i * 0.08 + flow * 0.3))
                    y = flow * 17 + int(25 * math.cos(i * 0.06 + flow * 0.2))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw liquid pattern flow
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 45:
            # Popping Geometric Grid
            grid_size = 20
            for y in range(0, 256, grid_size):
                for x in range(0, 256, grid_size):
                    color = colors[((x//grid_size + y//grid_size) % len(colors))]
                    # Create popping effect
                    pop = int(5 * math.sin(x * 0.15 + y * 0.15))
                    shape_type = (x//grid_size + y//grid_size) % 4
                    if shape_type == 0:
                        draw.rectangle([x-pop, y-pop, x+grid_size+pop, y+grid_size+pop], fill=color)
                    elif shape_type == 1:
                        draw.ellipse([x-pop, y-pop, x+grid_size+pop, y+grid_size+pop], fill=color)
                    elif shape_type == 2:
                        points = [
                            (x+grid_size//2, y-pop),
                            (x+grid_size+pop, y+grid_size//2),
                            (x+grid_size//2, y+grid_size+pop),
                            (x-pop, y+grid_size//2)
                        ]
                        draw.polygon(points, fill=color)
                    else:
                        points = [
                            (x+grid_size//2, y-pop),
                            (x+grid_size+pop, y+grid_size),
                            (x-pop, y+grid_size)
                        ]
                        draw.polygon(points, fill=color)
        
        elif pattern_type == 46:
            # Shifting Color Waves
            for wave in range(12):
                color = colors[wave % len(colors)]
                points = []
                for x in range(0, 257, 4):
                    # Create shifting wave effect
                    wave_y = wave * 21 + int(35 * math.sin(x * 0.03 + wave * 0.4))
                    if 0 <= wave_y < 256:
                        points.append((x, wave_y))
                # Draw shifting wave
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 47:
            # Wobbling Pattern Field
            field_size = 18
            for y in range(0, 256, field_size):
                for x in range(0, 256, field_size):
                    color = colors[((x//field_size + y//field_size) % len(colors))]
                    # Create wobbling effect
                    wobble_x = int(6 * math.sin(y * 0.12 + x * 0.08))
                    wobble_y = int(6 * math.cos(x * 0.12 + y * 0.08))
                    draw.rectangle([x+wobble_x, y+wobble_y, x+field_size+wobble_x, y+field_size+wobble_y], fill=color)
        
        elif pattern_type == 48:
            # Swirling Color Matrix
            cx, cy = 128, 128
            for matrix in range(10):
                color = colors[matrix % len(colors)]
                points = []
                for i in range(50):
                    angle = i * 0.25 + matrix * math.pi / 5
                    r = i * 3 + int(8 * math.sin(i * 0.08))
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw swirling matrix
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=2)
        
        elif pattern_type == 49:
            # Flowing Pattern Storm
            for storm in range(8):
                color = colors[storm % len(colors)]
                points = []
                for i in range(80):
                    # Create flowing pattern storm
                    x = i * 3 + int(40 * math.sin(i * 0.05 + storm * 0.5))
                    y = storm * 32 + int(30 * math.cos(i * 0.04 + storm * 0.3))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                # Draw flowing pattern storm
                for i in range(len(points)-1):
                    draw.line([points[i], points[i+1]], fill=color, width=3)
        
        # Magicant-inspired patterns (25 new)
        elif pattern_type == 50:
            # Floating Magicant Islands
            for island in range(6):
                color = colors[island % len(colors)]
                cx, cy = random.randint(40, 216), random.randint(40, 216)
                # Floating island shape
                for i in range(20):
                    angle = i * math.pi / 10
                    r = 15 + int(10 * math.sin(i * 0.5))
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle)) + int(5 * math.sin(i * 0.3))
                    if 0 <= x < 256 and 0 <= y < 256:
                        draw.ellipse([x-2, y-2, x+2, y+2], fill=color)
        
        elif pattern_type == 51:
            # Psychedelic Sea of Stars
            for star in range(40):
                color = colors[star % len(colors)]
                cx, cy = random.randint(10, 246), random.randint(10, 246)
                # Star burst pattern
                for ray in range(8):
                    angle = ray * math.pi / 4
                    for r in range(1, 15):
                        x = cx + int(r * math.cos(angle))
                        y = cy + int(r * math.sin(angle))
                        if 0 <= x < 256 and 0 <= y < 256:
                            size = max(1, 3 - r // 5)
                            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        elif pattern_type == 52:
            # Dreamlike Flying Man
            cx, cy = 128, 128
            for spiral in range(3):
                color = colors[spiral % len(colors)]
                points = []
                for i in range(60):
                    angle = i * 0.15 + spiral * 2 * math.pi / 3
                    r = i * 2 + int(20 * math.sin(i * 0.1))
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 1:
                    draw.line(points, fill=color, width=2)
        
        elif pattern_type == 53:
            # Warping Reality Ripples
            cx, cy = 128, 128
            for ripple in range(12):
                color = colors[ripple % len(colors)]
                radius = ripple * 15
                points = []
                for angle in range(0, 360, 10):
                    rad = math.radians(angle)
                    warp = int(10 * math.sin(angle * 0.1 + ripple * 0.5))
                    x = cx + int((radius + warp) * math.cos(rad))
                    y = cy + int((radius + warp) * math.sin(rad))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 2:
                    draw.polygon(points, outline=color, width=2)
        
        elif pattern_type == 54:
            # Magicant's Twisted Trees
            for tree in range(8):
                color = colors[tree % len(colors)]
                x = tree * 32 + 16
                # Trunk
                for y in range(180, 220):
                    twist = int(5 * math.sin(y * 0.1))
                    if 0 <= x + twist < 256:
                        draw.line([x+twist, y, x+twist, y+2], fill=color, width=3)
                # Branches
                for branch in range(3):
                    by = 180 + branch * 10
                    for i in range(15):
                        bx = x + int((i+5) * math.sin(branch + i * 0.2))
                        by2 = by - i * 2
                        if 0 <= bx < 256 and 0 <= by2 < 256:
                            draw.ellipse([bx-1, by2-1, bx+1, by2+1], fill=color)
        
        elif pattern_type == 55:
            # Cosmic Mushroom Fields
            for mushroom in range(15):
                color = colors[mushroom % len(colors)]
                mx, my = random.randint(20, 236), random.randint(150, 230)
                # Stem
                for h in range(10):
                    draw.line([mx, my+h, mx, my+h+1], fill=color, width=2)
                # Cap
                cap_radius = 8 + int(4 * math.sin(mushroom * 0.5))
                draw.ellipse([mx-cap_radius, my-5, mx+cap_radius, my+5], fill=color)
                # Spots
                for spot in range(3):
                    sx = mx + random.randint(-cap_radius+2, cap_radius-2)
                    sy = my + random.randint(-3, 3)
                    spot_color = colors[(mushroom+1) % len(colors)]
                    draw.ellipse([sx-1, sy-1, sx+1, sy+1], fill=spot_color)
        
        elif pattern_type == 56:
            # Surreal Cloud Spirals
            for cloud in range(5):
                color = colors[cloud % len(colors)]
                cx, cy = random.randint(30, 226), random.randint(30, 226)
                for puff in range(20):
                    angle = puff * 0.3
                    r = puff * 3
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle)) + int(10 * math.sin(puff * 0.2))
                    size = 8 + int(4 * math.sin(puff * 0.3))
                    if 0 <= x < 256 and 0 <= y < 256:
                        draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        
        elif pattern_type == 57:
            # Mystical Statues Garden
            for statue in range(6):
                color = colors[statue % len(colors)]
                sx, sy = statue * 40 + 40, 180
                # Statue body
                for h in range(30):
                    width = 8 - h // 6
                    draw.line([sx-width, sy-h, sx+width, sy-h], fill=color, width=2)
                # Head
                draw.ellipse([sx-5, sy-35, sx+5, sy-25], fill=color)
                # Mystical glow
                glow_color = colors[(statue+1) % len(colors)]
                for g in range(3):
                    gx = sx + random.randint(-15, 15)
                    gy = sy - 20 + random.randint(-10, 10)
                    draw.ellipse([gx-2, gy-2, gx+2, gy+2], fill=glow_color)
        
        elif pattern_type == 58:
            # Flying Man's Sanctuary
            cx, cy = 128, 128
            for ring in range(8):
                color = colors[ring % len(colors)]
                radius = 20 + ring * 12
                # Sacred circle
                for angle in range(0, 360, 5):
                    rad = math.radians(angle)
                    x = cx + int(radius * math.cos(rad))
                    y = cy + int(radius * math.sin(rad))
                    if 0 <= x < 256 and 0 <= y < 256:
                        draw.ellipse([x-1, y-1, x+1, y+1], fill=color)
        
        elif pattern_type == 59:
            # Magicant's Color Rain
            for drop in range(30):
                color = colors[drop % len(colors)]
                x = drop * 8 + random.randint(-3, 3)
                for y in range(0, 256, 4):
                    ry = y + random.randint(0, 3)
                    if 0 <= x < 256 and 0 <= ry < 256:
                        length = 8 + int(4 * math.sin(drop * 0.5))
                        draw.line([x, ry, x, ry+length], fill=color, width=2)
        
        elif pattern_type == 60:
            # Distorted Flying Carpets
            for carpet in range(6):
                color = colors[carpet % len(colors)]
                cx, cy = random.randint(40, 216), random.randint(40, 216)
                points = []
                for i in range(16):
                    angle = i * math.pi / 8
                    r = 20 + int(15 * math.sin(i * 0.4 + carpet * 0.5))
                    x = cx + int(r * math.cos(angle))
                    y = cy + int(r * math.sin(angle)) + int(10 * math.cos(i * 0.3))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 2:
                    draw.polygon(points, fill=color)
        
        elif pattern_type == 61:
            # Psychedelic Bird Patterns
            for bird in range(8):
                color = colors[bird % len(colors)]
                cx, cy = bird * 30 + 30, random.randint(40, 150)
                # Bird body
                draw.ellipse([cx-8, cy-3, cx+8, cy+3], fill=color)
                # Wings
                for wing in [-1, 1]:
                    points = []
                    for i in range(10):
                        wx = cx + wing * (i * 2)
                        wy = cy + int(8 * math.sin(i * 0.3 + bird * 0.5))
                        if 0 <= wx < 256 and 0 <= wy < 256:
                            points.append((wx, wy))
                    if len(points) > 1:
                        draw.line(points, fill=color, width=2)
        
        elif pattern_type == 62:
            # Magicant's Melting Ground
            for stream in range(12):
                color = colors[stream % len(colors)]
                start_x = stream * 21 + 10
                points = []
                for x in range(start_x, min(start_x + 30, 256)):
                    y = 200 + int(20 * math.sin(x * 0.1 + stream * 0.3)) + int(x - start_x)
                    if 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 1:
                    for i in range(len(points)-1):
                        draw.line([points[i], points[i+1]], fill=color, width=3)
        
        elif pattern_type == 63:
            # Surreal Star Constellations
            stars = []
            for star in range(20):
                color = colors[star % len(colors)]
                sx, sy = random.randint(10, 246), random.randint(10, 246)
                stars.append((sx, sy, color))
                # Draw star
                for ray in range(4):
                    angle = ray * math.pi / 2
                    for r in range(1, 8):
                        x = sx + int(r * math.cos(angle))
                        y = sy + int(r * math.sin(angle))
                        if 0 <= x < 256 and 0 <= y < 256:
                            draw.ellipse([x-1, y-1, x+1, y+1], fill=color)
            # Connect stars
            for i in range(len(stars)-1):
                for j in range(i+1, min(i+3, len(stars))):
                    if random.random() > 0.5:
                        draw.line([stars[i][0], stars[i][1], stars[j][0], stars[j][1]], 
                                fill=stars[i][2], width=1)
        
        elif pattern_type == 64:
            # Dreamscape Water Ripples
            cx, cy = 128, 128
            for ripple_set in range(4):
                color = colors[ripple_set % len(colors)]
                offset = ripple_set * 40
                for ripple in range(5):
                    radius = ripple * 15 + offset
                    points = []
                    for angle in range(0, 360, 15):
                        rad = math.radians(angle)
                        wave = int(5 * math.sin(angle * 0.2 + ripple * 0.5))
                        x = cx + int((radius + wave) * math.cos(rad))
                        y = cy + int((radius + wave) * math.sin(rad))
                        if 0 <= x < 256 and 0 <= y < 256:
                            points.append((x, y))
                    if len(points) > 2:
                        draw.polygon(points, outline=color, width=1)
        
        elif pattern_type == 65:
            # Magicant's Floating Rocks
            for rock in range(10):
                color = colors[rock % len(colors)]
                rx, ry = random.randint(20, 236), random.randint(20, 236)
                size = random.randint(8, 20)
                # Irregular rock shape
                points = []
                for i in range(8):
                    angle = i * math.pi / 4
                    r = size + int(5 * math.sin(i * 0.7 + rock * 0.3))
                    x = rx + int(r * math.cos(angle))
                    y = ry + int(r * math.sin(angle))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 2:
                    draw.polygon(points, fill=color)
                # Mystical glow
                glow_color = colors[(rock+1) % len(colors)]
                draw.ellipse([rx-size-2, ry-size-2, rx+size+2, ry+size+2], 
                           outline=glow_color, width=1)
        
        elif pattern_type == 66:
            # Cosmic Energy Fields
            for field in range(6):
                color = colors[field % len(colors)]
                cx, cy = field * 40 + 40, 128
                # Energy waves
                for wave in range(8):
                    points = []
                    for i in range(30):
                        x = cx - 30 + i * 2
                        y = cy + int(15 * math.sin(i * 0.2 + wave * 0.5 + field * 0.3))
                        if 0 <= x < 256 and 0 <= y < 256:
                            points.append((x, y))
                    if len(points) > 1:
                        draw.line(points, fill=color, width=2)
        
        elif pattern_type == 67:
            # Psychedelic Flower Spirals
            for flower in range(5):
                color = colors[flower % len(colors)]
                cx, cy = flower * 50 + 30, random.randint(80, 180)
                # Flower petals in spiral
                for petal in range(12):
                    angle = petal * math.pi / 6
                    r = 15 + int(8 * math.sin(petal * 0.5))
                    px = cx + int(r * math.cos(angle))
                    py = cy + int(r * math.sin(angle))
                    if 0 <= px < 256 and 0 <= py < 256:
                        # Spiral petal
                        petal_points = []
                        for i in range(10):
                            spiral_angle = angle + i * 0.2
                            spiral_r = 5 + i
                            sx = px + int(spiral_r * math.cos(spiral_angle))
                            sy = py + int(spiral_r * math.sin(spiral_angle))
                            if 0 <= sx < 256 and 0 <= sy < 256:
                                petal_points.append((sx, sy))
                        if len(petal_points) > 1:
                            draw.line(petal_points, fill=color, width=2)
        
        elif pattern_type == 68:
            # Magicant's Twisted Reality
            cx, cy = 128, 128
            for twist in range(8):
                color = colors[twist % len(colors)]
                points = []
                for i in range(50):
                    angle = i * 0.2 + twist * math.pi / 4
                    r = i * 3
                    # Reality warp effect
                    warp_x = int(20 * math.sin(angle * 2 + twist))
                    warp_y = int(20 * math.cos(angle * 3 + twist))
                    x = cx + int(r * math.cos(angle)) + warp_x
                    y = cy + int(r * math.sin(angle)) + warp_y
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 1:
                    draw.line(points, fill=color, width=2)
        
        elif pattern_type == 69:
            # Surreal Moon Patterns
            for moon in range(4):
                color = colors[moon % len(colors)]
                mx, my = moon * 60 + 40, 60
                # Moon phases
                for phase in range(4):
                    px = mx + phase * 15
                    py = my + int(10 * math.sin(phase * 0.5))
                    if 0 <= px < 256 and 0 <= py < 256:
                        # Crescent shape
                        for i in range(8):
                            angle = i * math.pi / 4
                            if phase % 2 == 0:
                                r = 8
                            else:
                                r = 8 - i
                            x = px + int(r * math.cos(angle))
                            y = py + int(r * math.sin(angle))
                            if 0 <= x < 256 and 0 <= y < 256:
                                draw.ellipse([x-1, y-1, x+1, y+1], fill=color)
        
        elif pattern_type == 70:
            # Flying Man's Dream Path
            for path in range(3):
                color = colors[path % len(colors)]
                points = []
                for i in range(40):
                    x = i * 6 + path * 20
                    y = 128 + int(30 * math.sin(i * 0.1 + path * 2)) + int(20 * math.cos(i * 0.05))
                    if 0 <= x < 256 and 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 1:
                    draw.line(points, fill=color, width=3)
                    # Mystical stepping stones
                    for i in range(0, len(points), 5):
                        if i < len(points):
                            draw.ellipse([points[i][0]-3, points[i][1]-3, 
                                       points[i][0]+3, points[i][1]+3], fill=color)
        
        elif pattern_type == 71:
            # Magicant's Color Waves
            for wave in range(6):
                color = colors[wave % len(colors)]
                points = []
                for x in range(0, 256, 3):
                    y = wave * 40 + int(25 * math.sin(x * 0.05 + wave * 0.5))
                    if 0 <= y < 256:
                        points.append((x, y))
                if len(points) > 1:
                    for i in range(len(points)-1):
                        draw.line([points[i], points[i+1]], fill=color, width=2)
        
        elif pattern_type == 72:
            # Cosmic Dust Particles
            for particle in range(100):
                color = colors[particle % len(colors)]
                px = random.randint(5, 251)
                py = random.randint(5, 251)
                size = random.randint(1, 3)
                # Particle trail
                for trail in range(3):
                    tx = px + trail * random.randint(-2, 2)
                    ty = py + trail * random.randint(-2, 2)
                    if 0 <= tx < 256 and 0 <= ty < 256:
                        trail_size = max(1, size - trail)
                        draw.ellipse([tx-trail_size, ty-trail_size, 
                                   tx+trail_size, ty+trail_size], fill=color)
        
        elif pattern_type == 73:
            # Psychedelic Sky Bubbles
            for bubble in range(20):
                color = colors[bubble % len(colors)]
                cx, cy = random.randint(20, 236), random.randint(20, 236)
                # Rising bubble
                for size in range(1, 8):
                    by = cy - size * 5
                    if 0 <= by < 256:
                        # Bubble wobble
                        wobble = int(3 * math.sin(size * 0.5 + bubble))
                        bx = cx + wobble
                        if 0 <= bx < 256:
                            draw.ellipse([bx-size, by-size, bx+size, by+size], 
                                       outline=color, width=1)
        
        elif pattern_type == 74:
            # Magicant's Mystical Maze
            cell_size = 16
            for row in range(16):
                for col in range(16):
                    if random.random() > 0.3:  # 70% chance of wall
                        color = colors[(row + col) % len(colors)]
                        x, y = col * cell_size, row * cell_size
                        # Maze wall with mystical gaps
                        for i in range(cell_size):
                            if random.random() > 0.2:  # 80% chance of wall segment
                                if random.choice([True, False]):
                                    # Horizontal wall segment
                                    if x + i < 256:
                                        draw.line([x+i, y, x+i, y+2], fill=color, width=2)
                                else:
                                    # Vertical wall segment
                                    if y + i < 256:
                                        draw.line([x, y+i, x+2, y+i], fill=color, width=2)
        
        return img
    
    def _open_background_generator(self):
        """Open the background generator popup window.
        
        Creates a popup with preview, zoom/hue controls, and buttons to
        generate, save, and load custom backgrounds.
        """
        popup = ctk.CTkToplevel(self)
        popup.title("Background Generator")
        popup.geometry("450x700")
        popup.grab_set()
        popup.resizable(False, False)
        
        # Preview frame
        preview_frame = ctk.CTkFrame(popup, fg_color="#1a1a1a")
        preview_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Pattern name label
        self.pattern_name_label = ctk.CTkLabel(preview_frame, text="", font=("Arial", 12, "bold"), text_color="#3498db")
        self.pattern_name_label.pack(pady=(10, 5))
        
        ctk.CTkLabel(preview_frame, text="Generated Background", font=("Arial", 14, "bold")).pack(pady=5)
        
        # Generate initial background
        self.generated_bg = self._generate_earthbound_background()
        self.generated_bg_original = self.generated_bg.copy()
        self.generated_bg_zoom = 1.0
        self.generated_bg_hue = 0
        
        # Initialize sliders
        self.bg_zoom_slider = None
        self.bg_hue_slider = None
        
        # Update display
        self._update_background_display()
        
        self.bg_preview_label = ctk.CTkLabel(preview_frame, image=self.generated_bg_ctk, text="")
        self.bg_preview_label.pack(pady=10)
        
        # Sliders frame
        sliders_frame = ctk.CTkFrame(preview_frame, fg_color="#222222")
        sliders_frame.pack(pady=15, padx=15, fill="x")
        
        ctk.CTkLabel(sliders_frame, text="Adjustments", font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        # Zoom slider
        zoom_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        zoom_frame.pack(pady=8, padx=10, fill="x")
        ctk.CTkLabel(zoom_frame, text="Zoom:", width=60, font=("Arial", 10)).pack(side="left", padx=(0, 10))
        self.bg_zoom_slider = ctk.CTkSlider(zoom_frame, from_=0.5, to=3.0, number_of_steps=25, 
                                          command=self._on_bg_zoom_change)
        self.bg_zoom_slider.set(1.0)
        self.bg_zoom_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.bg_zoom_label = ctk.CTkLabel(zoom_frame, text="1.0x", width=40, font=("Arial", 10))
        self.bg_zoom_label.pack(side="left")
        
        # Hue slider
        hue_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        hue_frame.pack(pady=8, padx=10, fill="x")
        ctk.CTkLabel(hue_frame, text="Hue:", width=60, font=("Arial", 10)).pack(side="left", padx=(0, 10))
        self.bg_hue_slider = ctk.CTkSlider(hue_frame, from_=0, to=360, number_of_steps=72, 
                                          command=self._on_bg_hue_change)
        self.bg_hue_slider.set(0)
        self.bg_hue_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.bg_hue_label = ctk.CTkLabel(hue_frame, text="0°", width=40, font=("Arial", 10))
        self.bg_hue_label.pack(side="left")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(popup, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        # Generate button
        ctk.CTkButton(buttons_frame, text="Generate", fg_color="#3498db", hover_color="#2980b9", 
                     width=100, height=40, command=self._regenerate_background).pack(side="left", padx=10)
        
        # Save button
        ctk.CTkButton(buttons_frame, text="Save", fg_color="#2ecc71", hover_color="#27ae60", 
                     width=100, height=40, command=self._save_generated_background).pack(side="left", padx=10)
        
        # Load button
        ctk.CTkButton(buttons_frame, text="Load", fg_color="#e67e22", hover_color="#d35400", 
                     width=100, height=40, command=lambda: self._open_load_background_popup(popup)).pack(side="left", padx=10)
        
        self.bg_generator_popup = popup
    
    def _update_background_display(self):
        """Update the background display with current zoom and hue settings.
        
        Applies zoom scaling and hue shift to the generated background
        and updates the preview display.
        """
        # Apply zoom
        if self.generated_bg_zoom != 1.0:
            new_size = int(256 * self.generated_bg_zoom)
            bg = self.generated_bg_original.resize((new_size, new_size), Image.Resampling.LANCZOS)
            # Crop to 256x256 if zoomed in
            if new_size > 256:
                left = (new_size - 256) // 2
                top = (new_size - 256) // 2
                bg = bg.crop((left, top, left + 256, top + 256))
        else:
            bg = self.generated_bg_original
        
        # Apply hue shift if needed
        if self.generated_bg_hue != 0:
            bg = self._apply_hue_shift(bg, self.generated_bg_hue)
        
        # Update display
        self.generated_bg = bg
        self.generated_bg_display = bg.resize((300, 300), Image.Resampling.LANCZOS)
        self.generated_bg_ctk = ctk.CTkImage(light_image=self.generated_bg_display, size=(300, 300))
        
        # Check if the preview label still exists before updating
        if hasattr(self, 'bg_preview_label') and self.bg_preview_label.winfo_exists():
            try:
                self.bg_preview_label.configure(image=self.generated_bg_ctk)
            except:
                pass  # Widget might be in the process of being destroyed
        
        # Update pattern name display
        if hasattr(self, 'pattern_name_label') and self.pattern_name_label.winfo_exists():
            try:
                self.pattern_name_label.configure(text=f"Pattern: {self.current_pattern_name}")
            except:
                pass

    def _save_generated_background(self):
        """Save the generated background to the Generated Backgrounds folder.
        
        Saves with a timestamped filename and handles duplicate naming.
        """
        from datetime import datetime
        
        # Get current date and use a simple pattern name
        date_str = datetime.now().strftime("%Y-%m-%d")
        pattern_name = "GeneratedPattern"
        
        filename = f"BG:{date_str}_{pattern_name}.png"
        filepath = os.path.join(GENERATED_BG_DIR, filename)
        
        # Check if file already exists and add number if needed
        counter = 1
        original_filename = filename
        while os.path.exists(filepath):
            filename = f"BG:{date_str}_{pattern_name}_{counter}.png"
            filepath = os.path.join(GENERATED_BG_DIR, filename)
            counter += 1
        
        # Save the background
        self.generated_bg.save(filepath, "PNG")
        
        # Refresh background files list
        self._load_asset_lists()
        
        messagebox.showinfo("Success", f"Background saved as {filename}")

    def _apply_hue_shift(self, img, hue_shift):
        """Apply hue shift to an image.
        
        Args:
            img: PIL Image to shift
            hue_shift: Hue shift amount in degrees (0-360)
            
        Returns:
            PIL Image with hue-shifted colors
        """
        import colorsys
        # Convert to RGBA to preserve alpha channel
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        pixels = img.load()
        
        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]
                
                # Skip transparent pixels
                if a == 0:
                    continue
                
                # Convert RGB to HSV using colorsys (hue range 0-1)
                h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
                
                # Shift hue (convert from 0-360 to 0-1 range)
                h = (h + hue_shift / 360.0) % 1.0
                
                # Convert back to RGB
                r, g, b = colorsys.hsv_to_rgb(h, s, v)
                pixels[x, y] = (int(r*255), int(g*255), int(b*255), a)
        
        return img
    
    def _rgb_to_hsv(self, r, g, b):
        """Convert RGB color values to HSV.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
            
        Returns:
            Tuple of (hue, saturation, value) where hue is 0-360, s and v are 0-1
        """
        r, g, b = r/255.0, g/255.0, b/255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx-mn
        
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g-b)/df) + 360) % 360
        elif mx == g:
            h = (60 * ((b-r)/df) + 120) % 360
        elif mx == b:
            h = (60 * ((r-g)/df) + 240) % 360
        
        s = 0 if mx == 0 else df/mx
        v = mx
        return h, s, v
    
    def _hsv_to_rgb(self, h, s, v):
        """Convert HSV color values to RGB.
        
        Args:
            h: Hue component (0-360)
            s: Saturation component (0-1)
            v: Value component (0-1)
            
        Returns:
            Tuple of (red, green, blue) with values 0-255
        """
        h = h/60
        c = v * s
        x = c * (1 - abs((h % 2) - 1))
        m = v - c
        
        if 0 <= h < 1:
            r, g, b = c, x, 0
        elif 1 <= h < 2:
            r, g, b = x, c, 0
        elif 2 <= h < 3:
            r, g, b = 0, c, x
        elif 3 <= h < 4:
            r, g, b = 0, x, c
        elif 4 <= h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        r = int((r + m) * 255)
        g = int((g + m) * 255)
        b = int((b + m) * 255)
        return r, g, b
    
    def _on_bg_zoom_change(self, value):
        """Handle zoom slider change in background generator."""
        self.generated_bg_zoom = value
        self.bg_zoom_label.configure(text=f"{value:.1f}x")
        self._update_background_display()
    
    def _on_bg_hue_change(self, value):
        """Handle hue slider change in background generator."""
        self.generated_bg_hue = int(value)
        self.bg_hue_label.configure(text=f"{int(value)}°")
        self._update_background_display()
    
    def _regenerate_background(self):
        """Regenerate a new random background pattern."""
        self.generated_bg = self._generate_earthbound_background()
        self.generated_bg_original = self.generated_bg.copy()
        
        # Reset sliders to default
        if hasattr(self, 'bg_zoom_slider'):
            self.bg_zoom_slider.set(1.0)
            self.bg_hue_slider.set(0)
        self.generated_bg_zoom = 1.0
        self.generated_bg_hue = 0
        
        # Update display
        self._update_background_display()
        
        # Update pattern name display
        self.pattern_name_label.configure(text=f"Pattern: {self.current_pattern_name}")
    
    def _save_generated_background(self):
        """Save the generated background to the Generated Backgrounds folder.
        
        Uses numbered naming (Custombg_1.png, Custombg_2.png, etc.)
        to maintain order.
        """
        # Find next available number
        existing_files = [f for f in os.listdir(GENERATED_BG_DIR) if f.startswith("Custombg_") and f.endswith(".png")]
        numbers = []
        for f in existing_files:
            try:
                num = int(f.replace("Custombg_", "").replace(".png", ""))
                numbers.append(num)
            except:
                pass
        
        next_num = 1
        while numbers and next_num in numbers:
            next_num += 1
        
        filename = f"Custombg_{next_num}.png"
        filepath = os.path.join(GENERATED_BG_DIR, filename)
        
        # Save the background
        self.generated_bg.save(filepath, "PNG")
        
        # Refresh background files list
        self._load_asset_lists()
        
        messagebox.showinfo("Success", f"Background saved as {filename}")
    
    def _open_load_background_popup(self, parent_popup):
        """Open a popup to load and manage custom backgrounds.
        
        Shows a grid of saved custom backgrounds with load and delete buttons.
        
        Args:
            parent_popup: The parent background generator popup
        """
        popup = ctk.CTkToplevel(self)
        popup.title("Load Custom Background")
        popup.geometry("800x600")
        popup.grab_set()
        popup.resizable(True, True)
        
        ctk.CTkLabel(popup, text="Select a Custom Background", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Scrollable frame for backgrounds
        scroll_frame = ctk.CTkScrollableFrame(popup, fg_color="#1a1a1a", width=750, height=450)
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Get custom backgrounds
        custom_bgs = [f for f in os.listdir(GENERATED_BG_DIR) if f.startswith("Custombg_") and f.endswith(".png")]
        custom_bgs.sort(key=lambda x: int(x.replace("Custombg_", "").replace(".png", "")))
        
        if not custom_bgs:
            ctk.CTkLabel(scroll_frame, text="No custom backgrounds found. Generate and save some first!", 
                        font=("Arial", 12)).pack(pady=50)
        else:
            # Create grid of background previews
            for i, bg_file in enumerate(custom_bgs):
                row = i // 3
                col = i % 3
                
                frame = ctk.CTkFrame(scroll_frame, fg_color="#222222", corner_radius=8)
                frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
                
                # Load and display preview
                try:
                    bg_path = os.path.join(GENERATED_BG_DIR, bg_file)
                    bg_img = Image.open(bg_path).convert("RGBA")
                    bg_preview = bg_img.resize((200, 200), Image.Resampling.LANCZOS)
                    bg_ctk = ctk.CTkImage(light_image=bg_preview, size=(200, 200))
                    
                    img_label = ctk.CTkLabel(frame, image=bg_ctk, text="")
                    img_label.pack(pady=10)
                    
                    # Filename label
                    name_label = ctk.CTkLabel(frame, text=bg_file.replace(".png", ""), font=("Arial", 10))
                    name_label.pack(pady=5)
                    
                    # Buttons
                    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                    btn_frame.pack(pady=5)
                    
                    ctk.CTkButton(btn_frame, text="Load", width=60, height=30, fg_color="#3498db", 
                                 hover_color="#2980b9", command=lambda f=bg_file: self._load_custom_background(f, popup)).pack(side="left", padx=2)
                    
                    ctk.CTkButton(btn_frame, text="Delete", width=60, height=30, fg_color="#e74c3c", 
                                 hover_color="#c0392b", command=lambda f=bg_file: self._delete_custom_background(f, popup)).pack(side="left", padx=2)
                    
                except Exception as e:
                    ctk.CTkLabel(frame, text=f"Error loading {bg_file}", font=("Arial", 10), text_color="#e74c3c").pack(pady=10)
        
        # Close button
        ctk.CTkButton(popup, text="Close", fg_color="#95a5a6", hover_color="#7f8c8d", 
                     width=100, height=40, command=popup.destroy).pack(pady=10)
    
    def _load_custom_background(self, filename, popup):
        """Load a custom background and apply it to the current icon.
        
        Args:
            filename: Name of the custom background file
            popup: The load popup to close after loading
        """
        try:
            bg_path = os.path.join(GENERATED_BG_DIR, filename)
            
            # Ensure custom_bg_files list exists and is up to date
            if not hasattr(self, 'custom_bg_files'):
                self.custom_bg_files = []
            
            # Add to custom_bg_files if not already there
            if filename not in self.custom_bg_files:
                self.custom_bg_files.append(filename)
            
            # Calculate the correct index for this custom background
            custom_index = len(self.bg_files) + self.custom_bg_files.index(filename)
            
            # Add to background cache with the correct index
            self.bg_cache[custom_index] = Image.open(bg_path).convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
            
            # Set current background to this specific custom background
            self.current_bg_index = custom_index
            self._debounced_update()
            
            popup.destroy()
            self.bg_generator_popup.destroy()
            
            messagebox.showinfo("Success", f"Loaded {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background: {str(e)}")
    
    def _delete_custom_background(self, filename, popup):
        """Delete a custom background and rename others to maintain order.
        
        After deletion, renumbers remaining backgrounds to fill the gap
        and updates any templates that referenced the deleted background.
        
        Args:
            filename: Name of the background file to delete
            popup: The load popup to refresh after deletion
        """
        try:
            # Confirm deletion
            result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {filename}?")
            if not result:
                return
            
            # Delete the file
            bg_path = os.path.join(GENERATED_BG_DIR, filename)
            os.remove(bg_path)
            
            # Get the number of the deleted background
            deleted_num = int(filename.replace("Custombg_", "").replace(".png", ""))
            
            # Rename all backgrounds with higher numbers to maintain order
            existing_files = [f for f in os.listdir(GENERATED_BG_DIR) if f.startswith("Custombg_") and f.endswith(".png")]
            existing_nums = sorted([int(f.replace("Custombg_", "").replace(".png", "")) for f in existing_files])
            
            for num in existing_nums:
                if num > deleted_num:
                    old_path = os.path.join(GENERATED_BG_DIR, f"Custombg_{num}.png")
                    new_path = os.path.join(GENERATED_BG_DIR, f"Custombg_{num-1}.png")
                    os.rename(old_path, new_path)
            
            # Update templates that reference the deleted background
            self._update_templates_after_background_deletion(deleted_num)
            
            # Refresh the popup
            popup.destroy()
            self._open_load_background_popup(self.bg_generator_popup)
            
            messagebox.showinfo("Success", f"Deleted {filename} and reordered backgrounds")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete background: {str(e)}")
    
    def _update_templates_after_background_deletion(self, deleted_bg_num):
        """Update templates that reference deleted custom backgrounds.
        
        Adjusts or resets background indices in templates to handle
        the renumbering after deletion.
        
        Args:
            deleted_bg_num: The number of the deleted background
        """
        for i, template in enumerate(self.templates):
            # Check if template uses a custom background that was deleted
            if hasattr(template, 'current_bg_index') and template['current_bg_index'] >= len(self.bg_files):
                # Reset to first background
                template['current_bg_index'] = 0
            elif template['current_bg_index'] == deleted_bg_num:
                # This template used the deleted background, reset to first
                template['current_bg_index'] = 0
            elif template['current_bg_index'] > deleted_bg_num:
                # Adjust index for renumbered backgrounds
                template['current_bg_index'] -= 1
        
        # Save updated templates
        self._save_templates()

    def _create_default_templates(self):
        """Create default template configurations.
        
        Returns a list of 6 template dictionaries with default settings
        for different icon configurations.
        
        Returns:
            List of template dictionaries
        """
        base = {"line_hues": [0.0, 0.0, 0.0], "line_rainbows": [False, False, False], "line_outlines": [True, True, True], "line_font_size_offsets": [0, 0, 0], "line_font_spacing_offsets": [0, 0, 0], "line_text_offset_xs": [0, 0, 0], "line_text_offset_ys": [4, 4, 4], "line_active": [True, True, True], "bg_hue": 0.0, "bg_brightness": 1.0, "zoom_level": 50, "offset_x": 0, "offset_y": 0, "stretch_x": 1.0, "stretch_y": 1.0, "brightness": 0.9, "crt_enabled": True, "bg_scale": 1.0, "bg_offset_x": 0, "bg_offset_y": 0, "frame_offset_x": 0, "frame_offset_y": 0, "scanline_alpha": 20, "current_bg_index": 0, "current_frame_index": 0, "current_font_index": 0, "line_spacing_offset": -10, "font_position_step": 1, "decor_enabled": True, "current_decor_index": 0, "decor_scale": 1.0, "decor_offset_x": 0, "decor_offset_y": 0}
        templates = []
        for i in range(6):
            t = dict(base)
            t["title_lines"] = [f"Template {i+1}"]
            t["current_bg_index"] = min(i, 4)
            t["current_frame_index"] = [0, 0, 1, 2, 3, 1][i]
            templates.append(t)
        return templates


if __name__ == "__main__":
    app = SNESIconGenerator()
    app.mainloop()
