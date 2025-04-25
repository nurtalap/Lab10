import pygame
import random
import pygame
import psycopg2
from collections import namedtuple

pygame.init()
pygame.font.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Enhanced Snake Game with Timed Food")

# ========== DATABASE ==========
def get_connection():
    return psycopg2.connect(
        dbname="gameusers",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

def get_or_create_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, level, user_score, speed_level FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    if user:
        user_id, level, score, speed = user
    else:
        cur.execute(
            "INSERT INTO users (username, level, user_score, speed_level) VALUES (%s, %s, %s, %s) RETURNING id",
            (username, 1, 0, 1)
        )
        user_id = cur.fetchone()[0]
        level, score, speed = 1, 0, 1
        conn.commit()
    cur.close()
    conn.close()
    return user_id, level, score, speed

def save_user_score(user_id, level, score, speed_level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET level=%s, user_score=%s, speed_level=%s WHERE id=%s",
        (level, score, speed_level, user_id)
    )
    conn.commit()
    cur.close()
    conn.close()

# ========== USERNAME INPUT ==========
def get_username_pygame():
    input_active = True
    username = ""
    input_box = pygame.Rect(width // 2 - 150, height // 2 - 30, 300, 50)
    font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    while input_active:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20 and event.unicode.isprintable():
                        username += event.unicode

        prompt = font.render("Enter your username:", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(width // 2, height // 2 - 70)))
        pygame.draw.rect(screen, (255, 255, 255), input_box, 2)
        screen.blit(font.render(username, True, (255, 255, 255)), (input_box.x + 10, input_box.y + 10))
        pygame.display.flip()
        clock.tick(30)

    return username

username = get_username_pygame()
user_id, level, score, speed_level = get_or_create_user(username)

# ========== GAME SETUP ==========
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

FoodType = namedtuple('FoodType', ['color', 'weight', 'points', 'duration'])
FOOD_TYPES = [
    FoodType(RED, 70, 10, 10000),
    FoodType(BLUE, 20, 25, 5000),
    FoodType(PURPLE, 10, 50, 3000)
]

fruits_per_level = 3
fruits_eaten_total = 0
base_delay = 200
current_delay = max(50, base_delay - (speed_level - 1) * 40)

head_square = [100, 100]
squares = [[x, 100] for x in range(30, 101, 10)]
direction = "right"
next_dir = "right"

class Food:
    def __init__(self, position, food_type, spawn_time):
        self.position = position
        self.food_type = food_type
        self.spawn_time = spawn_time
    
    def is_expired(self, current_time):
        return current_time - self.spawn_time > self.food_type.duration

def draw_grid():
    for x in range(0, width, 10):
        pygame.draw.line(screen, GRAY, (x, 0), (x, height), 1)
    for y in range(0, height, 10):
        pygame.draw.line(screen, GRAY, (0, y), (width, y), 1)

def game_over(font, size, color):
    global done
    save_user_score(user_id, level, score, speed_level)
    overlay = pygame.Surface((width, height))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(200)
    screen.blit(overlay, (0, 0))
    g_o_font = pygame.font.SysFont(font, size - 10, bold=True)
    msg = f"Game Over! Score: {score} - Level: {level} - Speed: {speed_level}"
    screen.blit(g_o_font.render(msg, True, BLACK), (width//2+2 - g_o_font.size(msg)[0]//2, height//2+2))
    screen.blit(g_o_font.render(msg, True, color), (width//2 - g_o_font.size(msg)[0]//2, height//2))
    pygame.display.update()
    pygame.time.delay(4000)
    pygame.quit()

def spawn_food():
    while True:
        x = random.randrange(1, width//10) * 10
        y = random.randrange(1, height//10) * 10
        if [x, y] not in squares:
            food_type = random.choices(FOOD_TYPES, weights=[ft.weight for ft in FOOD_TYPES], k=1)[0]
            return Food([x, y], food_type, pygame.time.get_ticks())

current_food = spawn_food()
clock = pygame.time.Clock()
done = False
paused = False

while not done:
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_user_score(user_id, level, score, speed_level)
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused:
                    save_user_score(user_id, level, score, speed_level)
            if not paused:
                if event.key == pygame.K_DOWN: next_dir = "down"
                elif event.key == pygame.K_UP: next_dir = "up"
                elif event.key == pygame.K_LEFT: next_dir = "left"
                elif event.key == pygame.K_RIGHT: next_dir = "right"

    if paused: continue

    if head_square in squares[:-1]:
        game_over("arial", 45, YELLOW)

    if next_dir == "right" and direction != "left": direction = "right"
    elif next_dir == "up" and direction != "down": direction = "up"
    elif next_dir == "left" and direction != "right": direction = "left"
    elif next_dir == "down" and direction != "up": direction = "down"

    if direction == "right": head_square[0] += 10
    elif direction == "left": head_square[0] -= 10
    elif direction == "up": head_square[1] -= 10
    elif direction == "down": head_square[1] += 10

    if not (0 <= head_square[0] < width and 0 <= head_square[1] < height):
        game_over("arial", 30, YELLOW)

    squares.append(head_square.copy())
    squares.pop(0)

    fruit_eaten = False
    if head_square == current_food.position:
        fruit_eaten = True
        score += current_food.food_type.points
        fruits_eaten_total += 1
        if fruits_eaten_total % fruits_per_level == 0:
            level += 1
            speed_level += 1
            current_delay = max(50, base_delay - (speed_level - 1) * 40)
        current_food = spawn_food()
    elif current_food.is_expired(current_time):
        current_food = spawn_food()

    if fruit_eaten:
        squares.insert(0, squares[0].copy())

    screen.fill(BLACK)
    draw_grid()

    stats_font = pygame.font.SysFont("arial", 20, bold=True)
    stats_text = f"User: {username}  Score: {score}  Level: {level}  Speed: {speed_level}"
    screen.blit(stats_font.render(stats_text, True, BLACK), (12, 12))
    screen.blit(stats_font.render(stats_text, True, WHITE), (10, 10))

    food_color = current_food.food_type.color
    time_left = max(0, current_food.food_type.duration - (current_time - current_food.spawn_time))
    alpha = int((time_left / current_food.food_type.duration) * 255)

    glow_surface = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*YELLOW, 100), (7, 7), 7)
    screen.blit(glow_surface, (current_food.position[0]-2, current_food.position[1]-2))

    food_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(food_surface, (*food_color, alpha), (5, 5), 5)
    screen.blit(food_surface, current_food.position)

    for i, el in enumerate(squares):
        green_value = min(255, 100 + i * 10)
        pygame.draw.rect(screen, (0, green_value, 0), pygame.Rect(el[0], el[1], 10, 10))
        pygame.draw.rect(screen, DARK_GREEN, pygame.Rect(el[0], el[1], 10, 10), 1)

    pygame.draw.rect(screen, GREEN, pygame.Rect(head_square[0], head_square[1], 10, 10))
    pygame.draw.rect(screen, DARK_GREEN, pygame.Rect(head_square[0], head_square[1], 10, 10), 1)

    pygame.display.flip()
    pygame.time.delay(current_delay)
    clock.tick(60)

pygame.quit()
