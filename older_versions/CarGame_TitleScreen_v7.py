import pygame

# --- Colors (can be shared or defined specifically for title screen) ---
COLOR_BLACK = pygame.Color("black")
COLOR_WHITE = pygame.Color("white")
COLOR_PROGRESS_BAR_BG = pygame.Color("gray20")
COLOR_PROGRESS_BAR_FG = pygame.Color("limegreen")

SPACE_HOLD_TARGET_TIME = 1.0


class TitleScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- Fonts ---
        self.title_font = pygame.font.Font(None, 80)
        self.header_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.small_text_font = pygame.font.Font(None, 28)

        self.space_held_duration = 0.0
        self.start_game_triggered = False  # Flag to signal game start

        self.controls_lines = [
            "W - Drive",
            "S - Reverse",
            "A - Steer Anticlockwise (while driving)",
            "D - Steer Clockwise (while driving)",
            "SHIFT - Brake"
        ]
        self.how_to_play_lines = [
            "Stay within screen and avoid all obstacles",
            "for as long as possible."
        ]

    def _draw_text_line(self, surface, text, font, color,
                        center_x_pos, y_pos):
        """Helper to draw a single line of text, horizontally centered."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(centerx=center_x_pos,
                                          top=y_pos)
        surface.blit(text_surface, text_rect)

    def reset(self):
        """Resets the state of the title screen for re-entry."""
        self.space_held_duration = 0.0
        self.start_game_triggered = False

    def update(self, delta_time, keys_pressed):
        """Handles input and updates the title screen state."""
        if self.start_game_triggered:  # Already triggered, do nothing more here
            return

        if keys_pressed[pygame.K_SPACE]:
            self.space_held_duration += delta_time
        else:
            self.space_held_duration = 0.0  # Reset if space is released

        if self.space_held_duration >= SPACE_HOLD_TARGET_TIME:
            self.start_game_triggered = True

    def should_start_game(self):
        """Returns True if the conditions to start the game have been met."""
        return self.start_game_triggered

    def draw(self, surface):
        """Draws the title screen."""
        surface.fill(COLOR_BLACK)

        current_y = 70
        self._draw_text_line(surface, "Car Game", self.title_font,
                             COLOR_WHITE, self.screen_width // 2,
                             current_y)
        current_y += 100

        self._draw_text_line(surface, "Controls:", self.header_font,
                             COLOR_WHITE, self.screen_width // 2,
                             current_y)
        current_y += 50
        for line in self.controls_lines:
            self._draw_text_line(surface, line, self.text_font,
                                 COLOR_WHITE, self.screen_width // 2,
                                 current_y)
            current_y += 35

        current_y += 30  # Extra space
        self._draw_text_line(surface, "How to play:",
                             self.header_font, COLOR_WHITE,
                             self.screen_width // 2, current_y)
        current_y += 50
        for line in self.how_to_play_lines:
            self._draw_text_line(surface, line, self.small_text_font,
                                 COLOR_WHITE, self.screen_width // 2,
                                 current_y)
            current_y += 30
        current_y += 40  # More space before hold message

        # Progress bar display
        progress_bar_width = 300
        progress_bar_height = 25
        progress_bar_x = (self.screen_width - progress_bar_width) // 2
        progress_bar_y = current_y + 20

        pygame.draw.rect(surface, COLOR_PROGRESS_BAR_BG,
                         (progress_bar_x, progress_bar_y,
                          progress_bar_width, progress_bar_height))

        current_progress_fill = min(
            self.space_held_duration / SPACE_HOLD_TARGET_TIME,
            1.0) * progress_bar_width
        pygame.draw.rect(surface, COLOR_PROGRESS_BAR_FG,
                         (progress_bar_x, progress_bar_y,
                          current_progress_fill, progress_bar_height))

        # Hold message text
        hold_message_y = progress_bar_y - 30
        hold_text = f"Hold SPACE to begin ({self.space_held_duration:.1f}s / {SPACE_HOLD_TARGET_TIME:.1f}s)"
        if self.space_held_duration >= SPACE_HOLD_TARGET_TIME:
            hold_text = "Starting!"
        self._draw_text_line(surface, hold_text, self.text_font,
                             COLOR_WHITE, self.screen_width // 2,
                             hold_message_y)