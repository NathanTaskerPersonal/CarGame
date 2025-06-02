import pygame
import math
import os  # For high score file path

from CarGame_Background_v10 import Background
from CarGame_PlayerCar_v10 import (
    Car as PlayerCar, CAR_SCALE_FACTOR,
    CAR_MAX_SPEED_FORWARD as PLAYER_CAR_MAX_SPEED_WORLD
)
from CarGame_TitleScreen_v10 import TitleScreen
from CarGame_GameOverScreen_v10 import GameOverScreen
# For stationary obstacles
from CarGame_ObstacleManager_v10 import ObstacleManager
from CarGame_BotManager_v10 import BotManager  # For bot cars

# --- Game States ---
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"

# --- Camera Speed Constants ---
CAMERA_SPEED_ASYMPTOTE_FACTOR = 0.95
CAMERA_SPEED_APPROACH_RATE = 0.05  # Tune for camera speed ramp-up

HIGH_SCORE_FILE = "highscore.txt"


def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except ValueError:
            return 0  # Invalid content
    return 0


def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            f.write(str(score))
    except IOError:
        print(
            f"Warning: Could not save high score to "
            f"{HIGH_SCORE_FILE}"
        )


def run_game():
    pygame.init()
    pygame.font.init()

    try:
        game_icon = pygame.image.load('assets/images/game_icon.png')
        pygame.display.set_icon(game_icon)
    except pygame.error as e:
        print(f"Warning: Error loading game icon: {e}")

    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Car Game")
    clock = pygame.time.Clock()
    fps = 60

    # Score and UI Font
    score_ui_font = pygame.font.Font(None, 36)
    COLOR_SCORE_TEXT = pygame.Color("white")

    world_unit_scale = 100.0

    # PLAYER_CAR_MAX_SPEED_WORLD is imported from PlayerCar module
    max_camera_speed_world_units = (
        PLAYER_CAR_MAX_SPEED_WORLD *
        CAMERA_SPEED_ASYMPTOTE_FACTOR
    )
    max_camera_speed_pixels_sec = (
        max_camera_speed_world_units * world_unit_scale
    )

    grass_pixel_size_const = 10
    grass_colours_const = [
        pygame.Color("#3F692B"), pygame.Color("#578A3A"),
        pygame.Color("#72A74C"),
        pygame.Color("#4A7733"), pygame.Color("#649841")
    ]

    high_score = load_high_score()

    current_game_state = STATE_TITLE
    title_screen_handler = TitleScreen(screen_width, screen_height)
    # Set initial high score for title
    title_screen_handler.set_high_score(high_score)

    game_over_screen_handler = GameOverScreen(
        screen_width, screen_height
    )
    stationary_obstacle_manager = ObstacleManager(
        screen_width, screen_height, world_unit_scale
    )
    bot_car_manager = BotManager(
        screen_width, screen_height,
        world_unit_scale,
        PLAYER_CAR_MAX_SPEED_WORLD,
        CAR_SCALE_FACTOR
    )

    # Gameplay variables
    player_car = None
    game_background = None
    total_elapsed_time_playing = 0.0
    game_camera_world_y = 0.0
    current_score = 0

    car_off_screen_timer = 0.0
    CAR_OFF_SCREEN_LIMIT_SECONDS = 3.0
    screen_bounds_rect = screen.get_rect()

    is_running = True
    while is_running:
        delta_time = clock.tick(fps) / 1000.0
        if delta_time > (1.0 / 20.0):
            delta_time = (1.0 / 20.0)

        keys_pressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        if current_game_state == STATE_TITLE:
            title_screen_handler.update(delta_time, keys_pressed)
            title_screen_handler.draw(screen)
            if title_screen_handler.should_start_game():
                current_game_state = STATE_PLAYING
                # Reset gameplay variables for a new game
                total_elapsed_time_playing = 0.0
                game_camera_world_y = 0.0
                car_off_screen_timer = 0.0
                current_score = 0  # Reset score

                game_background = Background(
                    screen_width, screen_height,
                    grass_pixel_size_const,
                    grass_colours_const
                )
                car_initial_world_x = (
                    (screen_width / 2.0) / world_unit_scale
                )
                car_y_screen_norm = screen_height * 0.75
                car_y_world_offset = (
                    car_y_screen_norm / world_unit_scale
                )
                car_initial_world_y = (
                    car_y_world_offset + game_camera_world_y
                )
                player_car = PlayerCar(
                    car_initial_world_x, car_initial_world_y
                )

                stationary_obstacle_manager.reset()
                bot_car_manager.reset()  # Reset bot cars
                title_screen_handler.reset()

        elif current_game_state == STATE_PLAYING:
            if player_car is None:
                current_game_state = STATE_TITLE
                continue

            player_car.update(delta_time, keys_pressed)
            player_car.update_screen_rects(
                game_camera_world_y, world_unit_scale
            )

            time_factor = (
                -CAMERA_SPEED_APPROACH_RATE *
                total_elapsed_time_playing
            )
            decay_factor = 1 - math.exp(time_factor)
            current_camera_speed_pixels_sec = (
                max_camera_speed_pixels_sec * decay_factor
            )
            camera_y_pixel_change_on_screen = (
                -current_camera_speed_pixels_sec * delta_time
            )
            game_camera_world_y += (
                camera_y_pixel_change_on_screen / world_unit_scale
            )
            total_elapsed_time_playing += delta_time

            stationary_obstacle_manager.update_spawning_and_culling(
                game_camera_world_y
            )
            score_from_bots = bot_car_manager.update_bots(
                delta_time, game_camera_world_y, player_car.world_y
            )
            current_score += score_from_bots

            game_over_reason = None
            if not player_car.collision_rect.colliderect(
                    screen_bounds_rect):
                car_off_screen_timer += delta_time
                if car_off_screen_timer >= CAR_OFF_SCREEN_LIMIT_SECONDS:
                    game_over_reason = "You strayed too far off course!"
            else:
                car_off_screen_timer = 0.0

            if not game_over_reason:
                collided_obstacle = (
                    stationary_obstacle_manager.check_collisions(
                        player_car, game_camera_world_y,
                        world_unit_scale
                    )
                )
                if collided_obstacle:
                    game_over_reason = "Crashed into an obstacle!"

            if not game_over_reason:  # Check bot car collision
                collided_bot = bot_car_manager.check_player_collision(
                    player_car, game_camera_world_y
                )
                if collided_bot:
                    game_over_reason = "Collided with another car!"

            if game_over_reason:
                current_game_state = STATE_GAME_OVER
                is_new_high = False
                if current_score > high_score:
                    high_score = current_score
                    save_high_score(high_score)
                    is_new_high = True
                game_over_screen_handler.set_scores(
                    current_score, high_score, is_new_high
                )
                game_over_screen_handler.set_messages(
                    reason_msg=game_over_reason
                )
                # Reset its internal state for display
                game_over_screen_handler.reset()

            # --- Drawing ---
            screen.fill(pygame.Color("black"))
            game_background.draw(
                screen, game_camera_world_y, world_unit_scale
            )
            stationary_obstacle_manager.draw_all(
                screen, game_camera_world_y, world_unit_scale
            )
            # Draw bot cars
            bot_car_manager.draw_all(screen, game_camera_world_y)
            player_car.draw(
                screen, game_camera_world_y, world_unit_scale
            )

            # Draw Score UI
            score_text_surface = score_ui_font.render(
                f"Score: {current_score}", True, COLOR_SCORE_TEXT
            )
            screen.blit(score_text_surface, (10, 10))

        elif current_game_state == STATE_GAME_OVER:
            game_over_screen_handler.update(delta_time, keys_pressed)
            game_over_screen_handler.draw(screen)
            if game_over_screen_handler.should_restart_game():
                current_game_state = STATE_TITLE
                # Update title screen with latest high score
                title_screen_handler.set_high_score(high_score)
                title_screen_handler.reset()
                game_over_screen_handler.reset()

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()


if __name__ == '__main__':
    run_game()
