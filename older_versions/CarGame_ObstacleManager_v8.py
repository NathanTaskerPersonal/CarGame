# CarGame_ObstacleManager_v8.py
import pygame
import random
from CarGame_Obstacle_v8 import Obstacle

OBSTACLE_COLOR = pygame.Color("gray50")
MIN_OBSTACLE_WIDTH_WORLD = 0.5
MAX_OBSTACLE_WIDTH_WORLD = 1.5
MIN_OBSTACLE_HEIGHT_WORLD = 0.5
MAX_OBSTACLE_HEIGHT_WORLD = 2.5
SPAWN_DISTANCE_AHEAD_FACTOR = 0.5
SPAWN_ZONE_DEPTH_FACTOR = 1.5
CULL_DISTANCE_BEHIND_FACTOR = 0.5
TARGET_OBSTACLES_PER_Y_WORLD_DISTANCE = 10.0


class ObstacleManager:
    def __init__(self, screen_width_pixels, screen_height_pixels, world_unit_scale):
        self.obstacles = []
        self.screen_width_pixels = screen_width_pixels
        self.screen_height_pixels = screen_height_pixels
        self.world_unit_scale = world_unit_scale
        self.screen_width_world = screen_width_pixels / world_unit_scale
        self.screen_height_world = screen_height_pixels / world_unit_scale
        self.last_camera_y_for_spawn_check = 0.0
        self.accumulated_camera_dy_world = 0.0

    def reset(self):
        self.obstacles = []
        self.last_camera_y_for_spawn_check = 0.0
        self.accumulated_camera_dy_world = 0.0

    def _spawn_obstacle(self, target_world_y):
        width_world = random.uniform(MIN_OBSTACLE_WIDTH_WORLD, MAX_OBSTACLE_WIDTH_WORLD)
        height_world = random.uniform(MIN_OBSTACLE_HEIGHT_WORLD, MAX_OBSTACLE_HEIGHT_WORLD)
        spawnable_track_width_world = self.screen_width_world * 0.90
        half_track_width_world = spawnable_track_width_world / 2.0
        center_screen_world_x = self.screen_width_world / 2.0
        world_x = random.uniform(
            center_screen_world_x - half_track_width_world,
            center_screen_world_x + half_track_width_world)
        new_obstacle = Obstacle(world_x, target_world_y, width_world, height_world, OBSTACLE_COLOR)
        self.obstacles.append(new_obstacle)

    def update_spawning_and_culling(self, camera_world_y):
        if self.last_camera_y_for_spawn_check == 0.0 and camera_world_y != 0.0:
            self.last_camera_y_for_spawn_check = camera_world_y
        elif self.last_camera_y_for_spawn_check == 0.0 and camera_world_y == 0.0:
            self.last_camera_y_for_spawn_check = 0.0001

        delta_camera_y_scrolled_up_world = self.last_camera_y_for_spawn_check - camera_world_y
        if delta_camera_y_scrolled_up_world > 0:
            self.accumulated_camera_dy_world += delta_camera_y_scrolled_up_world
        self.last_camera_y_for_spawn_check = camera_world_y

        if self.accumulated_camera_dy_world >= TARGET_OBSTACLES_PER_Y_WORLD_DISTANCE:
            num_to_spawn_events = int(self.accumulated_camera_dy_world / TARGET_OBSTACLES_PER_Y_WORLD_DISTANCE)
            for _ in range(num_to_spawn_events):
                spawn_y_offset_from_camera_top = self.screen_height_world * SPAWN_DISTANCE_AHEAD_FACTOR + \
                                                 random.uniform(0, self.screen_height_world * SPAWN_ZONE_DEPTH_FACTOR)
                actual_spawn_y_world = camera_world_y - spawn_y_offset_from_camera_top
                self._spawn_obstacle(actual_spawn_y_world)
            self.accumulated_camera_dy_world -= num_to_spawn_events * TARGET_OBSTACLES_PER_Y_WORLD_DISTANCE

        cull_line_world_y = camera_world_y + self.screen_height_world + \
                            (self.screen_height_world * CULL_DISTANCE_BEHIND_FACTOR)
        self.obstacles = [
            obs for obs in self.obstacles
            if (obs.world_y - obs.height_world / 2.0) < cull_line_world_y
        ]

    def check_collisions(self, player_car, camera_world_y, world_unit_scale):
        if not player_car:
            return False

        for obs in self.obstacles:
            obs.update_screen_rect(camera_world_y, world_unit_scale)
            # Use the car's specific collision_rect for the check
            if player_car.collision_rect.colliderect(obs.rect): # <--- MODIFIED HERE
                return True
        return False

    def draw_all(self, surface, camera_world_y, world_unit_scale):
        for obs in self.obstacles:
            obs.draw(surface, camera_world_y, world_unit_scale)