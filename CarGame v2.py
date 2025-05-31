import pygame
import random
import math


class Background:
    def __init__(self, screen_width, screen_height, pixel_size,
                 bg_colours):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pixel_size = pixel_size
        self.camera_y = 0.0

        self.bg_colours = bg_colours
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
        idx = abs(hash_val) % len(self.bg_colours)
        return self.bg_colours[idx]

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
    game_icon = pygame.image.load('assets/images/game_icon.png')
    pygame.display.set_icon(game_icon)
    screen_width = 1280
    screen_height = 720
    world_unit_scale = 100
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(
        "Car Game")

    clock = pygame.time.Clock()
    fps = 60

    grass_pixel_size = 10
    grass_colours = [
        pygame.Color("#3F692B"),
        pygame.Color("#578A3A"),
        pygame.Color("#72A74C"),
        pygame.Color("#4A7733"),
        pygame.Color("#649841")
    ]
    game_background = Background(screen_width, screen_height,
                                 grass_pixel_size, grass_colours)

    def world_to_screen(world_x, world_y, game_cam_y_world_units,
                        screen_w, screen_h, unit_scale):
        screen_center_x = screen_w / 2
        screen_center_y = screen_h / 2

        point_pixel_x_from_origin = world_x * unit_scale
        point_pixel_y_from_origin = world_y * unit_scale

        camera_pixel_y_from_origin = (game_cam_y_world_units *
                                      unit_scale)

        point_relative_pixel_x = point_pixel_x_from_origin
        point_relative_pixel_y_wrt_camera = (
                point_pixel_y_from_origin -
                camera_pixel_y_from_origin)

        screen_x = screen_center_x + point_relative_pixel_x
        screen_y = screen_center_y - point_relative_pixel_y_wrt_camera

        return int(screen_x), int(screen_y)

    game_camera_world_y = 0.0
    total_elapsed_time = 0.0
    camera_acceleration = 5

    is_running = True
    while is_running:
        delta_time = clock.tick(fps) / 1000.0
        total_elapsed_time += delta_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        camera_speed = camera_acceleration * total_elapsed_time
        camera_y_change = -camera_speed * delta_time

        if world_unit_scale != 0:
            game_camera_world_y -= camera_y_change / world_unit_scale

        game_background.update(camera_y_change)
        game_background.draw(screen)

        world_points_to_draw = [
            (0, 0),
            (0, 10),
            (-5, 15),
            (5, 15)
        ]
        circle_radius = 5
        circle_color = pygame.Color("red")

        for wx, wy in world_points_to_draw:
            sx, sy = world_to_screen(wx, wy, game_camera_world_y,
                                     screen_width, screen_height,
                                     world_unit_scale)
            pygame.draw.circle(screen, circle_color, (sx, sy),
                               circle_radius)

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()


if __name__ == '__main__':
    run_game()
