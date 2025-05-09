import pygame
import random
import os
import math
from constants import CELL_SIZE, EMPTY, WHITE_DAISY, BLACK_DAISY, WATER

class DaisyworldSimulation:
    def __init__(self, config):
        self.config = config
        # Fixed constants (could also be class attributes if they never change)
        self.cell_size = CELL_SIZE  # Base cell size in pixels
        self.tile_width = self.cell_size  # For isometric rendering
        self.tile_height = self.cell_size // 2
        self.gods_brush_active = False
        self.brush_scroll = 0
        self.dragging_brush = False
        self.brush_drag_start_y = 0
        self.brush_start_offset = 0
        self.time_flow = int(config.get("time_flow", 100))
        # Simulation parameters from config with defaults
        self.temp_thickness = float(config.get("temp_thickness", 3))
        self.T_space = float(config.get("T_space", 2.7))
        self.SUN_SCREENING = float(config.get("SUN_SCREENING", 1900))
        self.HEAT_DIFFUSION_COEFFICIENT = float(config.get("HEAT_DIFFUSION_COEFFICIENT", 0.2))
        self.HEATING_RATE = float(config.get("HEATING_RATE", 0.2))
        self.INITIAL_TEMPERATURE = float(config.get("INITIAL_TEMPERATURE", 500))
        self.ALBEDO_BLACK = float(config.get("ALBEDO_BLACK", 0.25))
        self.ALBEDO_WHITE = float(config.get("ALBEDO_WHITE", 0.75))
        self.ALBEDO_BARE = float(config.get("ALBEDO_BARE", 0.5))
        self.ALBEDO_WATER = float(config.get("ALBEDO_WATER", 0.9))
        self.HEAT_RETENTION = float(config.get("HEAT_RETENTION", 0.1))
        self.T_OPTIMAL = float(config.get("T_OPTIMAL", 500))
        # single “average” tolerance for backward compatibility
        self.T_TOLERANCE = float(config.get("T_TOLERANCE", 50))
        # separate low/high tolerances
        self.T_TOL_LOW  = float(config.get("T_TOL_LOW", self.T_TOLERANCE))
        self.T_TOL_HIGH = float(config.get("T_TOL_HIGH", self.T_TOLERANCE))
        self.SPREAD_CHANCE = float(config.get("SPREAD_CHANCE", 0.2))
        self.DEATH_CHANCE = float(config.get("DEATH_CHANCE", 0.05))
        self.COOLING_COEFFICIENT = float(config.get("COOLING_COEFFICIENT", 9e-9))
        self.CUM_MOR_NET = float(config.get("CUM_MOR_NET", 500))
        self.DAY_BORDER_SPEED = float(config.get("DAY_BORDER_SPEED", 30))
        self.DAY_PERIOD = float(config.get("DAY_PERIOD", 60.0))
        self.THRESHOLD = float(config.get("THRESHOLD", 1))
        self.THRESHOLD_TMID = float(config.get("THRESHOLD_TMID", 1))
        self.MAX_ITERS_TMID = int(config.get("MAX_ITERS_TMID", 200))
        self.INFLUENCE_LEVEL = int(config.get("INFLUENCE_LEVEL", 1))
        self.MAX_HISTORY = 1000  # Fixed history length for graphs
        self.time_minus_rect = pygame.Rect(0,0,0,0)
        self.time_plus_rect  = pygame.Rect(0,0,0,0)
        # Daisy types
        self.EMPTY = EMPTY
        self.BLACK_DAISY = BLACK_DAISY
        self.WHITE_DAISY = WHITE_DAISY
        self.WATER = WATER
        self.sun_screening = float(config.get("sun_screening", self.SUN_SCREENING))

        # Colors for simulation
        self.COLOR_BARE = (139, 69, 19)
        self.COLOR_GRID = (50, 50, 50)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_WATER = (0, 0, 255)
        self.COLOR_PAUSE = (255, 165, 0)
        self.COLOR_BORDER = (0, 0, 0)
        self.COLOR_TEXT = (0, 0, 0)
        self.COLOR_OVERLAY = (0, 0, 0)

        # Map and display dimensions (also from config)
        self.map_width = int(config.get("map_width", 500))
        self.map_height = int(config.get("map_height", 500))
        self.ambient_temperature = float(config.get("ambient_temperature", self.INITIAL_TEMPERATURE))

        # Derived dimensions for grid and window
        self.GRID_WIDTH = self.map_width // self.cell_size
        self.GRID_HEIGHT = self.map_height // self.cell_size
        self.WINDOW_WIDTH = int(self.map_width * 1.25)
        self.WINDOW_HEIGHT = self.map_height

        # You might also initialize other instance variables here later,
        # for example, to hold the simulation grid, temperature grid, or history data.
        btn_w = int(self.WINDOW_WIDTH * 0.10)
        btn_h = int(self.WINDOW_HEIGHT * 0.08)
        btn_x = int(self.WINDOW_WIDTH * 0.02)
        btn_y = int(self.WINDOW_HEIGHT * 0.02)
        self.white_history = []
        self.black_history = []
        self.t_mean_history = []
        self.prev_white_count = None
        self.prev_black_count = None
        self.white_cumulative = []
        self.black_cumulative = []
        self.mortal_cumulative = []
        self.pause_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        # first, define all six slider rect placeholders
        self.slider_rects = {
            "time":    {"minus":None, "plus":None},
            "sun":     {"minus":None, "plus":None},
            "growth":  {"minus":None, "plus":None},
            "shift_x": {"minus":None, "plus":None},
            "shift_y": {"minus":None, "plus":None},
            "shift_z": {"minus":None, "plus":None},
        }
        # now create per‐slider hold state (None / "minus" / "plus")
        self.holding = { key: None for key in self.slider_rects }
        self.hold_repeat_interval = 150   # ms between repeats
        self.hold_last_time    = 0
        self.OVERLAY_SHIFT_X = float(config.get("overlay_shift_x", 200))
        self.OVERLAY_SHIFT_Y = float(config.get("overlay_shift_y", -10))
        self.gap_between_layers = float(config.get("overlay_shift_z", 50))
        self.peak_growth   = float(config.get("peak_growth", 100.0))
        self.slider_rects = {
            "time":    {"minus":None, "plus":None},
            "sun":     {"minus":None, "plus":None},
            "growth":  {"minus":None, "plus":None},
            "shift_x": {"minus":None, "plus":None},
            "shift_y": {"minus":None, "plus":None},
            "shift_z": {"minus":None, "plus":None},
        }
        # build 100 log‐spaced steps from 1 → 1000

        num_steps = 100
        log_min, log_max = math.log10(1.0), math.log10(1000.0)
        step = (log_max - log_min) / (num_steps - 1)
        self._time_flow_steps = [
            int(round(10 ** (log_min + i * step)))
            for i in range(num_steps)
        ]
        # find nearest start index
        self._time_flow_index = min(
            range(num_steps),
            key=lambda i: abs(self._time_flow_steps[i] - self.time_flow)
        )
        # snap to exact log‐value
        self.time_flow = self._time_flow_steps[self._time_flow_index]
        
    def draw_stat_panel(self, screen, panel_rect, grid, temp_grid, mid_temp, scroll_offset=0):
        """
        Draws a stats panel in the given panel_rect, including a pie chart of cell types,
        T_mid/T_mean, net changes for daisies, and line graphs.
        """
        PAPER_BG = (245, 245, 220)
        pygame.draw.rect(screen, PAPER_BG, panel_rect)
    
        # --- Count cell types (ignore WATER cells) ---
        bare_count = white_count = black_count = 0
        for row in grid:
            for cell in row:
                if cell == self.EMPTY:
                    bare_count += 1
                elif cell == self.WHITE_DAISY:
                    white_count += 1
                elif cell == self.BLACK_DAISY:
                    black_count += 1
        
        total_count = bare_count + white_count + black_count
        if getattr(self, "paused", False):
            # still draw the pie‐chart and text below, but skip all the net‐calc & appends
            # jump straight to the text‐and‐graph drawing code
            goto_draw_only = True
        else:
            goto_draw_only = False
        # --- Draw pie chart ---
        pie_size = min(panel_rect.width, panel_rect.height // 4)
        pie_center = (panel_rect.x + panel_rect.width // 2,
                      panel_rect.y + pie_size // 2 + scroll_offset)
        radius = pie_size // 2
    
        def draw_pie_wedge(surface, center, radius, start_angle, end_angle, color):
            points = [center]
            steps = 30
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * i / steps
                x = center[0] + radius * math.cos(angle)
                y = center[1] + radius * math.sin(angle)
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
    
        start_angle = 0
        if total_count > 0:
            slices = [
                (bare_count, self.COLOR_BARE),
                (white_count, self.COLOR_WHITE),
                (black_count, self.COLOR_BLACK)
            ]
            for count, color in slices:
                fraction = count / total_count
                end_angle = start_angle + fraction * 2 * math.pi
                draw_pie_wedge(screen, pie_center, radius, start_angle, end_angle, color)
                start_angle = end_angle
    
        # --- Net Born/Mortality Calculation ---
        if self.prev_white_count is None:
            self.prev_white_count = white_count
        if self.prev_black_count is None:
            self.prev_black_count = black_count
    
        # Step-wise net changes
        white_net = white_count - self.prev_white_count
        black_net = black_count - self.prev_black_count
        mortal_net = (self.prev_white_count + self.prev_black_count) - (white_count + black_count)
    
        self.white_cumulative.append(white_net)
        self.black_cumulative.append(black_net)
        self.mortal_cumulative.append(mortal_net)
    
        # Keep only last CUM_MOR_NET items
        if len(self.white_cumulative) > self.CUM_MOR_NET:
            self.white_cumulative.pop(0)
        if len(self.black_cumulative) > self.CUM_MOR_NET:
            self.black_cumulative.pop(0)
        if len(self.mortal_cumulative) > self.CUM_MOR_NET:
            self.mortal_cumulative.pop(0)
    
        # Sums
        white_cum_net = sum(self.white_cumulative)
        black_cum_net = sum(self.black_cumulative)
        mortal_cum_net = sum(self.mortal_cumulative)
    
        self.prev_white_count = white_count
        self.prev_black_count = black_count
    
        # --- Append current net values and compute T_mean ---
        total_temp = 0
        cell_count = 0
        for row in temp_grid:
            for t in row:
                total_temp += t
                cell_count += 1
        t_mean = total_temp / cell_count if cell_count else 0

        # --- Only update histories when running ---
        if not self.paused:
            self.white_history.append(white_cum_net)
            self.black_history.append(black_cum_net)
            self.t_mean_history.append(t_mean)
            # trim to max length
            if len(self.white_history) > self.MAX_HISTORY:
                self.white_history.pop(0)
            if len(self.black_history) > self.MAX_HISTORY:
                self.black_history.pop(0)
            if len(self.t_mean_history) > self.MAX_HISTORY:
                self.t_mean_history.pop(0)
    
        # Gather all temps
        all_temps = [temp for row in temp_grid for temp in row]
        all_temps.sort()
        if len(all_temps) >= 100:
            Tl = sum(all_temps[:100]) / 100.0
            Th = sum(all_temps[-100:]) / 100.0
        else:
            Tl = min(all_temps)
            Th = max(all_temps)
    
        # Limit history arrays to self.MAX_HISTORY
        if len(self.white_history) > self.MAX_HISTORY:
            self.white_history.pop(0)
        if len(self.black_history) > self.MAX_HISTORY:
            self.black_history.pop(0)
        if len(self.t_mean_history) > self.MAX_HISTORY:
            self.t_mean_history.pop(0)
    
        # --- Draw text stats ---
        text_y = panel_rect.y + pie_size + 10 + scroll_offset
        font = pygame.font.SysFont(None, 20)
        t_mid_text = font.render(f"T_equilibrium: {mid_temp:.2f}", True, self.COLOR_TEXT)
        screen.blit(t_mid_text, (panel_rect.x + 10, text_y))
        text_y += 25
        t_mean_text = font.render(f"T_mean: {t_mean:.2f}", True, self.COLOR_TEXT)
        screen.blit(t_mean_text, (panel_rect.x + 10, text_y))
        text_y += 25
        mortal_text = font.render(f"Mortality Net: {mortal_cum_net}", True, self.COLOR_TEXT)
        screen.blit(mortal_text, (panel_rect.x + 10, text_y))
        text_y += 30
        Tl_text = font.render(f"Tl (100 coldest mean): {Tl:.2f}", True, self.COLOR_TEXT)
        screen.blit(Tl_text, (panel_rect.x + 10, text_y))
        text_y += 25
        Th_text = font.render(f"Th (100 hottest mean): {Th:.2f}", True, self.COLOR_TEXT)
        screen.blit(Th_text, (panel_rect.x + 10, text_y))
        text_y += 25
    
        # --- Graph width & drawing code ---
        graph_width = panel_rect.width - 20
        graph_height = 50
    
        # --- White daisies line graph ---
        graph_rect = pygame.Rect(panel_rect.x + 10, text_y, graph_width, graph_height)
        pygame.draw.rect(screen, (200, 200, 200), graph_rect, 1)
        if len(self.white_history) > 1:
            max_val = max(self.white_history + [0])
            min_val = min(self.white_history + [0])
            rng_val = max_val - min_val if max_val != min_val else 1
            points = []
            for i, val in enumerate(self.white_history):
                x = graph_rect.x + i * graph_rect.width / self.MAX_HISTORY
                y = graph_rect.y + graph_rect.height - ((val - min_val) / rng_val) * graph_rect.height
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, (255, 0, 0), False, points, 2)
    
            # Horizontal line at net=0
            if min_val <= 0 <= max_val:
                zero_y = graph_rect.y + graph_rect.height - ((0 - min_val) / rng_val) * graph_rect.height
                pygame.draw.line(screen, (255,165,0), (graph_rect.x, zero_y),
                                 (graph_rect.x + graph_rect.width, zero_y), 1)
        text_y += graph_height + 10
    
        # --- Black daisies line graph ---
        graph_rect = pygame.Rect(panel_rect.x + 10, text_y, graph_width, graph_height)
        pygame.draw.rect(screen, (200, 200, 200), graph_rect, 1)
        if len(self.black_history) > 1:
            max_val = max(self.black_history + [0])
            min_val = min(self.black_history + [0])
            rng_val = max_val - min_val if max_val != min_val else 1
            points = []
            for i, val in enumerate(self.black_history):
                x = graph_rect.x + i * graph_rect.width / self.MAX_HISTORY
                y = graph_rect.y + graph_rect.height - ((val - min_val) / rng_val) * graph_rect.height
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, (0, 0, 0), False, points, 2)
    
            # Horizontal line at net=0
            if min_val <= 0 <= max_val:
                zero_y = graph_rect.y + graph_rect.height - ((0 - min_val) / rng_val) * graph_rect.height
                pygame.draw.line(screen, (255,165,0), (graph_rect.x, zero_y),
                                 (graph_rect.x + graph_rect.width, zero_y), 1)
        text_y += graph_height + 10
    
        # --- T_mean graph with T_mid line ---
        graph_rect = pygame.Rect(panel_rect.x + 10, text_y, graph_width, graph_height)
        pygame.draw.rect(screen, (200, 200, 200), graph_rect, 1)
        if len(self.t_mean_history) > 1:
            max_val = max(self.t_mean_history + [mid_temp])
            min_val = min(self.t_mean_history + [mid_temp])
            rng_val = max_val - min_val if max_val != min_val else 1
            points = []
            for i, val in enumerate(self.t_mean_history):
                x = graph_rect.x + i * graph_rect.width / self.MAX_HISTORY
                y = graph_rect.y + graph_rect.height - ((val - min_val) / rng_val) * graph_rect.height
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(screen, (0,255,0), False, points, 2)
    
            # Horizontal line for T_mid
            if min_val <= mid_temp <= max_val:
                t_mid_y = graph_rect.y + graph_rect.height - ((mid_temp - min_val)/rng_val)*graph_rect.height
                pygame.draw.line(screen, (255,0,0), (graph_rect.x, t_mid_y),
                                 (graph_rect.x + graph_rect.width, t_mid_y), 1)
        # text_y += graph_height + 10
    def init_grid(self):
        if self.config.get("scenario_map") is not None:
            return self.config["scenario_map"]

        grid = [[self.EMPTY for _ in range(self.GRID_WIDTH)]
                for _ in range(self.GRID_HEIGHT)]
        half = 50
        for _ in range(half):
            x = random.randint(0, self.GRID_WIDTH - 1)
            y = random.randint(0, self.GRID_HEIGHT - 1)
            grid[y][x] = self.BLACK_DAISY
        for _ in range(half):
            x = random.randint(0, self.GRID_WIDTH - 1)
            y = random.randint(0, self.GRID_HEIGHT - 1)
            grid[y][x] = self.WHITE_DAISY
        return grid

    def grid_to_iso(self, x, y, origin_x, origin_y):
        screen_x = origin_x + (x - y) * (self.cell_size // 2)
        screen_y = origin_y + (x + y) * (self.cell_size // 4)
        return screen_x, screen_y

    def draw_iso_tile(self, surface, color, x, y, origin_x, origin_y):
        cx, cy = self.grid_to_iso(x, y, origin_x, origin_y)
        top    = (cx, cy - self.cell_size // 4)
        right  = (cx + self.cell_size // 2, cy)
        bottom = (cx, cy + self.cell_size // 4)
        left   = (cx - self.cell_size // 2, cy)
        pygame.draw.polygon(surface, color, [top, right, bottom, left])

    def draw_grid_iso(self, surface, grid, origin_x, origin_y):
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                cell = grid[y][x]
                if cell == self.EMPTY:
                    color = self.COLOR_BARE
                elif cell == self.BLACK_DAISY:
                    color = self.COLOR_BLACK
                elif cell == self.WHITE_DAISY:
                    color = self.COLOR_WHITE
                elif cell == self.WATER:
                    color = self.COLOR_WATER
                self.draw_iso_tile(surface, color, x, y, origin_x, origin_y)

    def update_grid(self, grid, temp_grid, dt):
        new = [row[:] for row in grid]
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                cell = grid[y][x]
                if cell == self.WATER:
                    new[y][x] = self.WATER
                    continue
                if cell in (self.BLACK_DAISY, self.WHITE_DAISY):
                    if random.random() < self.DEATH_CHANCE * self.time_flow / 100:
                        new[y][x] = self.EMPTY
                elif cell == self.EMPTY:
                    neighbors, temp_sum = [], 0
                    for dy in range(-self.INFLUENCE_LEVEL, self.INFLUENCE_LEVEL + 1):
                        for dx in range(-self.INFLUENCE_LEVEL, self.INFLUENCE_LEVEL + 1):
                            if dx == 0 and dy == 0:
                                continue
                            # level 1 = 4‑way, level 2 = 8‑way, >2 = circular
                            if self.INFLUENCE_LEVEL == 1 and abs(dx) + abs(dy) != 1:
                                continue
                            if self.INFLUENCE_LEVEL > 2 and (dx*dx + dy*dy) ** 0.5 > self.INFLUENCE_LEVEL:
                                continue
                    
                            nx = (x + dx) % self.GRID_WIDTH
                            ny = y + dy
                            if 0 <= ny < self.GRID_HEIGHT:
                                ncell = grid[ny][nx]
                                if ncell in (self.BLACK_DAISY, self.WHITE_DAISY):
                                    neighbors.append(ncell)
                                    temp_sum += temp_grid[ny][nx]
                    if neighbors:
                        local_temp = temp_sum/len(neighbors)
                        # choose low‐ or high‐side tolerance
                        tol = (self.T_TOL_LOW
                               if local_temp < self.T_OPTIMAL
                               else self.T_TOL_HIGH)
                        rate = max(0, 1 - ((local_temp - self.T_OPTIMAL) / tol)**2)
                        if random.random() < self.SPREAD_CHANCE * (self.peak_growth/100.0) * rate * self.time_flow / 100.0:
                            new[y][x] = random.choice(neighbors)
        return new
    def update_temperature(self, temp_grid, grid, dt, mid_temp):
        new_temp = [row[:] for row in temp_grid]
        heating = [[0]*self.GRID_WIDTH for _ in range(self.GRID_HEIGHT)]

        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if grid[y][x] == self.WATER:
                    heating[y][x] = mid_temp
                    continue

                cell = grid[y][x]
                if cell == self.BLACK_DAISY:
                    albedo = self.ALBEDO_BLACK
                elif cell == self.WHITE_DAISY:
                    albedo = self.ALBEDO_WHITE
                else:
                    albedo = self.ALBEDO_BARE

                day_start = self.day_phase_offset
                day_end = (day_start + self.GRID_WIDTH/2) % self.GRID_WIDTH

                if day_start < day_end:
                    is_day = day_start <= x < day_end
                else:
                    is_day = x >= day_start or x < day_end

                if is_day:
                    offset = x - day_start if x >= day_start else x + (self.GRID_WIDTH - day_start)
                    norm = offset/(self.GRID_WIDTH/2)
                    if norm < 0.25:
                        intensity = norm
                    elif norm > 0.75:
                        intensity = 1 - norm
                    else:
                        intensity = 1
                else:
                    intensity = 0

                heating[y][x] = temp_grid[y][x] + self.HEATING_RATE * (
                    self.sun_screening * intensity * (1 - albedo) - temp_grid[y][x]
                )

        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if grid[y][x] == self.WATER:
                    new_temp[y][x] = mid_temp
                    continue

                total, count = 0, 0
                for dy in range(-self.INFLUENCE_LEVEL, self.INFLUENCE_LEVEL + 1):
                    for dx in range(-self.INFLUENCE_LEVEL, self.INFLUENCE_LEVEL + 1):
                        if self.INFLUENCE_LEVEL == 1 and abs(dx) + abs(dy) != 1:
                            continue
                        if self.INFLUENCE_LEVEL > 2 and (dx*dx + dy*dy)**0.5 > self.INFLUENCE_LEVEL:
                            continue
                
                        nx = (x + dx) % self.GRID_WIDTH
                        ny = y + dy
                        if 0 <= ny < self.GRID_HEIGHT:
                            total += heating[ny][nx]
                            count += 1

                avg_heated = total/count if count else heating[y][x]
                loss = self.COOLING_COEFFICIENT * (temp_grid[y][x]**4 - self.T_space**4)
                new_temp[y][x] = temp_grid[y][x] + dt * (
                    self.HEATING_RATE * (avg_heated - loss)
                )

        return new_temp
    def compute_equilibrium_temp(self, dt=0.1):
        temp = [[self.ambient_temperature] * self.GRID_WIDTH
                for _ in range(self.GRID_HEIGHT)]
        day_phase = 0.0

        for _ in range(self.MAX_ITERS_TMID):
            new = [[0.0] * self.GRID_WIDTH for _ in range(self.GRID_HEIGHT)]
            heating = [[0.0] * self.GRID_WIDTH for _ in range(self.GRID_HEIGHT)]

            # First pass: day‑night heating
            for y in range(self.GRID_HEIGHT):
                for x in range(self.GRID_WIDTH):
                    albedo = self.ALBEDO_BARE
                    day_start = day_phase
                    day_end = (day_phase + self.GRID_WIDTH/2) % self.GRID_WIDTH

                    if (day_start < day_end and day_start <= x < day_end) or \
                       (day_start >= day_end and (x >= day_start or x < day_end)):
                        offset = x - day_start if x >= day_start else x + (self.GRID_WIDTH - day_start)
                        norm = offset/(self.GRID_WIDTH/2)
                        intensity = norm if norm < 0.25 else (1 - norm if norm > 0.75 else 1)
                    else:
                        intensity = 0

                    heating[y][x] = temp[y][x] + self.HEATING_RATE * (
                        self.sun_screening * intensity * (1 - albedo) - temp[y][x]
                    )

            # Second pass: diffusion + radiative cooling
            for y in range(self.GRID_HEIGHT):
                for x in range(self.GRID_WIDTH):
                    total, count = 0, 0
                    for dy in (-1,0,1):
                        for dx in (-1,0,1):
                            ny, nx = y+dy, x+dx
                            if 0 <= ny < self.GRID_HEIGHT and 0 <= nx < self.GRID_WIDTH:
                                total += heating[ny][nx]
                                count += 1
                    avg_heated = total/count if count else heating[y][x]
                    loss = self.COOLING_COEFFICIENT * (temp[y][x]**4 - self.T_space**4)
                    new[y][x] = temp[y][x] + dt * (self.HEATING_RATE * (avg_heated - loss))

            day_phase = (day_phase - self.DAY_BORDER_SPEED * dt) % self.GRID_WIDTH

            max_diff = max(abs(new[r][c] - temp[r][c])
                           for r in range(self.GRID_HEIGHT)
                           for c in range(self.GRID_WIDTH))
            temp = new
            if max_diff < self.THRESHOLD_TMID:
                break

        # Return average equilibrium temperature
        return sum(sum(row) for row in temp) / (self.GRID_WIDTH * self.GRID_HEIGHT)
    def draw_pause_button(self, surface, font):
        pygame.draw.rect(surface, self.COLOR_PAUSE, self.pause_btn_rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, self.pause_btn_rect, 2)
        text_surf = font.render("Pause", True, self.COLOR_TEXT)
        surface.blit(text_surf, text_surf.get_rect(center=self.pause_btn_rect.center))
        return self.pause_btn_rect
    
    def draw_pause_menu(self, surface, font):
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*self.COLOR_OVERLAY, 180))
        surface.blit(overlay, (0, 0))

        btn_w = int(self.WINDOW_WIDTH * 0.25)
        btn_h = int(self.WINDOW_HEIGHT * 0.1)
        resume_rect = pygame.Rect(
            (self.WINDOW_WIDTH - btn_w) // 2,
            int(self.WINDOW_HEIGHT * 0.4) - btn_h // 2,
            btn_w, btn_h
        )
        quit_rect = pygame.Rect(
            (self.WINDOW_WIDTH - btn_w) // 2,
            int(self.WINDOW_HEIGHT * 0.6) - btn_h // 2,
            btn_w, btn_h
        )
        # God's Brush button
        brush_rect = pygame.Rect(
            (self.WINDOW_WIDTH - btn_w) // 2,
            int(self.WINDOW_HEIGHT * 0.8) - btn_h // 2,  # position below Quit
            btn_w, btn_h
        )
        pygame.draw.rect(surface, self.COLOR_PAUSE, quit_rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, quit_rect, 2)
        quit_txt = font.render("Quit", True, self.COLOR_TEXT)
        surface.blit(quit_txt, quit_txt.get_rect(center=quit_rect.center))
        pygame.draw.rect(surface, self.COLOR_PAUSE, resume_rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, resume_rect, 2)
        resume_txt = font.render("Resume", True, self.COLOR_TEXT)
        surface.blit(resume_txt, resume_txt.get_rect(center=resume_rect.center))
        pygame.draw.rect(surface, self.COLOR_PAUSE, brush_rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, brush_rect, 2)
        brush_txt = font.render("God’s Brush", True, self.COLOR_TEXT)
        surface.blit(brush_txt, brush_txt.get_rect(center=brush_rect.center))
        
        return resume_rect, quit_rect, brush_rect

    def draw_gods_brush_menu(self, surface, font):
        # overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*self.COLOR_OVERLAY, 180))
        surface.blit(overlay, (0, 0))
        # centered full‐height white panel

        panel_x = 50
        panel_w = self.WINDOW_WIDTH - 100
        bg_rect = pygame.Rect(panel_x, 0, panel_w, self.WINDOW_HEIGHT)
        pygame.draw.rect(surface, (255, 255, 255), bg_rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, bg_rect, 2)
    
        # Title
        title = font.render("God’s Brush Settings", True, self.COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(self.WINDOW_WIDTH//2,
                                               50 + self.brush_scroll)))
    
        # Placeholder controls
        params = [
            ("Time Flow", 100, 200 + self.brush_scroll),
            ("Sun Screening", 100, 250 + self.brush_scroll),
            ("Peak Growth (%)",       100, 300 + self.brush_scroll),
            ("Overlay Shift X",            100, 350 + self.brush_scroll),
            ("Overlay Shift Y",            100, 400 + self.brush_scroll),
            ("Overlay Shift Z",            100, 450 + self.brush_scroll),
        ]
        for label, x, y in params:
            txt = font.render(label, True, self.COLOR_TEXT)
            surface.blit(txt, (x, y))
            # slider placeholder
            bar = pygame.Rect(x+250, y+5, 200, 20)
            pygame.draw.rect(surface, (200,200,200), bar, 1)
            # +/- buttons
            minus = pygame.Rect(bar.right+10, y, 20, 20)
            plus  = pygame.Rect(bar.right+35, y, 20, 20)
            pygame.draw.rect(surface, self.COLOR_BORDER, minus, 1)
            pygame.draw.rect(surface, self.COLOR_BORDER, plus, 1)
            surface.blit(font.render("-", True, self.COLOR_TEXT),
                         font.render("-", True, self.COLOR_TEXT).get_rect(center=minus.center))
            surface.blit(font.render("+", True, self.COLOR_TEXT),
                         font.render("+", True, self.COLOR_TEXT).get_rect(center=plus.center))
            key = None
            if label == "Time Flow":       key = "time"
            elif label == "Sun Screening": key = "sun"
            elif label == "Peak Growth (%)": key = "growth"
            elif label == "Overlay Shift X": key = "shift_x"
            elif label == "Overlay Shift Y": key = "shift_y"
            elif label == "Overlay Shift Z": key = "shift_z"
            if key:
                # register for click‐handling
                self.slider_rects[key]["minus"] = minus
                self.slider_rects[key]["plus"]  = plus
                # slider fill based on index
                # decide fill fraction & current value text
                if key == "time":
                    frac = self._time_flow_index / (len(self._time_flow_steps)-1)
                    current = self.time_flow
                elif key == "sun":
                    # map log10(100→20000) → [0,1]
                    min_sun, max_sun = 100.0, 100000.0
                    frac = (math.log10(self.sun_screening) - math.log10(min_sun)) \
                        / (math.log10(max_sun) - math.log10(min_sun))
                    current = int(self.sun_screening)
                elif key == "growth":
                    frac = self.peak_growth/100.0
                    current = int(self.peak_growth)
                elif key == "shift_x":
                    # assume ±200px range
                    frac = (self.OVERLAY_SHIFT_X+400)/800
                    current = int(self.OVERLAY_SHIFT_X)
                elif key == "shift_y":
                    frac = (self.OVERLAY_SHIFT_Y+400)/800
                    current = int(self.OVERLAY_SHIFT_Y)
                else:  # shift_z
                    # assume gap_between_layers range 0→100
                    frac = self.gap_between_layers/100.0
                    current = int(self.gap_between_layers)

                fill_w = int(bar.width * max(0, min(1, frac)))
                fill_rect = pygame.Rect(bar.x, bar.y, fill_w, bar.height)
                pygame.draw.rect(surface, (180, 180, 180), fill_rect)
                # draw the current exact value
                val_surf = font.render(str(current), True, self.COLOR_TEXT)
                surface.blit(val_surf, val_surf.get_rect(center=bar.center))

        # “Back” button to return to pause menu
        btn_w, btn_h = 120, 40
        panel_x = 50
        panel_w = self.WINDOW_WIDTH - 100
        back_rect = pygame.Rect(
            panel_x + (panel_w - btn_w)//2,    # center in panel
            self.WINDOW_HEIGHT - btn_h - 20,   # 20px margin from bottom
            btn_w, btn_h
        )
        pygame.draw.rect(surface, self.COLOR_PAUSE, back_rect)
        pygame.draw.rect(surface, self.COLOR_BORDER, back_rect, 2)
        back_txt = font.render("Back", True, self.COLOR_TEXT)
        surface.blit(back_txt, back_txt.get_rect(center=back_rect.center))

        return back_rect

    def quit_game(self):
        pygame.quit()
        os._exit(0)
    def _temp_color(self, t, mean, tmin, tmax):
        if t <= mean:
            delta = max(mean - tmin, self.THRESHOLD)
            v = ((t - tmin) / delta)**0.3
            return (int(255*v), int(255*v), 255, 128)
        else:
            delta = max(tmax - mean, self.THRESHOLD)
            v = (t - mean) / delta
            return (255, int(255*(1-v)), int(255*(1-v)), 128)
    def render(self, screen, grid, temp_grid, origin_x, origin_y, scroll_offset, mid_temp):
        screen.fill((0, 0, 0))

        # Draw world
        # Draw world
        self.draw_grid_iso(screen, grid, origin_x, origin_y)

        # → now draw overlay *behind* the stats panel...
        if not self.paused:
            # Temperature overlay
            temps = [temp for row in temp_grid for temp in row]
            current_min, current_max = min(temps), max(temps)
            t_mean = sum(temps) / len(temps)

            overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
            for y in range(self.GRID_HEIGHT):
                for x in range(self.GRID_WIDTH):
                    t = temp_grid[y][x]
                    cx, cy = self.grid_to_iso(x, y, origin_x, origin_y)
                    cy -= (int(self.tile_height / math.tan(math.radians(30))) * 3
                           + self.gap_between_layers)
                    cx += self.OVERLAY_SHIFT_X
                    cy += self.OVERLAY_SHIFT_Y
                    h = int(self.tile_height * self.temp_thickness)
                    color = self._temp_color(t, t_mean, current_min, current_max)
                    points = [
                        (cx, cy - h//2),
                        (cx + self.tile_width//2, cy),
                        (cx, cy + h//2),
                        (cx - self.tile_width//2, cy),
                    ]
                    pygame.draw.polygon(overlay, color, points)

            screen.blit(overlay, (0, 0))

            # Draw dawn/dusk borders
            dawn = self.day_phase_offset
            dusk = (self.day_phase_offset + self.GRID_WIDTH/2) % self.GRID_WIDTH
            dawn_pts = [
                self.grid_to_iso(dawn, row, origin_x, origin_y)
                for row in range(self.GRID_HEIGHT)
            ]
            dusk_pts = [
                self.grid_to_iso(dusk, row, origin_x, origin_y)
                for row in range(self.GRID_HEIGHT)
            ]
            pygame.draw.lines(screen, (255,165,0), False, dawn_pts, 2)
            pygame.draw.lines(screen, (0,255,255), False, dusk_pts, 2)

        # Draw stats panel *after* the overlay so it’s always on top
        stats_w = int(self.WINDOW_WIDTH * 0.20)
        stats_x = self.WINDOW_WIDTH - stats_w
        stats_rect = pygame.Rect(stats_x, 0, stats_w, self.WINDOW_HEIGHT)
        self.draw_stat_panel(screen, stats_rect, grid, temp_grid, mid_temp, scroll_offset)

        # Draw pause UI
        if self.paused:
            if self.gods_brush_active:
                self.draw_gods_brush_menu(screen, self.font)
            else:
                self.draw_pause_menu(screen, self.font)
        else:
            self.draw_pause_button(screen, self.font)

        pygame.display.flip()
    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("2.5D Daisyworld Model")
        clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        grid = self.init_grid()
        mid_temp = self.compute_equilibrium_temp()
        temp_grid = [
                    [mid_temp if grid[y][x] == self.WATER else self.ambient_temperature
                     for x in range(self.GRID_WIDTH)]
                    for y in range(self.GRID_HEIGHT)
                ]
        

        self.paused = False
        origin_x, origin_y = self.WINDOW_WIDTH // 2, 50
        scroll_offset = 0
        self.day_phase_offset = 0.0
        last_mouse = None
        self.dragging_panel = False
        self.dragging_world = False
        self.start_offset = 0
        self.panel_drag_start_y = 0

        while True:
            # —— hold‑and‑repeat logic ——
            now = pygame.time.get_ticks()

            def do_step(key, direction):
                if key == "time":
                    delta = -1 if direction=="minus" else +1
                    self._time_flow_index = min(max(0, self._time_flow_index+delta),
                                                len(self._time_flow_steps)-1)
                    self.time_flow = self._time_flow_steps[self._time_flow_index]
                elif key == "sun":
                    factor = 0.9 if direction=="minus" else 1.1
                    self.sun_screening = max(100, min(100000, self.sun_screening *factor))
                elif key == "growth":
                    step = -1 if direction=="minus" else +1
                    self.peak_growth = max(0, min(100, self.peak_growth + step))
                elif key == "shift_x":
                    self.OVERLAY_SHIFT_X += -10 if direction=="minus" else +10
                elif key == "shift_y":
                    self.OVERLAY_SHIFT_Y += -10 if direction=="minus" else +10
                else:  # shift_z
                    self.gap_between_layers = max(0, min(200,
                        self.gap_between_layers + (-5 if direction=="minus" else +5)
                    ))
        
            # now repeat for **every** slider you’re holding
            for key, direction in self.holding.items():
                if direction and now - self.hold_last_time >= self.hold_repeat_interval:
                    do_step(key, direction)
                    self.hold_last_time = now
            # keep the loop at a steady 60 FPS, then speed up/slower by time_flow (%)
            FPS_CAP = 60
            raw_dt = clock.tick(FPS_CAP) / 1000.0       # real seconds per frame at 60 FPS
            dt = raw_dt * (self.time_flow / 100.0)      # scale by your brush setting (e.g. 100→1×speed)
            if not self.paused:
                self.day_phase_offset = (self.day_phase_offset - self.DAY_BORDER_SPEED * dt) % self.GRID_WIDTH

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.paused and self.pause_btn_rect.collidepoint(event.pos):
                        self.paused = True
        
                    # clicks inside pause‐screen
                    elif self.paused:
                        if self.gods_brush_active:
                            # start dragging the God’s Brush panel if you click inside its white box
                            drag_rect = pygame.Rect(50, 0, self.WINDOW_WIDTH - 100, self.WINDOW_HEIGHT)
                            if drag_rect.collidepoint(event.pos):
                                self.dragging_brush = True
                                self.brush_drag_start_y = event.pos[1]
                                self.brush_start_offset = self.brush_scroll
                            # redraw the menu (so time_minus/plus rects get updated)
                            back_btn = self.draw_gods_brush_menu(screen, self.font)
                        
                            # ---- HANDLE THE TIME‑FLOW BUTTONS ----
                            now = pygame.time.get_ticks()
                            for key, rects in self.slider_rects.items():
                                # skip if we haven’t yet laid out that slider
                                if rects["minus"] and rects["minus"].collidepoint(event.pos):
                                    self.holding[key]   = "minus"
                                    self.hold_last_time = now
                                    do_step(key, "minus")
                                elif rects["plus"] and rects["plus"].collidepoint(event.pos):
                                    self.holding[key]   = "plus"
                                    self.hold_last_time = now
                                    do_step(key, "plus")
                        
                            # ---- BACK BUTTON ----
                            if back_btn.collidepoint(event.pos):
                                self.gods_brush_active = False
                        else:
                            # three buttons: Resume, Quit, God’s Brush
                            resume_btn, quit_btn, brush_btn = self.draw_pause_menu(screen, self.font)
                            if resume_btn.collidepoint(event.pos):
                                self.paused = False
                            elif quit_btn.collidepoint(event.pos):
                                self.quit_game()
                            elif brush_btn.collidepoint(event.pos):
                                self.gods_brush_active = True
                    else:
                        stats_x = int(self.WINDOW_WIDTH * 0.80)
                        if event.pos[0] >= stats_x:
                            self.dragging_panel = True
                            self.panel_drag_start_y = event.pos[1]
                            self.start_offset = scroll_offset
                        else:
                            self.dragging_world = True
                            last_mouse = event.pos
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging_panel   = False
                    self.dragging_world   = False
                    self.dragging_brush   = False
                    last_mouse            = None
                    # stop any hold‑and‑repeat
                    for key in self.holding:
                        self.holding[key] = None
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_brush:
                        dy = event.pos[1] - self.brush_drag_start_y
                        self.brush_scroll = self.brush_start_offset + dy
                    elif self.dragging_panel:
                        scroll_offset = self.start_offset + (event.pos[1] - self.panel_drag_start_y)
                    elif self.dragging_world and last_mouse:
                        dx = event.pos[0] - last_mouse[0]
                        dy = event.pos[1] - last_mouse[1]
                        origin_x += dx
                        origin_y += dy
                        last_mouse = event.pos

            if not self.paused:
                temp_grid = self.update_temperature(temp_grid, grid, dt, mid_temp)
                grid = self.update_grid(grid, temp_grid, dt)

            self.render(screen, grid, temp_grid, origin_x, origin_y, scroll_offset, mid_temp)