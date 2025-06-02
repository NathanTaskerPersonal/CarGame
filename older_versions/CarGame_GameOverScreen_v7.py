import pygame

# --- Colors ---
COLOR_BLACK = pygame.Color("black")
COLOR_WHITE = pygame.Color("white")
COLOR_PROGRESS_BAR_BG = pygame.Color("gray20")
COLOR_PROGRESS_BAR_FG = pygame.Color(
    "darkorange")  # A distinct color for game over

RESTART_HOLD_TARGET_TIME = 1.0


class GameOverScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # --- Fonts ---
        self.large_font = pygame.font.Font(None,
                                           90)  # For "GAME OVER"
        self.medium_font = pygame.font.Font(None,
                                            48)  # For the reason
        self.small_font = pygame.font.Font(None, 32)  # For the prompt

        self.main_message_text = "GAME OVER"
        self.reason_message_text = "You lost!"  # Default
        self.prompt_message_text = f"Hold SPACE for {RESTART_HOLD_TARGET_TIME:.0f}s to play again."

        self.space_held_duration = 0.0
        self.restart_game_triggered = False

    def _draw_text_line(self, surface, text, font, color,
                        center_x_pos, y_pos):
        """Helper to draw a single line of text, horizontally centered."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(centerx=center_x_pos,
                                          top=y_pos)
        surface.blit(text_surface, text_rect)

    def set_messages(self, main_msg=None, reason_msg=None,
                     prompt_msg=None):
        """Sets the messages to be displayed on the game over screen."""
        if main_msg is not None:
            self.main_message_text = main_msg
        if reason_msg is not None:
            self.reason_message_text = reason_msg
        if prompt_msg is not None:
            self.prompt_message_text = prompt_msg
        else:  # Default prompt if not specified
            self.prompt_message_text = f"Hold SPACE for {RESTART_HOLD_TARGET_TIME:.0f}s to play again."

    def reset(self):
        """Resets the state of the game over screen for re-entry."""
        self.space_held_duration = 0.0
        self.restart_game_triggered = False
        # Optionally reset messages to default here if desired,
        # but typically they are set right before showing the screen.

    def update(self, delta_time, keys_pressed):
        """Handles input and updates the game over screen state."""
        if self.restart_game_triggered:
            return

        if keys_pressed[pygame.K_SPACE]:
            self.space_held_duration += delta_time
        else:
            self.space_held_duration = 0.0

        if self.space_held_duration >= RESTART_HOLD_TARGET_TIME:
            self.restart_game_triggered = True

    def should_restart_game(self):
        """Returns True if the conditions to restart the game have been met."""
        return self.restart_game_triggered

    def draw(self, surface):
        """Draws the game over screen."""
        surface.fill(COLOR_BLACK)

        center_x = self.screen_width // 2
        current_y = self.screen_height * 0.2  # Start a bit down from the top

        # Main "GAME OVER" message
        self._draw_text_line(surface, self.main_message_text,
                             self.large_font, COLOR_WHITE, center_x,
                             current_y)
        current_y += self.large_font.get_height() + 30

        # Reason message
        self._draw_text_line(surface, self.reason_message_text,
                             self.medium_font, COLOR_WHITE, center_x,
                             current_y)
        current_y += self.medium_font.get_height() + 80  # More space before prompt

        # Progress bar for restart
        progress_bar_width = 300
        progress_bar_height = 25
        progress_bar_x = (self.screen_width - progress_bar_width) // 2
        progress_bar_y = current_y + self.small_font.get_height() + 10  # Position below prompt text

        pygame.draw.rect(surface, COLOR_PROGRESS_BAR_BG,
                         (progress_bar_x, progress_bar_y,
                          progress_bar_width, progress_bar_height))

        current_progress_fill = min(
            self.space_held_duration / RESTART_HOLD_TARGET_TIME,
            1.0) * progress_bar_width
        pygame.draw.rect(surface, COLOR_PROGRESS_BAR_FG,
                         (progress_bar_x, progress_bar_y,
                          current_progress_fill, progress_bar_height))

        # Prompt message (above progress bar)
        hold_text_display = self.prompt_message_text
        if self.space_held_duration >= RESTART_HOLD_TARGET_TIME:
            hold_text_display = "Restarting..."  # Or keep the original prompt
        elif self.space_held_duration > 0:
            hold_text_display = f"Hold SPACE ({self.space_held_duration:.1f}s / {RESTART_HOLD_TARGET_TIME:.1f}s)"

        self._draw_text_line(surface, hold_text_display,
                             self.small_font, COLOR_WHITE, center_x,
                             current_y)