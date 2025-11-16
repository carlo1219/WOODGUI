import tkinter as tk  # Still need standard tkinter for Canvas
import customtkinter as ctk
from datetime import datetime
import time

# =============================================================================
# UI CONFIGURATION SECTION - Customize the user interface appearance and behavior
# =============================================================================

# ------------------------------------------------------------------------------
# WINDOW AND DISPLAY SETTINGS
# ------------------------------------------------------------------------------
WINDOW_SCALE = 0.65
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600
ENABLE_FULLSCREEN_STARTUP = True

# ------------------------------------------------------------------------------
# FONT SETTINGS
# ------------------------------------------------------------------------------
PRIMARY_FONT_FAMILY = "Helvetica"
BUTTON_FONT_FAMILY = "Helvetica"
MONOSPACE_FONT_FAMILY = "Courier"

FONT_SIZE_DIVISOR = 60  # Changed from 80 to make fonts larger
FONT_SIZE_BASE_MIN = 10  # Changed from 8
FONT_SIZE_BASE_MAX = 16  # Changed from 12

# ------------------------------------------------------------------------------
# COLOR THEME SETTINGS - DARK MODE (Inverted Colors)
# ------------------------------------------------------------------------------
BACKGROUND_COLOR = "#1a1a1a"  # Dark background (inverted from #f0f0f0)
FRAME_BACKGROUND_COLOR = "#2d2d2d"  # Dark frame background (inverted from #ffffff)
TEXT_COLOR = "#e0e0e0"  # Light text (inverted from #000000)
SECONDARY_TEXT_COLOR = "#999999"  # Light secondary text (inverted from #666666)

BUTTON_BACKGROUND_COLOR = "#3d3d3d"  # Dark button (inverted from #e0e0e0)
BUTTON_ACTIVE_COLOR = "#4d4d4d"  # Slightly lighter on press (inverted from #d0d0d0)
BUTTON_TEXT_COLOR = "#e0e0e0"  # Light button text (inverted from #000000)

STATUS_READY_COLOR = "#28a745"  # Keep green for ready
STATUS_WARNING_COLOR = "#ffc107"  # Keep yellow for warning
STATUS_ERROR_COLOR = "#dc3545"  # Keep red for error

GRADE_PERFECT_COLOR = "#32CD32"  # Bright green for perfect
GRADE_GOOD_COLOR = "#90EE90"  # Light green for good
GRADE_FAIR_COLOR = "#FFB347"  # Light orange for fair
GRADE_POOR_COLOR = "#FF6B6B"  # Light red for poor

DETECTION_BOX_COLOR = "#00FF00"  # Keep bright green
ROI_OVERLAY_COLOR = "#FFFF00"  # Keep yellow

# ------------------------------------------------------------------------------
# LAYOUT AND SPACING SETTINGS
# ------------------------------------------------------------------------------
MAIN_PADDING = 5
FRAME_PADDING = 2
CAMERA_FRAME_PADDING = 1
ELEMENT_PADDING_X = 2
ELEMENT_PADDING_Y = 2
LABEL_PADDING = 5

CAMERA_FEEDS_WEIGHT = 0
CONTROLS_WEIGHT = 0
STATS_WEIGHT = 1
CAMERA_FEED_HEIGHT_WEIGHT = 0

CAMERA_ASPECT_RATIO = "16:9"
CAMERA_DISPLAY_MARGIN = -35
CAMERA_FEED_MARGIN = 0

# ------------------------------------------------------------------------------
# UI BEHAVIOR SETTINGS
# ------------------------------------------------------------------------------
ENABLE_TOOLTIPS = True
ENABLE_ANIMATIONS = False
AUTO_SCROLL_LOGS = True
SCROLL_SENSITIVITY = 3

UI_UPDATE_SKIP = 3
STATS_UPDATE_SKIP = 15
LOG_UPDATE_SKIP = 10

# ------------------------------------------------------------------------------
# ADVANCED UI SETTINGS
# ------------------------------------------------------------------------------
STATS_TAB_HEIGHT = 200
LOG_SCROLLABLE_HEIGHT = 200

STATUS_BAR_HEIGHT = 25
STATUS_UPDATE_INTERVAL = 100

DETECTION_DETAILS_HEIGHT = 150
MAX_DETECTION_ENTRIES = 50

# =============================================================================
# END OF UI CONFIGURATION SECTION
# =============================================================================


class GUIOnlyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.title("Wood Sorting Application - Modern UI (CustomTkinter)")

        # Get screen dimensions for dynamic sizing
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate window size
        if ENABLE_FULLSCREEN_STARTUP:
            self.attributes("-fullscreen", True)
            self.is_fullscreen = True
            window_width = screen_width
            window_height = screen_height
        else:
            window_width = int(screen_width * WINDOW_SCALE)
            window_height = int(screen_height * WINDOW_SCALE)
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.resizable(True, True)
        self.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Fullscreen keybindings
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # Calculate responsive font sizes
        base_font_size = max(FONT_SIZE_BASE_MIN, min(FONT_SIZE_BASE_MAX, int(screen_height / FONT_SIZE_DIVISOR)))
        self.font_small = (PRIMARY_FONT_FAMILY, base_font_size - 1)
        self.font_normal = (PRIMARY_FONT_FAMILY, base_font_size)
        self.font_large = (PRIMARY_FONT_FAMILY, base_font_size + 2, "bold")
        self.font_button = (BUTTON_FONT_FAMILY, base_font_size, "bold")

        # Initialize variables
        self.total_pieces_processed = 0
        self.session_start_time = time.time()
        self.grade_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        self.live_stats = {"grade1": 0, "grade2": 0, "grade3": 0, "grade4": 0, "grade5": 0}
        self.current_mode = "IDLE"
        
        # Camera display dimensions - match GUIonly.py exactly
        self.canvas_width = screen_width // 2 - 25
        self.canvas_height = 360

        self.create_gui()
        
        # Set close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_gui(self):
        """Create all GUI components with CustomTkinter"""
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate layout dimensions
        camera_feed_width = (screen_width - 30) // 3  # 1/3 for each camera feed
        middle_width = (screen_width - 30) // 3       # 1/3 for defects boxes
        right_width = (screen_width - 30) // 3        # 1/3 for report and grading
        
        left_x = 10
        middle_x = left_x + camera_feed_width + 10
        right_x = middle_x + middle_width + 10
        
        camera_height = 280
        
        # =====================
        # LEFT SIDE - Camera Feeds with Grade Display
        # =====================
        
        # Top Camera Feed
        self.top_canvas = tk.Canvas(self, width=camera_feed_width, height=camera_height, 
                                   bg='black', highlightbackground="#555555", highlightthickness=2)
        self.top_canvas.place(x=left_x, y=10)
        
        # Top Camera Grade Box
        top_grade_y = 10 + camera_height + 10
        top_grade_height = 50
        top_grade_frame = ctk.CTkFrame(self, width=camera_feed_width, height=top_grade_height, corner_radius=6)
        top_grade_frame.place(x=left_x, y=top_grade_y)
        top_grade_frame.pack_propagate(False)
        
        # Horizontal layout with label on left and grade on right
        grade_container = ctk.CTkFrame(top_grade_frame, fg_color="transparent")
        grade_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        ctk.CTkLabel(grade_container, text="Top Wood Grade:", font=("Arial", 20, "bold")).pack(side="left", padx=(0, 5))
        self.top_grade_label = ctk.CTkLabel(grade_container, text="No Grade",
                                           text_color="#FFB347", font=("Arial", 20, "bold"))
        self.top_grade_label.pack(side="right", expand=True)
        
        # Bottom Camera Feed
        self.bottom_canvas = tk.Canvas(self, width=camera_feed_width, height=camera_height,
                                      bg='black', highlightbackground="#555555", highlightthickness=2)
        self.bottom_canvas.place(x=left_x, y=top_grade_y + top_grade_height + 10)
        
        # Bottom Camera Grade Box
        bot_grade_y = top_grade_y + top_grade_height + 10 + camera_height + 10
        bot_grade_height = 50
        bot_grade_frame = ctk.CTkFrame(self, width=camera_feed_width, height=bot_grade_height, corner_radius=6)
        bot_grade_frame.place(x=left_x, y=bot_grade_y)
        bot_grade_frame.pack_propagate(False)
        
        # Horizontal layout with label on left and grade on right
        bot_grade_container = ctk.CTkFrame(bot_grade_frame, fg_color="transparent")
        bot_grade_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        ctk.CTkLabel(bot_grade_container, text="Bot Wood Grade:", font=("Arial", 20, "bold")).pack(side="left", padx=(0, 5))
        self.bot_grade_label = ctk.CTkLabel(bot_grade_container, text="No Grade", 
                                           text_color="#FFB347", font=("Arial", 20, "bold"))
        self.bot_grade_label.pack(side="right", expand=True)
        
        # System Status
        status_y = bot_grade_y + bot_grade_height + 10
        status_height = 70
        status_frame = ctk.CTkFrame(self, width=camera_feed_width, height=status_height, corner_radius=6)
        status_frame.place(x=left_x, y=status_y)
        status_frame.pack_propagate(False)
        
        ctk.CTkLabel(status_frame, text="System Status", font=("Arial", 20, "bold")).pack(pady=(4, 2))
        
        self.status_label = tk.Text(status_frame, font=("Arial",20), wrap=tk.WORD,
                                   height=2, width=int(camera_feed_width/8), state=tk.DISABLED, relief="flat",
                                   background=FRAME_BACKGROUND_COLOR, foreground=TEXT_COLOR,
                                   insertbackground=TEXT_COLOR, borderwidth=0)
        self.status_label.pack(pady=(2, 3), padx=6, fill="both", expand=True)
        self.update_status_text("Status: Ready")
        
        # Conveyor Control
        control_y = status_y + status_height + 10
        # Calculate available height from control_y to near bottom, leaving margin
        control_height = screen_height - control_y - 30
        if control_height < 60:
            control_height = 60
        
        control_frame = ctk.CTkFrame(self, width=camera_feed_width, height=control_height, corner_radius=6)
        control_frame.place(x=left_x, y=control_y)
        control_frame.pack_propagate(False)
        
        ctk.CTkLabel(control_frame, text="Conveyor Control", font=("Arial", 20, "bold")).pack(pady=(4, 4))
        
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        
        button_width = int((camera_feed_width - 20) / 2)
        ctk.CTkButton(
            button_frame, text="ON", command=lambda: self.set_mode("SCAN_PHASE"),
            fg_color="#28a745", hover_color="#218838", corner_radius=6,
            font=("Arial", 20, "bold"), width=button_width
        ).pack(side="left", padx=2, fill="both", expand=True)
        
        ctk.CTkButton(
            button_frame, text="OFF", command=lambda: self.set_mode("IDLE"),
            fg_color="#6c757d", hover_color="#5a6268", corner_radius=6,
            font=("Arial", 20, "bold"), width=button_width
        ).pack(side="left", padx=2, fill="both", expand=True)
        
        # =====================
        # MIDDLE - Defects Boxes (beside camera feeds)
        # =====================
        
        # Top Defects Box (extend down to bottom of Top Grade box)
        # Height should span from top of camera (y=10) to bottom of top-grade box
        top_defects_height = camera_height + top_grade_height + 10
        top_defects_frame = ctk.CTkFrame(self, width=middle_width, height=top_defects_height, corner_radius=6)
        top_defects_frame.place(x=middle_x, y=10)
        top_defects_frame.pack_propagate(False)
        
        ctk.CTkLabel(top_defects_frame, text="Top Defects", font=("Arial", 20, "bold")).pack(pady=(5, 3))
        
        top_defects_scroll = ctk.CTkScrollableFrame(top_defects_frame, width=middle_width - 20, 
                                                    height=top_defects_height - 40, fg_color="transparent")
        top_defects_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 5))
        
        self.top_defects_label = ctk.CTkLabel(top_defects_scroll, text="No defects detected",
                                             text_color=SECONDARY_TEXT_COLOR, font=("Arial", 20))
        self.top_defects_label.pack(pady=10)
        
        # Bottom Defects Box (align to bottom camera vertical bounds)
        # Place at the same y as the bottom camera and match its height
        bot_defects_y = top_grade_y + top_grade_height + 10  # same y where bottom camera was placed
        # Extend defects box down through the camera and its grade box
        bot_defects_height = camera_height + 10 + bot_grade_height
        bot_defects_frame = ctk.CTkFrame(self, width=middle_width, height=bot_defects_height, corner_radius=6)
        bot_defects_frame.place(x=middle_x, y=bot_defects_y)
        bot_defects_frame.pack_propagate(False)
        
        ctk.CTkLabel(bot_defects_frame, text="Bot Defects", font=("Arial", 20, "bold")).pack(pady=(5, 3))
        
        bot_defects_scroll = ctk.CTkScrollableFrame(bot_defects_frame, width=middle_width - 20, 
                                                    height=bot_defects_height - 40, fg_color="transparent")
        bot_defects_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 5))
        
        self.bot_defects_label = ctk.CTkLabel(bot_defects_scroll, text="No defects detected",
                                             text_color=SECONDARY_TEXT_COLOR, font=("Arial", 20))
        self.bot_defects_label.pack(pady=10)
        
        # =====================
        # RIGHT SIDE - Last Graded Report (top to bottom defects edge)
        # =====================
        
        # Last Graded Report - start at top (y=10) and extend to bottom of bot defects
        bot_defects_bottom = bot_defects_y + bot_defects_height
        report_height = bot_defects_bottom - 10
        report_frame = ctk.CTkFrame(self, width=right_width, height=report_height, corner_radius=6)
        report_frame.place(x=right_x, y=10)
        report_frame.pack_propagate(False)
        
        ctk.CTkLabel(report_frame, text="Last Graded Report", font=("Arial", 20, "bold")).pack(pady=(5, 3))
        
        report_scrollable = ctk.CTkScrollableFrame(report_frame, width=right_width - 20, 
                                                   height=report_height - 40, fg_color="transparent")
        report_scrollable.pack(fill="both", expand=True, padx=8, pady=(0, 5))
        
        self.report_label = ctk.CTkLabel(report_scrollable, text="No report available",
                                        text_color=SECONDARY_TEXT_COLOR, font=("Arial", 20))
        self.report_label.pack(pady=10)
        
        # Live Grading Result - occupies all space below bot defects and last graded report
        # Width spans from left of Bot Defects (middle_x) to right of Last Graded Report (right_x + right_width)
        # Calculate where bot defects ends
        bot_defects_bottom = bot_defects_y + bot_defects_height + 10
        report_bottom = 10 + report_height + 10
        
        # Start after both end (use the larger of the two)
        grading_y = max(bot_defects_bottom, report_bottom)
        # Extend to bottom of window
        grading_height = screen_height - grading_y - 20
        
        # Width: from left of Bot Defects to right of Last Graded Report
        grading_x = middle_x
        grading_width = (right_x + right_width) - middle_x
        
        grading_frame = ctk.CTkFrame(self, width=grading_width, height=grading_height, corner_radius=6)
        grading_frame.place(x=grading_x, y=grading_y)
        grading_frame.pack_propagate(False)
        
        ctk.CTkLabel(grading_frame, text="Live Grading Result", font=("Arial", 20, "bold")).pack(pady=(5, 5))
        
        # Grade boxes container
        grades_container = ctk.CTkFrame(grading_frame, fg_color="transparent")
        grades_container.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        
        # Create 5 grade boxes
        grade_colors = {
            "G2-0": "#32CD32",  # Green - Good
            "G2-1": "#90EE90",  # Light green - Good
            "G2-2": "#FFB347",  # Orange - Fair
            "G2-3": "#FF8C00",  # Dark orange - Fair
            "G2-4": "#FF6B6B"   # Red - Poor
        }
        
        self.grade_buttons = {}
        for i, (grade_label, color) in enumerate(grade_colors.items()):
            grade_btn = ctk.CTkButton(
                grades_container, text=f"{grade_label}\n(0)", 
                fg_color=color, hover_color=color, state="normal",
                font=("Arial", 20, "bold"), corner_radius=4, text_color="#000000"
            )
            grade_btn.pack(side="left", fill="both", expand=True, padx=1)
            self.grade_buttons[grade_label] = grade_btn

    def update_status_text(self, text, color=None):
        """Update status text widget"""
        self.status_label.config(state=tk.NORMAL)
        self.status_label.delete(1.0, tk.END)
        self.status_label.insert(1.0, text)
        if color:
            self.status_label.config(foreground=color)
        self.status_label.config(state=tk.DISABLED)

    def set_mode(self, mode):
        """Set system mode (GUI only - no actual functionality)"""
        self.current_mode = mode
        self.update_status_text(f"Status: {mode}", STATUS_READY_COLOR)
        print(f"Mode set to: {mode}")

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode"""
        self.is_fullscreen = False
        self.attributes("-fullscreen", False)
        return "break"

    def on_closing(self):
        """Handle window closing"""
        print("Closing GUI design application...")
        self.destroy()


if __name__ == "__main__":
    app = GUIOnlyApp()
    app.mainloop()
