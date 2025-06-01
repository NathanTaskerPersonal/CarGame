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
