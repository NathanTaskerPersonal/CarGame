import pygame
from CarGame_Background_v5 import Background
from CarGame_PlayerCar_v5 import Car
from CarGame_TitleScreen_v5 import TitleScreen

# --- Game States ---
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"


# Removed color constants that are now in title_screen.py

def run_game():
    pygame.init()
    pygame.font.init()

    try:
        game_icon = pygame.image.load('assets/images/game_icon.png')
        pygame.display.set_icon(game_icon)
    except pygame.error as e:
        print(f"Warning: Error loading game icon: {e}")

    # --- Core Game Setup ---
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Car Game")
    clock = pygame.time.Clock()
    fps = 60

    # --- Game-wide Constants ---
    world_unit_scale = 100.0
    camera_acceleration = 10.0

    grass_pixel_size_const = 10
    grass_colours_const = [
        pygame.Color("#3F692B"), pygame.Color("#578A3A"),
        pygame.Color("#72A74C"), pygame.Color("#4A7733"),
        pygame.Color("#649841")
    ]

    # --- State Management & Screen Objects ---
    current_game_state = STATE_TITLE
    title_screen_handler = TitleScreen(screen_width, screen_height)

    # --- Gameplay Variables (initialized on game start) ---
    player_car = None
    game_background = None
    total_elapsed_time_playing = 0.0
    game_camera_world_y = 0.0

    is_running = True
    while is_running:
        delta_time = clock.tick(fps) / 1000.0
        if delta_time > (1.0 / 20.0):
            delta_time = (1.0 / 20.0)

        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # ------------------ STATE: TITLE SCREEN ------------------
        if current_game_state == STATE_TITLE:
            title_screen_handler.update(delta_time, keys_pressed)
            title_screen_handler.draw(screen)

            if title_screen_handler.should_start_game():
                current_game_state = STATE_PLAYING

                # Reset/Initialize game-specific variables for a fresh game
                total_elapsed_time_playing = 0.0
                game_camera_world_y = 0.0

                game_background = Background(screen_width,
                                             screen_height,
                                             grass_pixel_size_const,
                                             grass_colours_const)

                car_initial_world_x = (
                                                  screen_width / 2.0) / world_unit_scale
                car_initial_world_y = ((
                                                   screen_height * 0.75) / world_unit_scale) + game_camera_world_y
                player_car = Car(car_initial_world_x,
                                 car_initial_world_y)

                title_screen_handler.reset()  # Reset title screen state for potential re-entry

        # -------------------- STATE: PLAYING ---------------------
        elif current_game_state == STATE_PLAYING:
            if player_car is None or game_background is None:
                print(
                    "Error: Game objects not initialized for PLAYING state. Reverting to TITLE.")
                current_game_state = STATE_TITLE
                title_screen_handler.reset()  # Ensure title screen is reset
                continue

            player_car.update(delta_time, keys_pressed)

            camera_speed_pixels_sec = camera_acceleration * total_elapsed_time_playing
            camera_y_pixel_change = -camera_speed_pixels_sec * delta_time

            game_camera_world_y += camera_y_pixel_change / world_unit_scale

            total_elapsed_time_playing += delta_time

            # Define a fill color for playing state if needed, or rely on background
            playing_state_bg_color = pygame.Color(
                "black")  # Or some other default
            screen.fill(playing_state_bg_color)
            game_background.draw(screen, game_camera_world_y,
                                 world_unit_scale)
            player_car.draw(screen, game_camera_world_y,
                            world_unit_scale)

        pygame.display.flip()

    pygame.font.quit()
    pygame.quit()


if __name__ == '__main__':
    run_game()