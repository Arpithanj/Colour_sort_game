import copy
import random
import pygame

# initialize pygame
pygame.init()
pygame.mixer.init()

# initialize game variables
WIDTH = 500
HEIGHT = 550  # Adjusted for 4 colors
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('ColorSort PyGame By @rpi&Kusu')
font = pygame.font.Font('freesansbold.ttf', 24)
fps = 60
timer = pygame.time.Clock()
color_choices = ['red', 'orange', 'light blue', 'dark blue', 'dark green', 'pink', 'purple', 'dark gray',
                 'brown', 'light green', 'yellow', 'white']
tube_colors = []
initial_colors = []
tubes = 10
new_game = True
selected = False
tube_rects = []
select_rect = 100
win = False
level = 1
show_hint = False

# undo and redo stacks
undo_stack = []
redo_stack = []

# Load sound effects
move_sound = pygame.mixer.Sound('C:\\Users\\arpit\\Downloads\\colorSortPyGame-main\\colorSortPyGame-main\\Sound\\Winning.wav')
win_sound = pygame.mixer.Sound('C:\\Users\\arpit\\Downloads\\colorSortPyGame-main\\colorSortPyGame-main\\Sound\\Piano Loop 01.wav')
select_sound = pygame.mixer.Sound('C:\\Users\\arpit\\Downloads\\colorSortPyGame-main\\colorSortPyGame-main\\Sound\\Winning.wav')

# select a number of tubes and pick random colors upon new game setup
def generate_start(level):
    tubes_number = min(10 + level, 14)  # Increase tubes with level, max 14
    tubes_colors = []
    available_colors = []
    for i in range(tubes_number):
        tubes_colors.append([])
        if i < tubes_number - 2:
            for j in range(4):  # Adjusted to 4 colors per tube
                available_colors.append(i)
    for i in range(tubes_number - 2):
        for j in range(4):  # Adjusted to 4 colors per tube
            color = random.choice(available_colors)
            tubes_colors[i].append(color)
            available_colors.remove(color)
    random.shuffle(tubes_colors)  # Shuffle to increase complexity
    return tubes_number, tubes_colors

# draw all tubes and colors on screen, as well as indicating what tube was selected
def draw_tubes(tubes_num, tube_cols):
    tube_boxes = []
    if tubes_num % 2 == 0:
        tubes_per_row = tubes_num // 2
        offset = False
    else:
        tubes_per_row = tubes_num // 2 + 1
        offset = True
    spacing = WIDTH / tubes_per_row
    for i in range(tubes_per_row):
        for j in range(len(tube_cols[i])):
            pygame.draw.rect(screen, color_choices[tube_cols[i][j]], [5 + spacing * i, 200 - (50 * j), 65, 50], 0, 3)  # Adjusted for 4 colors
        box = pygame.draw.rect(screen, 'blue', [5 + spacing * i, 50, 65, 200], 5, 5)  # Adjusted for 4 colors
        if select_rect == i:
            pygame.draw.rect(screen, 'green', [5 + spacing * i, 50, 65, 200], 3, 5)  # Adjusted for 4 colors
        tube_boxes.append(box)
    if offset:
        for i in range(tubes_per_row - 1):
            for j in range(len(tube_cols[i + tubes_per_row])):
                pygame.draw.rect(screen, color_choices[tube_cols[i + tubes_per_row][j]],
                                 [(spacing * 0.5) + 5 + spacing * i, 450 - (50 * j), 65, 50], 0, 3)  # Adjusted for 4 colors
            box = pygame.draw.rect(screen, 'blue', [(spacing * 0.5) + 5 + spacing * i, 300, 65, 200], 5, 5)  # Adjusted for 4 colors
            if select_rect == i + tubes_per_row:
                pygame.draw.rect(screen, 'green', [(spacing * 0.5) + 5 + spacing * i, 300, 65, 200], 3, 5)  # Adjusted for 4 colors
            tube_boxes.append(box)
    else:
        for i in range(tubes_per_row):
            for j in range(len(tube_cols[i + tubes_per_row])):
                pygame.draw.rect(screen, color_choices[tube_cols[i + tubes_per_row][j]], [5 + spacing * i,
                                                                                          450 - (50 * j), 65, 50], 0, 3)  # Adjusted for 4 colors
            box = pygame.draw.rect(screen, 'blue', [5 + spacing * i, 300, 65, 200], 5, 5)  # Adjusted for 4 colors
            if select_rect == i + tubes_per_row:
                pygame.draw.rect(screen, 'green', [5 + spacing * i, 300, 65, 200], 3, 5)  # Adjusted for 4 colors
            tube_boxes.append(box)
    return tube_boxes

