import pygame #MODULE FOR CREATING THIS GAME
import random
import time
import sys

pygame.init()

# ---------------- CONFIGURATIONS ----------------
WIDTH, HEIGHT = 800, 600
FPS = 60
GAME_TIME = 30 #time limit

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cupid Vector Game")
clock = pygame.time.Clock()

font = pygame.font.Font("Assets/Pixel_font.ttf", 36)
FONT_COLOR = (199, 21, 133)  # dark pink

# --------------- ASSETS -------------
heart_imgs = [
    pygame.image.load("Assets/red_heart.png").convert_alpha(),
    pygame.image.load("Assets/pink_heart.png").convert_alpha()
]
heart_imgs = [pygame.transform.scale(img, (60, 60)) for img in heart_imgs]

arrow_img = pygame.image.load("Assets/arrow2.png").convert_alpha()
arrow_img = pygame.transform.scale(arrow_img, (80, 80))

newbackground_img = pygame.image.load("Assets/newbackground.png").convert_alpha()
newbackground_img = pygame.transform.scale(newbackground_img, (WIDTH, HEIGHT))

cupid_img = pygame.image.load("Assets/cupid.png").convert_alpha()
cupid_img = pygame.transform.scale(cupid_img, (200, 200))

# ---------------- GAME STATES (WHICH SCREEN TO SHOW)-------------
MENU = "menu"
GAME = "game"
WITHDRAW = "withdraw"
FINAL_SCORE = "final_score"
state = MENU

# ---------------- PLAYER ------------------
player_pos = pygame.Vector2(10, HEIGHT // 2) #CUPID'S POSITION 

# ---------------- ARROWS -------------------
arrows = []  # multiple arrows
arrow_vel = pygame.Vector2(20, 0) # velocity 

# ---------------- HEARTS ------------------
def create_hearts(): 
    hearts = []
    for _ in range(15): #to create 15 hearts at random positions and falling speed
        img = random.choice(heart_imgs)
        hearts.append({
            "img": img,
            "pos": pygame.Vector2(random.randint(200, WIDTH), random.randint(-600, 0)),
            "vel": pygame.Vector2(0, random.randint(2, 4)),
            "hit": False, #if arrow has hit it
            "combo": False, #to make the arrow stick with the heart if hit
            "combo_vel": pygame.Vector2(10, 0) #combines the two in same speed as they exit the screen
        })
    return hearts

hearts = []
score = 0
start_time = 0
HEARTBEATS = 100 

# ---------------- FUNCTIONS ---------------
def draw_text_center(text, y): # to center text on screen
    surf = font.render(text, True, FONT_COLOR)
    screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y))

def draw_menu(): #shows the main text on top of the bg
    screen.blit(newbackground_img, (0, 0))
    draw_text_center("Cupid Vector Game", 200)
    draw_text_center("Press 1 - Play Game", 350)
    draw_text_center("Press 2 - ISBN Points", 400)

def draw_final_score():
    screen.blit(newbackground_img, (0, 0))
    draw_text_center("Game Over!", 200)
    draw_text_center(f"Final Score: {score}", 300)
    draw_text_center("ESC to return to Menu", 350)

def start_game(): #game set ups
    global hearts, score, start_time, arrows
    hearts = create_hearts()
    score = 0 #starting point
    arrows = [] 
    start_time = time.time()

