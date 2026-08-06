# ./main.py

import os, sys, random, pygame, time
from src.dungeon_gen import generate_dungeon
from src.constants import *
from src.focus import remember_focus, restore_focus
from helpers.env import custom_invite

room_by_coord = {}


def draw(screen, font, grid, rooms, seed, status, room_by_coord):
    screen.fill(COLOR_BG)
    if status["status"] != 0:
        label = font.render(f"Error: {status['message']}", True, (255, 0, 0))
        screen.blit(label, (MARGIN, MARGIN + GRID_H * CELL_SIZE + 12))
        return

    room_by_coord = {room.coord: room for room in rooms}
    for x, y in grid:
        rect = pygame.Rect(
            MARGIN + x * CELL_SIZE, MARGIN + y * CELL_SIZE , CELL_SIZE, CELL_SIZE
        )
        if (x, y) in room_by_coord:
            room = room_by_coord[(x, y)]
            color = (
                COLOR_SPAWN
                if room.room_type == "spawn"
                else COLOR_BOSS if room.room_type == "boss" else COLOR_ROOM
            )
        else:
            color = COLOR_EMPTY
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)

    label = font.render(f"seed={seed}  rooms={len(rooms)}", True, COLOR_TEXT)

    screen.blit(label, (MARGIN, MARGIN + GRID_H * CELL_SIZE + 12))
    label = font.render(
        "(R: random seed, ESPACE: seed+1, ECHAP: quitter)", True, COLOR_TEXT
    )
    screen.blit(label, (MARGIN, MARGIN + GRID_H * CELL_SIZE + 36))


def screen_to_grid_coord(mouse_pos, margin, cell_size):
    mx, my = mouse_pos
    gx = (mx - margin) // cell_size
    gy = (my - margin) // cell_size
    return (gx, gy)


def draw_room_inspector(screen, font, room, population, x, y):
    """Panneau texte listant le contenu d'une salle survolée."""
    type_label = (
        "Salle de spawn"
        if room.room_type == "spawn"
        else "Salle de boss" if room.room_type == "boss" else "Salle normale"
    )
    lines = [f"Salle {room.coord} - {type_label}"]
    if room.pattern:
        lines.append(f"Pattern: {room.pattern.pattern_id}")

    if population:
        lines.append("Contenu:")
        for item in population:
            lines.append(f" - {item}")

    if room.pattern and room.pattern.containers:
        lines.append("Conteneurs:")
        for container in room.pattern.containers:
            lines.append(f" - {container}")

    panel_rect = pygame.Rect(x, y, 260, 20 + len(lines) * 20)
    pygame.draw.rect(screen, (20, 20, 24), panel_rect)
    pygame.draw.rect(screen, (90, 90, 100), panel_rect, 1)
    for i, line in enumerate(lines):
        surf = font.render(line, True, (230, 230, 230))
        screen.blit(surf, (x + 8, y + 8 + i * 20))


def main():
    os.environ["SDL_VIDEO_WINDOW_POS"] = (
        f"{APP_LEFT},{APP_TOP}"  # params dans constants.py
    )

    remember_focus()

    pygame.init()
    screen = pygame.display.set_mode(
        (MARGIN * 2 + GRID_W * CELL_SIZE, MARGIN * 3 + GRID_H * CELL_SIZE + 20)
    )
    pygame.display.set_caption("Dungeon Generator")
    font = pygame.font.SysFont(None, 24)

    # Rend le focus à la fenêtre précédente
    time.sleep(0.2)
    restore_focus()

    seed = random.randint(0, 2**32 - 1)
    grid, rooms, status = generate_dungeon(
        seed, continuity_bias=CONTINUITY_BIAS, w=GRID_W, h=GRID_H, max_rooms=MAX_ROOMS
    )
    room_by_coord = {room.coord: room for room in rooms}

    print(f"{custom_invite()}", flush=True)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    seed = random.randint(0, 2**32 - 1)
                    grid, rooms, status = generate_dungeon(
                        seed,
                        continuity_bias=CONTINUITY_BIAS,
                        w=GRID_W,
                        h=GRID_H,
                        max_rooms=MAX_ROOMS,
                    )
                    room_by_coord = {room.coord: room for room in rooms}
                elif event.key == pygame.K_SPACE:
                    seed += 1
                    grid, rooms, status = generate_dungeon(
                        seed,
                        continuity_bias=CONTINUITY_BIAS,
                        w=GRID_W,
                        h=GRID_H,
                        max_rooms=MAX_ROOMS,
                    )
                    room_by_coord = {room.coord: room for room in rooms}
        draw(screen, font, grid, rooms, seed, status, room_by_coord=room_by_coord)
        hovered_coord = screen_to_grid_coord(pygame.mouse.get_pos(), MARGIN, CELL_SIZE)
        hovered_room = room_by_coord.get(hovered_coord)
        if hovered_room:
            population = hovered_room.population if hovered_room.population else []
            draw_room_inspector(screen, font, hovered_room, population, x=20, y=20)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    # print("\n\n" + f"{custom_invite()}", end=" > ", flush=True)


if __name__ == "__main__":
    print("Go!")
    main()
