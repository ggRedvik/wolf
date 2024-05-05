import pygame
import random
import sqlite3

# Инициализация Pygame
pygame.init()

# Размеры окна игры
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Создание окна игры
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Волк и яйца")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Размеры объектов
PLAYER_SIZE = 50
EGG_SIZE = 30
OBSTACLE_SIZE = 50

# Начальные позиции
player_x = WINDOW_WIDTH // 2 - PLAYER_SIZE // 2
player_y = WINDOW_HEIGHT - 100
obstacle_x = random.randint(0, WINDOW_WIDTH - OBSTACLE_SIZE)
obstacle_y = 0 - OBSTACLE_SIZE
eggs = []

# Скорость движения
player_speed = 10
egg_speed = 7
obstacle_speed = 6

# Счет
score = 0
missed_eggs = 0
max_missed_eggs = 3

# Состояние игры
paused = False
game_over = False
menu = True

# Загрузка и масштабирование изображений
player_img = pygame.image.load("волк.jpg").convert_alpha()
player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
egg_img = pygame.image.load("egg.png").convert_alpha()
egg_img = pygame.transform.scale(egg_img, (EGG_SIZE, EGG_SIZE))
obstacle_img = pygame.image.load("препятствие.jpg").convert_alpha()
obstacle_img = pygame.transform.scale(obstacle_img, (OBSTACLE_SIZE, OBSTACLE_SIZE))

# Загрузка звуков
catch_sound = pygame.mixer.Sound("catch.ogg")
crash_sound = pygame.mixer.Sound("crash.ogg")
miss_sound = pygame.mixer.Sound("pass.ogg")

# Функции для отображения и взаимодействия
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if click[0] == 1 and action:
            action()
            pygame.time.wait(150)  # Delay to prevent multiple clicks
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))

    small_text = pygame.font.Font(None, 20)
    text_surf = small_text.render(msg, True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(text_surf, text_rect)

def display_objects():
    screen.blit(player_img, (player_x, player_y))
    for egg in eggs:
        screen.blit(egg_img, (egg[0], egg[1]))
    screen.blit(obstacle_img, (obstacle_x, obstacle_y))

def check_collision(px, py, ex, ey, size):
    return px < ex + size and px + PLAYER_SIZE > ex and py < ey + size and py + PLAYER_SIZE > ey

def reset_game():
    global score, missed_eggs, eggs, obstacle_x, obstacle_y, game_over, paused, menu
    score = 0
    missed_eggs = 0
    eggs = []
    obstacle_x = random.randint(0, WINDOW_WIDTH - OBSTACLE_SIZE)
    obstacle_y = 0 - OBSTACLE_SIZE
    game_over = False
    paused = False
    menu = False

def quitgame():
    save_high_score()
    pygame.quit()
    quit()

def pause_game():
    global paused
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                unpause_game()

        screen.fill(WHITE)
        draw_text("Пауза", pygame.font.Font(None, 50), BLACK, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
        button("Продолжить", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 - 50, 200, 50, GRAY, BLACK, unpause_game)
        button("Новая игра", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, 200, 50, GRAY, BLACK, reset_game)
        button("Выйти", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 50, 200, 50, GRAY, BLACK, quitgame)

        pygame.display.update()
        clock.tick(15)

def unpause_game():
    global paused
    paused = False

def game_menu():
    global menu
    menu = True
    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                pygame.quit()
                quit()

        screen.fill(WHITE)
        draw_text("Волк и Яйца", pygame.font.Font(None, 60), BLACK, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
        button("Новая игра", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 - 50, 200, 50, GRAY, BLACK, reset_game)
        button("Рекорды", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, 200, 50, GRAY, BLACK, show_high_scores)
        button("Выйти", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 50, 200, 50, GRAY, BLACK, quitgame)
        pygame.display.update()

def game_over_screen():
    global game_over
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                pygame.quit()
                quit()

        screen.fill(WHITE)
        draw_text("Ты проиграл!", pygame.font.Font(None, 50), BLACK, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 4)
        button("Новая игра", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 - 50, 200, 50, GRAY, BLACK, reset_game)
        button("Рекорды", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2, 200, 50, GRAY, BLACK, show_high_scores)
        button("Выйти", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 50, 200, 50, GRAY, BLACK, quitgame)

        pygame.display.update()
        clock.tick(15)

def show_high_scores():
    global menu
    menu = True
    conn = sqlite3.connect('high_scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS high_scores
                 (score INTEGER)''')
    c.execute("SELECT * FROM high_scores ORDER BY score DESC LIMIT 5")
    high_scores = c.fetchall()
    conn.close()

    while menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                pygame.quit()
                quit()

        screen.fill(WHITE)
        draw_text("Рекорды", pygame.font.Font(None, 60), BLACK, screen, WINDOW_WIDTH / 2, WINDOW_HEIGHT / 8)
        y = WINDOW_HEIGHT / 4
        for score in high_scores:
            draw_text(f"Счет: {score[0]}", pygame.font.Font(None, 36), BLACK, screen, WINDOW_WIDTH / 2, y)
            y += 50
        button("Назад", WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT - 100, 200, 50, GRAY, BLACK, game_menu)
        pygame.display.update()

def save_high_score():
    conn = sqlite3.connect('high_scores.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS high_scores
             (score INTEGER)''')
    c.execute("INSERT INTO high_scores (score) VALUES (?)", (score,))
    conn.commit()
    conn.close()

# Таймеры для игры
clock = pygame.time.Clock()
egg_timer = pygame.USEREVENT + 1
pygame.time.set_timer(egg_timer, 2000)

# Основной игровой цикл
game_menu()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score()
            pygame.quit()
            quit()
        if event.type == egg_timer:
            eggs.append([random.randint(0, WINDOW_WIDTH - EGG_SIZE), 0])
        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            pause_game()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WINDOW_WIDTH - PLAYER_SIZE:
        player_x += player_speed

    if not game_over:
        screen.fill(WHITE)
        display_objects()

        obstacle_y += obstacle_speed
        if obstacle_y > WINDOW_HEIGHT:
            obstacle_x = random.randint(0, WINDOW_WIDTH - OBSTACLE_SIZE)
            obstacle_y = 0 - OBSTACLE_SIZE

        for egg in eggs[:]:
            egg[1] += egg_speed
            if egg[1] > WINDOW_HEIGHT:
                eggs.remove(egg)
                missed_eggs += 1
                miss_sound.play()
                if missed_eggs >= max_missed_eggs:
                    game_over = True
            elif check_collision(player_x, player_y, egg[0], egg[1], EGG_SIZE):
                eggs.remove(egg)
                score += 1
                catch_sound.play()

        if check_collision(player_x, player_y, obstacle_x, obstacle_y, OBSTACLE_SIZE):
            crash_sound.play()
            game_over = True

        draw_text(f"Счет: {score}", pygame.font.Font(None, 30), BLACK, screen, 70, 20)
        draw_text(f" {missed_eggs}/{max_missed_eggs}", pygame.font.Font(None, 30), BLACK, screen, 70, 50)

        pygame.display.update()
        clock.tick(60)
    else:
        save_high_score()
        game_over_screen()