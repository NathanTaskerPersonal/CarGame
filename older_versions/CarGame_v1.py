import pygame
import random
import math


class Background:
    def __init__(self, screen_width, screen_height, pixel_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pixel_size = pixel_size
        self.camera_y = 0.0

        self.grass_colors = [
            pygame.Color("#3F692B"),
            pygame.Color("#578A3A"),
            pygame.Color("#72A74C"),
            pygame.Color("#4A7733"),
            pygame.Color("#649841")
        ]
        self.noise_seed = random.randint(0, 1000000000)
        self.prime1 = 73856093
        self.prime2 = 19349663

        self.grass_buffer = pygame.Surface(
            (self.screen_width, self.screen_height))
        self.grass_buffer = self.grass_buffer.convert()

    def get_grass_color(self, world_grid_x, world_grid_y):
        hash_val = (world_grid_x * self.prime1 ^
                    world_grid_y * self.prime2 ^
                    self.noise_seed)
        idx = abs(hash_val) % len(self.grass_colors)
        return self.grass_colors[idx]

    def update(self, dy):
        self.camera_y += dy

    def draw(self, surface):
        start_world_row = math.floor(self.camera_y / self.pixel_size)
        end_world_row_exclusive = math.ceil(
            (self.camera_y + self.screen_height) / self.pixel_size)

        num_world_cols_exclusive = math.ceil(
            self.screen_width / self.pixel_size)

        for world_grid_y in range(start_world_row,
                                  end_world_row_exclusive):
            for world_grid_x in range(num_world_cols_exclusive):
                color = self.get_grass_color(world_grid_x,
                                             world_grid_y)

                screen_px_x = world_grid_x * self.pixel_size
                screen_px_y = ((world_grid_y * self.pixel_size)
                               - self.camera_y)

                pygame.draw.rect(self.grass_buffer, color,
                                 (screen_px_x, screen_px_y,
                                  self.pixel_size, self.pixel_size))

        surface.blit(self.grass_buffer, (0, 0))


def run_game():
    pygame.init()
    pygame.font.init()

    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(
        "Car Game")

    clock = pygame.time.Clock()
    fps = 60

    grass_pixel_size = 10

    game_background = Background(screen_width, screen_height,
                                 grass_pixel_size)

    total_elapsed_time = 0.0
    camera_acceleration = 10

    fps_font_size = 30
    fps_font = pygame.font.SysFont(None, fps_font_size)
    fps_text_color = pygame.Color("white")
    fps_bg_color = pygame.Color("black")

    is_running = True
    while is_running:
        delta_time = clock.tick(fps) / 1000.0

        total_elapsed_time += delta_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        camera_speed = camera_acceleration * total_elapsed_time
        camera_y_change = -camera_speed * delta_time

        game_background.update(camera_y_change)

        screen.fill(pygame.Color("#1A2A15"))
        game_background.draw(screen)

        current_fps = clock.get_fps()
        fps_surface = fps_font.render(f"FPS: {current_fps:.2f}", True,
                                      fps_text_color, fps_bg_color)
        screen.blit(fps_surface, (10, 10))

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()


if __name__ == '__main__':
    run_game()