# ---------------- ISBN / Heartbeat Withdrawal -----------------
def withdraw_points():
    global HEARTBEATS
    running_withdraw = True
    while running_withdraw:
        screen.blit(newbackground_img, (0, 0))
        draw_text_center(f"Starting Heartbeats: {HEARTBEATS}", 100)
        draw_text_center("Enter ISBN in the console", 250)
        draw_text_center("to accumulate more points", 300)
        draw_text_center("Type 'quit' to exit", 450)
        pygame.display.flip()

        # Get ISBN input from console
        user_input = input("Enter ISBN (X-XXX-XXXXX-X) or 'quit' to exit: ").strip()
        if user_input.lower() == "quit":
            running_withdraw = False
            break

        # Remove hyphens for calculation
        digits = user_input.replace("-", "")
        if len(digits) != 10 or not digits[:-1].isdigit() or (not digits[-1].isdigit() and digits[-1] != 'X'):
            print("Invalid ISBN format!")
            continue

        # Calculate check digit
        total = 0
        for i in range(9):
            total += int(digits[i]) * (i + 1)
        check_digit = total % 11

        entered_digit = digits[-1] #represents check or last digit
        if entered_digit == 'X':
            entered_digit = 10
        else:
            entered_digit = int(entered_digit)

        if check_digit == entered_digit: #so the check / last digit must be equal to the remainder of the sum of the indiv numbers times their index divided by 11
            print(f"{user_input} is VALID!")
            draw_text_center(f"{user_input} is VALID!", 300)
            HEARTBEATS += 10  # reward for valid ISBN
        else:
            print(f"{user_input} is INVALID! Correct check digit is {check_digit}")
            draw_text_center(f"{user_input} is INVALID! Correct: {check_digit}", 300)

        pygame.display.flip()
        print(f"Current Heartbeats: {HEARTBEATS}")

# ---------------- MAIN LOOP ----------------
running = True # game keeps running; program ends when player closes the window (false)
while running:
    clock.tick(FPS)

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == MENU:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    start_game()
                    state = GAME
                elif event.key == pygame.K_2:
                    state = WITHDRAW
                    withdraw_points()
                    state = MENU  # return to menu after withdrawal

        elif state == GAME:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Shoot a new arrow from Cupid's hand
                    arrows.append(pygame.Vector2(
                        player_pos.x + cupid_img.get_width() // 2,
                        player_pos.y - 43
                    ))

        elif state == FINAL_SCORE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = MENU

    # --- DRAW ---
    if state == MENU:
        draw_menu()
    elif state == GAME:
        # Draw background
        screen.blit(newbackground_img, (0, 0))

        # Update hearts
        for h in hearts:
            if h["combo"]:
                h["pos"] += h["combo_vel"]
                if h["pos"].x > WIDTH + 50:
                    h["combo"] = False
            else:
                h["pos"] += h["vel"]
                if h["pos"].y > HEIGHT:
                    h["pos"].y = random.randint(-600, 0)
                    h["pos"].x = random.randint(200, WIDTH)
                    h["hit"] = False

        # Update arrows
        for arrow_pos in arrows[:]:
            arrow_pos += arrow_vel

            # Collision detection
            for h in hearts:
                if not h["hit"] and arrow_pos.distance_to(h["pos"]) < 50:
                    h["hit"] = True
                    h["combo"] = True
                    score += 100
                    if arrow_pos in arrows:
                        arrows.remove(arrow_pos)
                    break

            # Remove arrow if off screen
            if arrow_pos in arrows and arrow_pos.x > WIDTH:
                arrows.remove(arrow_pos)

        # Draw player (Cupid)
        screen.blit(cupid_img, (player_pos.x, player_pos.y - cupid_img.get_height()//2))

        # Draw all arrows
        for arrow_pos in arrows:
            screen.blit(arrow_img, (arrow_pos.x, arrow_pos.y))

        # Draw hearts
        for h in hearts:
            screen.blit(h["img"], h["pos"])

        # Draw UI
        elapsed = int(time.time() - start_time)
        screen.blit(font.render(f"Score: {score}", True, FONT_COLOR), (10, 10))
        screen.blit(font.render(f"Time: {max(GAME_TIME - elapsed, 0)}", True, FONT_COLOR), (10, 50))
        screen.blit(font.render(f"Heartbeats: {HEARTBEATS}", True, FONT_COLOR), (10, 90))

        # End game after time
        if elapsed >= GAME_TIME:
            state = FINAL_SCORE

    elif state == FINAL_SCORE:
        draw_final_score()

    pygame.display.flip()

pygame.quit()
sys.exit()
