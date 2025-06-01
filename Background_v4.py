import pygame
import random
import math


class Background:
    def __init__(self, screen_width, screen_height, pixel_size,
                 bg_colours):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.pixel_size = pixel_size

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

    # def draw(self, surface): # Old signature
    def draw(self, surface, camera_world_y, world_unit_scale):
        camera_pixel_y_offset = camera_world_y * world_unit_scale

        start_world_row = math.floor(
            camera_pixel_y_offset / self.pixel_size)
        end_world_row_exclusive = math.ceil(
            (
                        camera_pixel_y_offset + self.screen_height) / self.pixel_size)

        num_world_cols_exclusive = math.ceil(
            self.screen_width / self.pixel_size)

        # It's good practice to fill the buffer once if there's transparency or gaps
        # or if not all pixels are redrawn each frame (though here they are).
        # self.grass_buffer.fill((some_debug_color_or_fully_transparent))

        for world_grid_y in range(start_world_row,
                                  end_world_row_exclusive):
            for world_grid_x in range(num_world_cols_exclusive):
                color = self.get_grass_color(world_grid_x,
                                             world_grid_y)

                # Calculate floating point positions first
                screen_px_x_float = world_grid_x * self.pixel_size
                screen_px_y_float = ((world_grid_y * self.pixel_size)
                                     - camera_pixel_y_offset)

                # Explicitly round to nearest int for drawing rects
                draw_x = round(
                    screen_px_x_float)  # world_grid_x * pixel_size is likely already int
                draw_y = round(screen_px_y_float)

                pygame.draw.rect(self.grass_buffer, color,
                                 (draw_x, draw_y,
                                  self.pixel_size, self.pixel_size))

        surface.blit(self.grass_buffer, (0, 0))
