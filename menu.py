import pygame
import os
from constants import CELL_SIZE, EMPTY, WHITE_DAISY, BLACK_DAISY, WATER
# ----- Constants and Colors -----
DEFAULT_MAP_WIDTH = 1000
DEFAULT_MAP_HEIGHT = 400

# Colors for text and backgrounds
COLOR_TEXT = (0, 0, 0)
COLOR_BG = (200, 200, 200)

# Colors for input boxes (used in the settings screen)
COLOR_INPUT_BG = (255, 255, 255)
COLOR_INPUT_BORDER = (0, 0, 0)

# Colors for buttons
COLOR_BUTTON = (255, 165, 0)
COLOR_BUTTON_BORDER = (0, 0, 0)

# Colors for scrollbar (used in the settings screen)
COLOR_SCROLLBAR_BG = (180, 180, 180)
COLOR_SCROLLBAR_THUMB = (100, 100, 100)

FPS = 30

# ----- Main Menu Screen -----
def main_menu(screen, font, window_size, config):
    """
    Draws the Main Menu screen with four buttons arranged in a 2x2 grid:
    Settings, Run, Exit, and Scenario.
    
    Returns:
      "settings" if the user clicks Settings,
      "run" if the user clicks Run,
      "exit" if the user clicks Exit,
      "scenario" if the user clicks Scenario.
    """
    win_w, win_h = window_size
    clock = pygame.time.Clock()

    # Define relative sizes for buttons
    button_w = int(win_w * 0.3)
    button_h = int(win_h * 0.2)
    
    # Positions for 2x2 grid:
    settings_button_rect = pygame.Rect(int(win_w * 0.25) - button_w // 2,
                                       int(win_h * 0.3) - button_h // 2,
                                       button_w, button_h)
    run_button_rect = pygame.Rect(int(win_w * 0.75) - button_w // 2,
                                  int(win_h * 0.3) - button_h // 2,
                                  button_w, button_h)
    exit_button_rect = pygame.Rect(int(win_w * 0.25) - button_w // 2,
                                   int(win_h * 0.7) - button_h // 2,
                                   button_w, button_h)
    scenario_button_rect = pygame.Rect(int(win_w * 0.75) - button_w // 2,
                                       int(win_h * 0.7) - button_h // 2,
                                       button_w, button_h)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if settings_button_rect.collidepoint(event.pos):
                    return "settings"
                if run_button_rect.collidepoint(event.pos):
                    return "run"
                if exit_button_rect.collidepoint(event.pos):
                    return "exit"
                if scenario_button_rect.collidepoint(event.pos):
                    return "scenario"

        # Draw background
        screen.fill(COLOR_BG)

        # Draw Settings button
        pygame.draw.rect(screen, COLOR_BUTTON, settings_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, settings_button_rect, 2)
        settings_text = font.render("Settings", True, COLOR_TEXT)
        screen.blit(settings_text, settings_text.get_rect(center=settings_button_rect.center))
        
        # Draw Run button
        pygame.draw.rect(screen, COLOR_BUTTON, run_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, run_button_rect, 2)
        run_text = font.render("Run", True, COLOR_TEXT)
        screen.blit(run_text, run_text.get_rect(center=run_button_rect.center))
        
        # Draw Exit button
        pygame.draw.rect(screen, COLOR_BUTTON, exit_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, exit_button_rect, 2)
        exit_text = font.render("Exit", True, COLOR_TEXT)
        screen.blit(exit_text, exit_text.get_rect(center=exit_button_rect.center))
        
        # Draw Scenario button
        pygame.draw.rect(screen, COLOR_BUTTON, scenario_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, scenario_button_rect, 2)
        scenario_text = font.render("Scenario", True, COLOR_TEXT)
        screen.blit(scenario_text, scenario_text.get_rect(center=scenario_button_rect.center))
        
        pygame.display.flip()
        clock.tick(FPS)

