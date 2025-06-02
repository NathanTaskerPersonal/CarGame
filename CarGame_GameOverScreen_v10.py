import pygame

COLOR_BLACK = pygame.Color("black")
COLOR_WHITE = pygame.Color("white")
COLOR_YELLOW = pygame.Color("gold")  # Brighter yellow for high score
# Festive color
COLOR_NEW_HIGH_SCORE_CELEBRATION = pygame.Color("springgreen")
COLOR_PROGRESS_BAR_BG = pygame.Color("gray20")
COLOR_PROGRESS_BAR_FG = pygame.Color("darkorange")
RESTART_HOLD_TARGET_TIME = 1.0


class GameOverScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.large_font = pygame.font.Font(None, 90)
        self.medium_font = pygame.font.Font(None, 48)
        self.score_font = pygame.font.Font(None, 42)
        # Larger for new high score text
        self.celebration_font = pygame.font.Font(None, 52)
        self.small_font = pygame.font.Font(None, 32)

        self.main_message_text = "GAME OVER"
        self.reason_message_text = "You lost!"
        self.prompt_message_text = (
            f"Hold SPACE for {RESTART_HOLD_TARGET_TIME:.0f}s "
            "to play again."
        )

        self.current_score = 0
        self.high_score = 0
        self.is_new_high_score = False

        self.space_held_duration = 0.0
        self.restart_game_triggered = False

    def _draw_text_line(self, surface, text, font, color,
                        center_x_pos, y_pos):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(centerx=center_x_pos,
                                          top=y_pos)
        surface.blit(text_surface, text_rect)

    def set_scores(self, current_score, high_score, is_new_high):
        self.current_score = current_score
        self.high_score = high_score
        self.is_new_high_score = is_new_high

    def set_messages(self, main_msg=None, reason_msg=None,
                     prompt_msg=None):
        if main_msg is not None:
            self.main_message_text = main_msg
        if reason_msg is not None:
            self.reason_message_text = reason_msg
        if prompt_msg is not None:
            self.prompt_message_text = prompt_msg
        else:
            self.prompt_message_text = (
                f"Hold SPACE for {RESTART_HOLD_TARGET_TIME:.0f}s "
                "to play again."
            )

    def reset(self):
        self.space_held_duration = 0.0
        self.restart_game_triggered = False
        # self.is_new_high_score = False
        # This should be set fresh each time set_scores is called

    def update(self, delta_time, keys_pressed):
        if self.restart_game_triggered:
            return
        if keys_pressed[pygame.K_SPACE]:
            self.space_held_duration += delta_time
        else:
            self.space_held_duration = 0.0
        if self.space_held_duration >= RESTART_HOLD_TARGET_TIME:
            self.restart_game_triggered = True

    def should_restart_game(self):
        return self.restart_game_triggered

    def draw(self, surface):
        surface.fill(COLOR_BLACK)
        center_x = self.screen_width // 2
        current_y = self.screen_height * 0.10  # Start a bit higher

        self._draw_text_line(
            surface, self.main_message_text,
            self.large_font, COLOR_WHITE, center_x, current_y
        )
        current_y += self.large_font.get_height() + 15

        self._draw_text_line(
            surface, self.reason_message_text,
            self.medium_font, COLOR_WHITE, center_x, current_y
        )
        current_y += self.medium_font.get_height() + 30

        # --- Enhanced Score Display ---
        if self.is_new_high_score:
            self._draw_text_line(
                surface, "🎉 NEW HIGH SCORE! 🎉",
                self.celebration_font,
                COLOR_NEW_HIGH_SCORE_CELEBRATION,
                center_x, current_y
            )
            current_y += self.celebration_font.get_height() + 15
            self._draw_text_line(
                surface, f"You scored: {self.current_score}",
                self.score_font, COLOR_YELLOW, center_x, current_y
            )
        else:
            self._draw_text_line(
                surface, f"Your Score: {self.current_score}",
                self.score_font, COLOR_WHITE, center_x, current_y
            )
        current_y += self.score_font.get_height() + 10

        self._draw_text_line(
            surface, f"Current High Score: {self.high_score}",
            self.score_font, COLOR_WHITE, center_x, current_y
        )
        current_y += self.score_font.get_height() + 40

        progress_bar_width = 300
        progress_bar_height = 25
        prompt_text_y = current_y
        progress_bar_y = (
            prompt_text_y + self.small_font.get_height() + 10
        )
        progress_bar_x = (
            self.screen_width - progress_bar_width
        ) // 2

        rect_pb_bg = (
            progress_bar_x, progress_bar_y,
            progress_bar_width, progress_bar_height
        )
        pygame.draw.rect(
            surface, COLOR_PROGRESS_BAR_BG, rect_pb_bg
        )

        progress_ratio = (
            self.space_held_duration / RESTART_HOLD_TARGET_TIME
        )
        current_progress_fill = (
            min(progress_ratio, 1.0) * progress_bar_width
        )
        rect_pb_fg = (
            progress_bar_x, progress_bar_y,
            current_progress_fill, progress_bar_height
        )
        pygame.draw.rect(
            surface, COLOR_PROGRESS_BAR_FG, rect_pb_fg
        )

        hold_text_display = self.prompt_message_text
        if self.space_held_duration >= RESTART_HOLD_TARGET_TIME:
            hold_text_display = "Restarting..."
        elif self.space_held_duration > 0:
            held_s = f"{self.space_held_duration:.1f}s"
            target_s = f"{RESTART_HOLD_TARGET_TIME:.1f}s"
            hold_text_display = (
                f"Hold SPACE ({held_s} / {target_s})"
            )
        self._draw_text_line(
            surface, hold_text_display,
            self.small_font, COLOR_WHITE, center_x, prompt_text_y
        )
