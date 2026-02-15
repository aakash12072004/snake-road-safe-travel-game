import pygame
import math
import random
import sys

# Initialize
pygame.init()
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Road: Safe Traffic + Return Home")

# Colors
GREEN = (34, 139, 34)
GRAY = (80, 80, 80)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)  # Boy
RED = (255, 0, 0)  # Car
CYAN = (0, 255, 255)  # Bike
PINK = (255, 192, 203)  # Auto
YELLOW = (255, 255, 0)
PURPLE = (160, 32, 240)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)

# Game states
boy_progress = 0
game_mode = "MENU"
stop_choice = None
journey_complete = False
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)
big_font = pygame.font.SysFont("Arial", 30, bold=True)

# Traffic
traffic = []
spawn_timer = 0


# Snake road
def get_road_y(x):
    wave = 50 * math.sin(x * 0.01) + 20 * math.sin(x * 0.03)
    return 250 + wave


def get_road_edges(x):
    base_y = get_road_y(x)
    return base_y - 60, base_y + 60


locations = [[250, "MARKET", YELLOW, 60], [550, "MALL", PURPLE, 60], [850, "FRIEND HOUSE", BROWN, 80]]
trees = [100, 350, 650, 950]
visited_stops = []


class Vehicle:
    def __init__(self, progress, vtype):
        self.progress = progress
        self.vtype = vtype
        self.speed = random.uniform(1.5, 3.0)
        self.color = [RED, CYAN, PINK][vtype]
        self.width = [35, 25, 30][vtype]
        self.height = [20, 15, 18][vtype]
        self.direction = random.choice([-1, 1])

    def update(self):
        self.progress += self.speed * self.direction
        return 0 < self.progress < WIDTH

    def get_rect(self):
        x, y = self.progress, get_road_y(self.progress) - 25
        return pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)

    def draw(self, screen):
        x, y = self.progress, get_road_y(self.progress) - 25
        pygame.draw.rect(screen, self.color, (x - self.width // 2, y - self.height // 2, self.width, self.height))


def spawn_traffic():
    global spawn_timer
    spawn_timer += 1
    if spawn_timer > 90:  # Less frequent spawn
        if random.random() < 0.6:
            traffic.append(Vehicle(50, random.randint(0, 2)))
        if random.random() < 0.4:
            traffic.append(Vehicle(WIDTH - 50, random.randint(0, 2)))
        spawn_timer = 0


def check_collision():
    """Check boy collision with traffic"""
    boy_rect = pygame.Rect(boy_progress - 15, get_road_y(boy_progress) - 30, 30, 40)
    for vehicle in traffic:
        if boy_rect.colliderect(vehicle.get_rect()):
            return True
    return False


def draw_snake_road():
    for x in range(0, WIDTH, 5):
        top_y, bottom_y = get_road_edges(x)
        pygame.draw.line(screen, GRAY, (x, top_y), (x + 5, get_road_edges(x + 5)[0]), 10)
        pygame.draw.line(screen, GRAY, (x, bottom_y), (x + 5, get_road_edges(x + 5)[1]), 10)
    for x in range(0, WIDTH, 25):
        pygame.draw.line(screen, ORANGE, (x, get_road_y(x)), (x + 20, get_road_y(x + 20)), 4)


def draw_world():
    screen.fill(GREEN)
    draw_snake_road()

    # Home & School
    hx, sx = 20, WIDTH - 80
    pygame.draw.rect(screen, (100, 100, 100), (hx, get_road_y(hx) - 30, 60, 80))
    pygame.draw.rect(screen, WHITE, (sx, get_road_y(sx) - 30, 60, 80))
    screen.blit(font.render("HOME", True, WHITE), (25, get_road_y(hx) - 55))
    screen.blit(font.render("SCHOOL", True, BLACK), (sx + 5, get_road_y(sx) - 55))

    # Trees & Locations (same as before)
    for tx in trees:
        tree_y = get_road_y(tx) - 100
        pygame.draw.rect(screen, BROWN, (tx - 5, tree_y + 20, 10, 30))
        pygame.draw.circle(screen, DARK_GREEN, (tx, tree_y), 25)

    for loc in locations:
        lx, name, color, lwidth = loc
        loc_y = get_road_y(lx) - 80
        pygame.draw.rect(screen, color, (lx, loc_y, lwidth, 60))
        screen.blit(font.render(name[:6], True, WHITE), (lx + 5, loc_y - 25))


def draw_ui():
    if game_mode == "MENU":
        overlay = pygame.Surface((500, 200), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (350, 100))
        screen.blit(font.render("WANT TO STOP AT PLACES?", True, WHITE), (370, 170))
        screen.blit(font.render("Press 1: NO (Direct to School)", True, WHITE), (370, 210))
        screen.blit(font.render("Press 2: YES (Stop everywhere)", True, WHITE), (370, 240))

    elif game_mode == "STOPPED":
        overlay = pygame.Surface((600, 100), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (300, 300))
        msg = f"STOPPED at {visited_stops[-1]}! SPACE →"
        screen.blit(font.render(msg, True, WHITE), (310, 330))

    elif game_mode == "SCHOOL_ARRIVED":
        overlay = pygame.Surface((600, 200), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (300, 150))
        screen.blit(big_font.render("SCHOOL ARRIVED! 🎓", True, YELLOW), (350, 170))
        screen.blit(font.render("YOU WANT TO GO BACK HOME?", True, WHITE), (380, 210))
        screen.blit(font.render("Y: YES | N: NO", True, WHITE), (390, 240))

    elif game_mode == "COLLISION":
        overlay = pygame.Surface((500, 150), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 180))
        screen.blit(overlay, (350, 200))
        screen.blit(big_font.render("ACCIDENT! 🚗💥", True, WHITE), (380, 220))
        screen.blit(font.render("R: Restart | ESC: Quit", True, WHITE), (390, 260))

    # HUD
    screen.blit(font.render(f"Traffic: {len(traffic)} | Progress: {boy_progress:.0f}", True, WHITE), (10, 10))


# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False

        if event.type == pygame.KEYDOWN:
            if game_mode == "MENU":
                if event.key == pygame.K_1: stop_choice, game_mode = "NO", "TRAVELING"
                if event.key == pygame.K_2: stop_choice, game_mode = "YES", "TRAVELING"

            elif game_mode == "STOPPED" and event.key == pygame.K_SPACE:
                game_mode = "TRAVELING"

            elif game_mode == "SCHOOL_ARRIVED":
                if event.key == pygame.K_y:
                    boy_progress = 0
                    game_mode = "TRAVELING"
                    visited_stops = []
                elif event.key == pygame.K_n:
                    running = False

            elif game_mode == "COLLISION" and event.key == pygame.K_r:
                # Restart
                boy_progress, game_mode, traffic, visited_stops = 0, "MENU", [], []

    # Game logic
    spawn_traffic()
    traffic = [v for v in traffic if v.update()]

    if game_mode == "TRAVELING":
        if check_collision():
            game_mode = "COLLISION"
        else:
            keys = pygame.key.get_pressed()
            speed = 4
            if keys[pygame.K_RIGHT] and boy_progress < WIDTH - 60:
                boy_progress += speed
            if keys[pygame.K_LEFT] and boy_progress > 50:
                boy_progress -= speed

            # Stops
            if stop_choice == "YES":
                for loc in locations:
                    if abs(boy_progress - loc[0]) < 25 and loc[1] not in visited_stops:
                        game_mode = "STOPPED"
                        visited_stops.append(loc[1])
                        break

            # School arrived
            if boy_progress >= WIDTH - 60:
                game_mode = "SCHOOL_ARRIVED"

    # Render
    draw_world()

    for vehicle in traffic:
        vehicle.draw(screen)

    # Boy (with collision outline)
    boy_x, boy_y = boy_progress, get_road_y(boy_progress) - 20
    pygame.draw.rect(screen, BLUE, (boy_x - 15, boy_y - 20, 30, 40))

    if game_mode == "TRAVELING":
        pygame.draw.rect(screen, RED, (boy_x - 15, boy_y - 20, 30, 40), 3)  # Collision box

    draw_ui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
