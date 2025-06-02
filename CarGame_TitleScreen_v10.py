import pygame

COLOR_BLACK = pygame.Color("black")
COLOR_WHITE = pygame.Color("white")
COLOR_PROGRESS_BAR_BG = pygame.Color("gray20")
COLOR_PROGRESS_BAR_FG = pygame.Color("limegreen")
SPACE_HOLD_TARGET_TIME = 1.0


class TitleScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.title_font = pygame.font.Font(None, 80)
        self.header_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 32)
        self.small_text_font = pygame.font.Font(None, 28)
        # Font for high score
        self.score_font = pygame.font.Font(None, 40)

        self.space_held_duration = 0.0
        self.start_game_triggered = False
        self.high_score = 0  # To be set from outside

        self.controls_lines = [
            "W - Drive", "S - Reverse",
            "A - Steer Anticlockwise (while driving)",
            "D - Steer Clockwise (while driving)", "SHIFT - Brake"
        ]
        self.how_to_play_lines = [
            "Stay within screen and avoid all obstacles",
            "Pass other cars to score points.",
            "Try to get the high score!"
        ]

    def set_high_score(self, score):
        self.high_score = score

    def _draw_text_line(self, surface, text, font, color,
                        center_x_pos, y_pos, align_left_x=None):
        text_surface = font.render(text, True, color)
        if align_left_x is not None:
            text_rect = text_surface.get_rect(left=align_left_x,
                                              top=y_pos)
        else:
            text_rect = text_surface.get_rect(centerx=center_x_pos,
                                              top=y_pos)
        surface.blit(text_surface, text_rect)

    def reset(self):
        self.space_held_duration = 0.0
        self.start_game_triggered = False

    def update(self, delta_time, keys_pressed):
        if self.start_game_triggered:
            return
        if keys_pressed[pygame.K_SPACE]:
            self.space_held_duration += delta_time
        else:
            self.space_held_duration = 0.0
        if self.space_held_duration >= SPACE_HOLD_TARGET_TIME:
            self.start_game_triggered = True

    def should_start_game(self):
        return self.start_game_triggered

    def draw(self, surface):
        surface.fill(COLOR_BLACK)
        center_x = self.screen_width // 2

        # High Score Display (Top Right)
        high_score_text = f"High Score: {self.high_score}"
        hs_text_surface = self.score_font.render(
            high_score_text, True, COLOR_WHITE
        )
        hs_text_rect = hs_text_surface.get_rect(
            right=self.screen_width - 20, top=20
        )
        surface.blit(hs_text_surface, hs_text_rect)

        current_y = 70
        self._draw_text_line(
            surface, "Car Game", self.title_font,
            COLOR_WHITE, center_x, current_y
        )
        current_y += 100

        self._draw_text_line(
            surface, "Controls:", self.header_font,
            COLOR_WHITE, center_x, current_y
        )
        current_y += 50
        for line in self.controls_lines:
            self._draw_text_line(
                surface, line, self.text_font,
                COLOR_WHITE, center_x, current_y
            )
            current_y += 35

        current_y += 30
        self._draw_text_line(
            surface, "How to play:", self.header_font,
            COLOR_WHITE, center_x, current_y
        )
        current_y += 50
        for line in self.how_to_play_lines:
            self._draw_text_line(
                surface, line, self.small_text_font,
                COLOR_WHITE, center_x, current_y
            )
            current_y += 30
        current_y += 40

        progress_bar_width = 300
        progress_bar_height = 25
        progress_bar_x = (self.screen_width - progress_bar_width) // 2
        progress_bar_y = current_y + 20

        rect_pb_bg = (
            progress_bar_x, progress_bar_y,
            progress_bar_width, progress_bar_height
        )
        pygame.draw.rect(
            surface, COLOR_PROGRESS_BAR_BG, rect_pb_bg
        )

        progress_ratio = (
            self.space_held_duration / SPACE_HOLD_TARGET_TIME
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

        hold_message_y = progress_bar_y - 30
        held_s = f"{self.space_held_duration:.1f}s"
        target_s = f"{SPACE_HOLD_TARGET_TIME:.1f}s"
        hold_text = (
            f"Hold SPACE to begin ({held_s} / {target_s})"
        )
        if self.space_held_duration >= SPACE_HOLD_TARGET_TIME:
            hold_text = "Starting!"
        self._draw_text_line(
            surface, hold_text, self.text_font,
            COLOR_WHITE, center_x, hold_message_y
        )