# Determine if a move is valid and return it
def get_hint(colors):
    for i in range(len(colors)):
        if len(colors[i]) > 0:
            color_to_move = colors[i][-1]
            for j in range(len(colors)):
                if i != j and len(colors[j]) < 4:
                    if len(colors[j]) == 0 or colors[j][-1] == color_to_move:
                        return i, j
    return None, None

# determine the top color of the selected tube and destination tube,
# as well as how long a chain of that color to move
def calc_move(colors, selected_rect, destination):
    chain = True
    color_on_top = 100
    length = 1
    color_to_move = 100
    if len(colors[selected_rect]) > 0:
        color_to_move = colors[selected_rect][-1]
        for i in range(1, len(colors[selected_rect])):
            if chain:
                if colors[selected_rect][-1 - i] == color_to_move:
                    length += 1
                else:
                    chain = False
    if 4 > len(colors[destination]):
        if len(colors[destination]) == 0:
            color_on_top = color_to_move
        else:
            color_on_top = colors[destination][-1]
    if color_on_top == color_to_move:
        for i in range(length):
            if len(colors[destination]) < 4:
                if len(colors[selected_rect]) > 0:
                    colors[destination].append(color_on_top)
                    colors[selected_rect].pop(-1)
    return colors

# check if every tube with colors is 4 long and all the same color. That's how we win
def check_victory(colors):
    won = True
    for i in range(len(colors)):
        if len(colors[i]) > 0:
            if len(colors[i]) != 4:
                won = False
            else:
                main_color = colors[i][-1]
                for j in range(len(colors[i])):
                    if colors[i][j] != main_color:
                        won = False
    return won

# main game loop
run = True
while run:
    screen.fill('black')
    timer.tick(fps)
    # generate game board on new game, make a copy of the colors in case of restart
    if new_game:
        tubes, tube_colors = generate_start(level)
        initial_colors = copy.deepcopy(tube_colors)
        new_game = False
    # draw tubes every cycle
    else:
        tube_rects = draw_tubes(tubes, tube_colors)
        # Highlight hint if show_hint is true
        if show_hint:
            hint_from, hint_to = get_hint(tube_colors)
            if hint_from is not None and hint_to is not None:
                pygame.draw.rect(screen, 'yellow', tube_rects[hint_from], 3)  # Highlight source tube
                pygame.draw.rect(screen, 'yellow', tube_rects[hint_to], 3)    # Highlight destination tube

    # check for victory every cycle
    win = check_victory(tube_colors)

    # event handling - Quit button exits, clicks select tubes, enter and space for restart and new board
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                tube_colors = copy.deepcopy(initial_colors)
            elif event.key == pygame.K_RETURN:
                new_game = True
                if win:
                    level += 1
                    win = False
            elif event.key == pygame.K_u:  # Undo action
                if undo_stack:
                    redo_stack.append(copy.deepcopy(tube_colors))
                    tube_colors = undo_stack.pop()
            elif event.key == pygame.K_r:  # Redo action
                if redo_stack:
                    undo_stack.append(copy.deepcopy(tube_colors))
                    tube_colors = redo_stack.pop()
            elif event.key == pygame.K_h:  # Hint action
                show_hint = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Check if the hint button was clicked
            if pygame.Rect(10, HEIGHT - 40, 100, 30).collidepoint(pos):
                show_hint = True
            elif not selected:
                for item in range(len(tube_rects)):
                    if tube_rects[item].collidepoint(pos):
                        selected = True
                        select_rect = item
                        select_sound.play()  # Play select sound
            else:
                for item in range(len(tube_rects)):
                    if tube_rects[item].collidepoint(pos):
                        dest_rect = item
                        undo_stack.append(copy.deepcopy(tube_colors))  # Save state before move
                        tube_colors = calc_move(tube_colors, select_rect, dest_rect)
                        move_sound.play()  # Play move sound
                        redo_stack.clear()  # Clear redo stack after new move
                        selected = False
                        select_rect = 100
                        show_hint = False  # Hide hint after making a move

    # draw 'victory' text when winning in middle, always show restart and new board text at top
    if win:
        victory_text = font.render(f'Level {level} Completed! Press Enter for Next Level!', True, 'white')
        screen.blit(victory_text, (30, 265))
        win_sound.play()  # Play win sound

    restart_text = font.render('ColourSort', True, 'white')
    screen.blit(restart_text, (10, 10))
    level_text = font.render(f'Level: {level}', True, 'white')
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))  # Positioning level text in top right corner

    # draw hint button
    hint_button = pygame.draw.rect(screen, 'blue', [10, HEIGHT - 40, 100, 30], 0, 5)
    hint_text = font.render('Hint', True, 'white')
    screen.blit(hint_text, (20, HEIGHT - 35))

    # display all drawn items on screen, exit pygame if run == False
    pygame.display.flip()
pygame.quit()