# ----- Settings Screen -----
def settings_menu(screen, font, window_size, config):
    """
    Displays a settings screen with a scrollable list of configuration items.
    The first two items are "Map Width" and "Map Height", followed by simulation
    parameters (sourced from simulation.py defaults).
    Updates the config dictionary with the new values.
    """
    win_w, win_h = window_size
    clock = pygame.time.Clock()
    
    margin = 20
    scroll_area = pygame.Rect(margin, margin, win_w - 2 * margin - 40, win_h - 100)
    item_height = 40
    spacing = 10
    
    # Build settings items list.
    # First two items: Map Width and Map Height.
    settings_items = []
    settings_items.append({
        "label": "Map Width",
        "text": str(config.get("map_width", DEFAULT_MAP_WIDTH))
    })
    settings_items.append({
        "label": "Map Height",
        "text": str(config.get("map_height", DEFAULT_MAP_HEIGHT))
    })
    
    # Simulation parameters from simulation.py
    simulation_params = [
         ("temp_thickness", 3),
         ("T_space", 2.7),
         ("SUN_SCREENING", 1900),
         ("HEAT_DIFFUSION_COEFFICIENT", 0.2),
         ("HEATING_RATE", 0.2),
         ("INITIAL_TEMPERATURE", 500),
         ("ALBEDO_BLACK", 0.25),
         ("ALBEDO_WHITE", 0.75),
         ("ALBEDO_BARE", 0.5),
         ("ALBEDO_WATER", 0.9),
         ("HEAT_RETENTION", 0.1),
         ("T_OPTIMAL", 500),
         ("T_TOL_LOW", 50),
         ("T_TOL_HIGH", 70),
         ("SPREAD_CHANCE", 0.2),
         ("DEATH_CHANCE", 0.05),
         ("COOLING_COEFFICIENT", 9e-9),
         ("CUM_MOR_NET", 500),
         ("DAY_BORDER_SPEED", 30),
         ("DAY_PERIOD", 60.0),
         ("THRESHOLD", 1),
         ("THRESHOLD_TMID", 1),
         ("MAX_ITERS_TMID", 200),
         ("INFLUENCE_LEVEL", 2),
         ("overlay_shift_x", 200),
         ("overlay_shift_y", -10),
         ("overlay_shift_z", 50)
    ]
    for label, default in simulation_params:
         settings_items.append({
            "label": label,
            "text": str(config.get(label, default))
         })
    
    total_items = len(settings_items)
    total_content_height = total_items * (item_height + spacing)
    scroll_offset = 0
    max_scroll = max(0, total_content_height - scroll_area.height)
    
    active_setting = None

    back_button_rect = pygame.Rect((win_w - 100) // 2, win_h - 70, 100, 50)
    
    dragging = False
    scrollbar_rect = pygame.Rect(scroll_area.right + 5, scroll_area.top, 20, scroll_area.height)
    thumb_height = max(20, int(scroll_area.height * (scroll_area.height / total_content_height)))
    
    def get_thumb_rect():
        if max_scroll > 0:
            thumb_y = scroll_area.top + int((scroll_offset / max_scroll) * (scroll_area.height - thumb_height))
        else:
            thumb_y = scroll_area.top
        return pygame.Rect(scrollbar_rect.x, thumb_y, scrollbar_rect.width, thumb_height)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    scroll_offset = max(scroll_offset - 20, 0)
                elif event.button == 5:  # Scroll down
                    scroll_offset = min(scroll_offset + 20, max_scroll)
                elif event.button == 1:
                    mouse_x, mouse_y = event.pos
                    if scroll_area.collidepoint(mouse_x, mouse_y):
                        rel_y = mouse_y - scroll_area.y + scroll_offset
                        index = rel_y // (item_height + spacing)
                        if 0 <= index < total_items:
                            active_setting = index
                    thumb_rect = get_thumb_rect()
                    if thumb_rect.collidepoint(event.pos):
                        dragging = True
                        drag_offset = event.pos[1] - thumb_rect.y
                    if back_button_rect.collidepoint(event.pos):
                        try:
                            config["map_width"] = int(settings_items[0]["text"])
                        except ValueError:
                            config["map_width"] = DEFAULT_MAP_WIDTH
                        try:
                            config["map_height"] = int(settings_items[1]["text"])
                        except ValueError:
                            config["map_height"] = DEFAULT_MAP_HEIGHT
                        # Update simulation parameters
                        sim_params_labels = [label for label, _ in simulation_params]
                        for i, label in enumerate(sim_params_labels, start=2):
                            # Get the default value to determine type.
                            default_value = dict(simulation_params)[label]
                            try:
                                if isinstance(default_value, int):
                                    config[label] = int(settings_items[i]["text"])
                                else:
                                    config[label] = float(settings_items[i]["text"])
                            except ValueError:
                                config[label] = default_value
                        return "back"
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    new_thumb_y = event.pos[1] - drag_offset
                    new_thumb_y = max(scroll_area.top, min(new_thumb_y, scroll_area.bottom - thumb_height))
                    scroll_offset = int(((new_thumb_y - scroll_area.top) / (scroll_area.height - thumb_height)) * max_scroll)
            if event.type == pygame.KEYDOWN:
                if active_setting is not None:
                    current_text = settings_items[active_setting]["text"]
                    if event.key == pygame.K_RETURN:
                        active_setting = None
                    elif event.key == pygame.K_BACKSPACE:
                        settings_items[active_setting]["text"] = current_text[:-1]
                    else:
                        settings_items[active_setting]["text"] = current_text + event.unicode

        screen.fill(COLOR_BG)
        pygame.draw.rect(screen, COLOR_INPUT_BORDER, scroll_area, 2)
        
        content_surf = pygame.Surface((scroll_area.width, total_content_height))
        content_surf.fill(COLOR_BG)
        
        for i, item in enumerate(settings_items):
            item_y = i * (item_height + spacing)
            label_surf = font.render(item["label"] + ":", True, COLOR_TEXT)
            content_surf.blit(label_surf, (10, item_y + (item_height - label_surf.get_height()) // 2))
            box_rect = pygame.Rect(scroll_area.width // 2, item_y, scroll_area.width // 2 - 10, item_height)
            pygame.draw.rect(content_surf, COLOR_INPUT_BG, box_rect)
            border = COLOR_INPUT_BORDER if active_setting == i else (100, 100, 100)
            pygame.draw.rect(content_surf, border, box_rect, 2)
            txt = font.render(item["text"], True, COLOR_TEXT)
            content_surf.blit(txt, txt.get_rect(center=box_rect.center))
        
        clip_rect = scroll_area.copy()
        screen.set_clip(clip_rect)
        screen.blit(content_surf, (scroll_area.x, scroll_area.y - scroll_offset))
        screen.set_clip(None)
        
        pygame.draw.rect(screen, COLOR_SCROLLBAR_BG, scrollbar_rect)
        thumb_rect = get_thumb_rect()
        pygame.draw.rect(screen, COLOR_SCROLLBAR_THUMB, thumb_rect)
        
        pygame.draw.rect(screen, COLOR_BUTTON, back_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, back_button_rect, 2)
        back_text = font.render("Back", True, COLOR_TEXT)
        screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))
        
        pygame.display.flip()
        clock.tick(FPS)

# ----- Scenario Editor -----
def scenario_editor(screen, config):
    """
    Launches a 2D map editor using the config's map size.
    You can pan the map, and in the lower left corner you have a larger UI panel with:
      - Four round brush buttons for: Bare land (EMPTY), White daisies (WHITE_DAISY), 
        Black daisies (BLACK_DAISY), and Water (WATER).
      - A horizontal slider above the brush buttons to adjust the brush size.
    Left-click in the map paints cells with the selected brush.
    Right-click drag pans the map.
    A "Save" button saves the edited map into config["scenario_map"],
    and a "Back" button cancels editing.
    """

    map_width = config.get("map_width", DEFAULT_MAP_WIDTH)
    map_height = config.get("map_height", DEFAULT_MAP_HEIGHT)
    pygame.display.set_mode((map_width, map_height))
    pygame.display.set_caption("Scenario Editor")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    GRID_WIDTH = map_width // CELL_SIZE
    GRID_HEIGHT = map_height // CELL_SIZE

    grid = [[EMPTY for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    painted = False

    pan_x, pan_y = 0, 0
    dragging_pan = False
    last_pan_pos = None

    brush_types = [EMPTY, WHITE_DAISY, BLACK_DAISY, WATER]
    brush_labels = ["Bare", "White", "Black", "Water"]
    current_brush = 0
    brush_radius = 2

    panel_rect = pygame.Rect(10, map_height - 170, 300, 150)
    brush_button_centers = [
        (panel_rect.x + 40, panel_rect.y + 110),
        (panel_rect.x + 100, panel_rect.y + 110),
        (panel_rect.x + 160, panel_rect.y + 110),
        (panel_rect.x + 220, panel_rect.y + 110)
    ]
    brush_button_radius = 20

    slider_rect = pygame.Rect(panel_rect.x + 10, panel_rect.y + 50, 280, 10)
    thumb_width = 10
    def get_thumb_rect():
        t = (brush_radius - 1) / 9.0
        thumb_x = slider_rect.x + int(t * (slider_rect.width - thumb_width))
        return pygame.Rect(thumb_x, slider_rect.y - 5, thumb_width, slider_rect.height + 10)
    dragging_slider = False

    save_button_rect = pygame.Rect(panel_rect.x + 20, panel_rect.y + 10, 80, 30)
    back_button_rect = pygame.Rect(panel_rect.x + 200, panel_rect.y + 10, 80, 30)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                os._exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    if panel_rect.collidepoint(mx, my):
                        for i, center in enumerate(brush_button_centers):
                            cx, cy = center
                            if (mx - cx) ** 2 + (my - cy) ** 2 <= brush_button_radius ** 2:
                                current_brush = i
                        if get_thumb_rect().collidepoint(mx, my):
                            dragging_slider = True
                        if save_button_rect.collidepoint(mx, my):
                            config["scenario_map"] = grid
                            running = False
                        if back_button_rect.collidepoint(mx, my):
                            running = False
                    else:
                        grid_x = (mx - pan_x) // CELL_SIZE
                        grid_y = (my - pan_y) // CELL_SIZE
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            painted = True
                            for i in range(max(0, grid_y - brush_radius), min(GRID_HEIGHT, grid_y + brush_radius + 1)):
                                for j in range(max(0, grid_x - brush_radius), min(GRID_WIDTH, grid_x + brush_radius + 1)):
                                    if ((i - grid_y) ** 2 + (j - grid_x) ** 2) ** 0.5 <= brush_radius:
                                        grid[i][j] = brush_types[current_brush]
                elif event.button == 3:
                    dragging_pan = True
                    last_pan_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_slider = False
                if event.button == 3:
                    dragging_pan = False
                    last_pan_pos = None
            elif event.type == pygame.MOUSEMOTION:
                if dragging_pan and last_pan_pos:
                    dx = event.pos[0] - last_pan_pos[0]
                    dy = event.pos[1] - last_pan_pos[1]
                    pan_x += dx
                    pan_y += dy
                    last_pan_pos = event.pos
                if dragging_slider:
                    rel_x = event.pos[0] - slider_rect.x
                    t = max(0, min(rel_x / (slider_rect.width - thumb_width), 1))
                    brush_radius = int(round(t * 9)) + 1
            elif event.type == pygame.MOUSEWHEEL:
                brush_radius = max(1, min(brush_radius + event.y, 10))
        screen.fill((50, 50, 50))
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                cell = grid[i][j]
                if cell == EMPTY:
                    color = (139, 69, 19)
                elif cell == WHITE_DAISY:
                    color = (255, 255, 255)
                elif cell == BLACK_DAISY:
                    color = (0, 0, 0)
                elif cell == WATER:
                    color = (0, 0, 255)
                rect = pygame.Rect(pan_x + j * CELL_SIZE, pan_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (80, 80, 80), rect, 1)
        pygame.draw.rect(screen, (200, 200, 200), panel_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, panel_rect, 2)
        pygame.draw.rect(screen, COLOR_BUTTON, save_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, save_button_rect, 2)
        save_text = font.render("Save", True, COLOR_TEXT)
        screen.blit(save_text, save_text.get_rect(center=save_button_rect.center))
        pygame.draw.rect(screen, COLOR_BUTTON, back_button_rect)
        pygame.draw.rect(screen, COLOR_BUTTON_BORDER, back_button_rect, 2)
        back_text = font.render("Back", True, COLOR_TEXT)
        screen.blit(back_text, back_text.get_rect(center=back_button_rect.center))
        pygame.draw.rect(screen, (100, 100, 100), slider_rect)
        thumb_rect = get_thumb_rect()
        pygame.draw.rect(screen, (200, 200, 200), thumb_rect)
        slider_text = font.render(f"Brush Size: {brush_radius}", True, COLOR_TEXT)
        screen.blit(slider_text, (slider_rect.x, slider_rect.y + 20))
        for i, center in enumerate(brush_button_centers):
            cx, cy = center
            if i == current_brush:
                pygame.draw.circle(screen, (255, 0, 0), center, brush_button_radius)
            else:
                pygame.draw.circle(screen, (150, 150, 150), center, brush_button_radius)
            label = font.render(brush_labels[i], True, COLOR_TEXT)
            screen.blit(label, label.get_rect(center=(cx, cy + brush_button_radius + 15)))
        pygame.display.flip()
        clock.tick(60)
    return grid

# ----- Main Entry for Menu -----
def menu_screen_main():
    """
    Runs the menu system.
    First shows the Main Menu; if Settings is selected, shows the Settings screen;
    if Scenario is selected, launches the scenario editor.
    When Run is selected, returns a configuration dictionary.
    """
    pygame.init()
    window_size = (600, 400)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Daisyworld Menu")
    font = pygame.font.SysFont(None, 32)
    
    # Initialize config with default values, including simulation parameters.
    config = {
        "map_width": DEFAULT_MAP_WIDTH,
        "map_height": DEFAULT_MAP_HEIGHT,
        "temp_thickness": 3,
        "T_space": 2.7,
        "SUN_SCREENING": 1900,
        "HEAT_DIFFUSION_COEFFICIENT": 0.2,
        "HEATING_RATE": 0.2,
        "INITIAL_TEMPERATURE": 500,
        "ALBEDO_BLACK": 0.25,
        "ALBEDO_WHITE": 0.75,
        "ALBEDO_BARE": 0.5,
        "ALBEDO_WATER": 0.9,
        "HEAT_RETENTION": 0.1,
        "T_OPTIMAL": 500,
        "T_TOL_LOW": 50,
        "T_TOL_HIGH": 70,
        "SPREAD_CHANCE": 0.2,
        "DEATH_CHANCE": 0.05,
        "COOLING_COEFFICIENT": 9e-9,
        "CUM_MOR_NET": 500,
        "DAY_BORDER_SPEED": 30,
        "DAY_PERIOD": 60.0,
        "THRESHOLD": 1,
        "THRESHOLD_TMID": 1,
        "MAX_ITERS_TMID": 200,
        "INFLUENCE_LEVEL": 2,
        "overlay_shift_x": 200,
        "overlay_shift_y": -10,
        "overlay_shift_z": 50
    }
    
    state = "main"  # or "settings"
    while True:
        if state == "main":
            result = main_menu(screen, font, window_size, config)
            if result == "settings":
                state = "settings"
            elif result == "run":
                return config
            elif result == "exit":
                pygame.quit()
                os._exit(0)
            elif result == "scenario":
                scenario_editor(screen, config)
                screen = pygame.display.set_mode(window_size)
                state = "main"
        elif state == "settings":
            result = settings_menu(screen, font, window_size, config)
            if result == "back":
                state = "main"

if __name__ == '__main__':
    final_config = menu_screen_main()
    print("Final configuration:", final_config)