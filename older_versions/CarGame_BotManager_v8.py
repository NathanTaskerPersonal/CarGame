import pygame
import random
from CarGame_BotCar_v8 import BotCar

# Spawning constants for BotCars
BOT_SPAWN_DISTANCE_AHEAD_FACTOR = 0.6  # Slightly further ahead than stationary
BOT_SPAWN_ZONE_DEPTH_FACTOR = 1.8
BOT_CULL_DISTANCE_BEHIND_FACTOR = 0.6

# Target one bot car spawn event every X world units of camera scroll
TARGET_BOTS_PER_Y_WORLD_DISTANCE = 15.0  # Less frequent than stationary obstacles maybe


class BotManager:
    def __init__(self, screen_width_pixels, screen_height_pixels,
                 world_unit_scale,
                 player_max_speed_world, player_car_scale_factor):
        self.bot_cars = []
        self.screen_width_pixels = screen_width_pixels
        self.screen_height_pixels = screen_height_pixels
        self.world_unit_scale = world_unit_scale

        self.screen_width_world = screen_width_pixels / world_unit_scale
        self.screen_height_world = screen_height_pixels / world_unit_scale

        self.player_max_speed_world = player_max_speed_world
        self.player_car_scale_factor = player_car_scale_factor

        self.last_camera_y_for_spawn_check = 0.0
        self.accumulated_camera_dy_world = 0.0

    def reset(self):
        self.bot_cars = []
        self.last_camera_y_for_spawn_check = 0.0
        self.accumulated_camera_dy_world = 0.0

    def _spawn_bot_car(self, target_world_y):
        # Spawn bot cars across the width of the screen
        spawnable_track_width_world = self.screen_width_world * 0.95  # Wider spawn for moving cars
        half_track_width_world = spawnable_track_width_world / 2.0
        center_screen_world_x = self.screen_width_world / 2.0

        world_x = random.uniform(
            center_screen_world_x - half_track_width_world,
            center_screen_world_x + half_track_width_world)

        new_bot = BotCar(world_x, target_world_y,
                         self.world_unit_scale,
                         self.player_max_speed_world,
                         self.player_car_scale_factor)
        self.bot_cars.append(new_bot)

    def update_bots(self, delta_time, camera_world_y,
                    player_car_world_y_center):
        # Update individual bot car movement
        for bot in self.bot_cars:
            bot.update(delta_time)

        # --- Spawning --- (camera_world_y DECREASES as camera moves "up")
        if self.last_camera_y_for_spawn_check == 0.0 and camera_world_y != 0.0:
            self.last_camera_y_for_spawn_check = camera_world_y
        elif self.last_camera_y_for_spawn_check == 0.0 and camera_world_y == 0.0:
            self.last_camera_y_for_spawn_check = 0.0001

        delta_camera_y_scrolled_up_world = self.last_camera_y_for_spawn_check - camera_world_y
        if delta_camera_y_scrolled_up_world > 0:
            self.accumulated_camera_dy_world += delta_camera_y_scrolled_up_world
        self.last_camera_y_for_spawn_check = camera_world_y

        score_increment = 0
        if self.accumulated_camera_dy_world >= TARGET_BOTS_PER_Y_WORLD_DISTANCE:
            num_to_spawn_events = int(
                self.accumulated_camera_dy_world / TARGET_BOTS_PER_Y_WORLD_DISTANCE)
            for _ in range(num_to_spawn_events):
                spawn_y_offset = self.screen_height_world * BOT_SPAWN_DISTANCE_AHEAD_FACTOR + \
                                 random.uniform(0,
                                                self.screen_height_world * BOT_SPAWN_ZONE_DEPTH_FACTOR)
                actual_spawn_y = camera_world_y - spawn_y_offset  # Spawn "above" camera's top
                self._spawn_bot_car(actual_spawn_y)
            self.accumulated_camera_dy_world %= TARGET_BOTS_PER_Y_WORLD_DISTANCE

        # --- Culling & Scoring ---
        # Cull if bot car's visual top edge is too far "below" (larger Y) camera's view
        # A bot's top edge Y = bot.world_y - (bot.image.get_height() / 2) / world_unit_scale (approx)
        # Or simpler: cull based on bot.world_y (center)
        cull_line_world_y = camera_world_y + self.screen_height_world + \
                            (
                                        self.screen_height_world * BOT_CULL_DISTANCE_BEHIND_FACTOR)

        active_bots = []
        for bot in self.bot_cars:
            # Scoring: Player's Y is smaller (higher) than bot's Y
            if not bot.passed_by_player and player_car_world_y_center < bot.world_y:
                bot.passed_by_player = True
                score_increment += 1

            # Culling condition: keep if bot's center is still "above" the far-bottom cull line
            # OR if its visual top is above the cull line. For simplicity use center for now.
            # Visual top of bot: bot.world_y - (bot.image_original.get_height() / 2 / self.world_unit_scale)
            bot_visual_height_world = bot.image_original.get_height() / self.world_unit_scale
            if (
                    bot.world_y - bot_visual_height_world / 2.0) < cull_line_world_y:
                active_bots.append(bot)
        self.bot_cars = active_bots

        return score_increment

    def check_player_collision(self, player_car, camera_world_y):
        if not player_car: return False
        # player_car.collision_rect should be up-to-date from main loop

        for bot in self.bot_cars:
            bot.update_screen_rects(
                camera_world_y)  # Ensure bot's rects are current
            if player_car.collision_rect.colliderect(
                    bot.collision_rect):
                return True
        return False

    def draw_all(self, surface, camera_world_y):
        for bot in self.bot_cars:
            bot.draw(surface, camera_world_y)