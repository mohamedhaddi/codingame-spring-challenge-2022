"""
Codingame handle: 3ataja
League: Legend
To watch this bot, click on "VIEW LAST BATTLES": https://www.codingame.com/multiplayer/bot-programming/spring-challenge-2022/leaderboard?column=keyword&value=3ataja
"""

import sys
from types import SimpleNamespace
import math

def get_entities(entity_count):

    monsters = []
    my_heroes = []
    enemy_heroes = []

    TYPE_MONSTER = 0
    TYPE_MY_HERO = 1
    TYPE_OP_HERO = 2

    for i in range(entity_count):
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
        action = "WAIT"

        entity = SimpleNamespace(**{
            'id': _id,                      # _id: Unique identifier
            'type': _type,                  # _type: 0=monster, 1=your hero, 2=opponent hero
            'x': x, 'y': y,                 # x,y: Position of this entity
            'shield_life': shield_life,     # shield_life: Ignore for this league; Count down until shield spell fades
            'is_controlled': is_controlled, # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
            'health': health,               # health: Remaining health of this monster
            'vx': vx, 'vy': vy,             # vx,vy: Trajectory of this monster
            'near_base': near_base,         # near_base: 0=monster with no target yet, 1=monster targeting a base
            'threat_for': threat_for,       # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
            'action': action
        })

        if _type == TYPE_MONSTER:
            monsters.append(entity)
        elif _type == TYPE_MY_HERO:
            my_heroes.append(entity)
        elif _type == TYPE_OP_HERO:
            enemy_heroes.append(entity)

    return monsters, my_heroes, enemy_heroes

def rank_monsters(monsters, base_x, base_y, enemy_heroes, threat_for):
    monsters_ranked = {}
    for monster in monsters:
        base_monster_dist = math.hypot(base_x - monster.x, base_y - monster.y)
        threat_level = 1 / (base_monster_dist + 1)
        if threat_for == 2:
            threat_level += monster.health
        if monster.threat_for == threat_for:
            threat_level *= 2
        if threat_for == 1:
            for enemy in enemy_heroes:
                base_enemy_dist = math.hypot(base_x - enemy.x, base_y - enemy.y)
                if base_enemy_dist <= 7000:
                    monster_enemy_dist = math.hypot(monster.x - enemy.x, monster.y - enemy.y)
                    if monster_enemy_dist <= 1280 + 800:
                        threat_level *= 2
        monsters_ranked[threat_level] = monster
    monsters_ranked = list(dict(sorted(monsters_ranked.items(), reverse=True)).values())
    return monsters_ranked

def get_closest_entity_to_entity(entities, entity):
    closest_entity_id = -1
    closest_entity_dist = 999999999
    for e in entities:
        dist = math.hypot(e.x - entity.x, e.y - entity.y)
        if dist < closest_entity_dist:
            closest_entity_id = e.id
            closest_entity_dist = dist
    return closest_entity_id

def get_closest_monsters_to_base(monsters, base_x, base_y, max_monster_base_dist):
    closest_monsters_to_base = []
    for monster in monsters:
        monster_base_dist = math.hypot(base_x - monster.x, base_y - monster.y)
        if monster_base_dist <= max_monster_base_dist:
            closest_monsters_to_base.append((monster_base_dist, monster))
    closest_monsters_to_base = sorted(closest_monsters_to_base, key=lambda x: x[0])
    return closest_monsters_to_base

def get_closest_monsters_to_hero_from_base(monsters, hero, base_x, base_y, max_monster_base_dist):
    closest_monsters_to_base = get_closest_monsters_to_base(monsters, base_x, base_y, max_monster_base_dist)
    closest_monsters_to_hero = []
    for monster in closest_monsters_to_base:
        monster_hero_dist = math.hypot(hero.x - monster[1].x, hero.y - monster[1].y)
        if hero.id == 0 or hero.id == 5:
            closest_monsters_to_hero.append((monster_hero_dist, monster[1]))
        elif (guards_thresholds[hero.id]['min']['x'] <= monster[1].x <= guards_thresholds[hero.id]['max']['x']) and \
           (guards_thresholds[hero.id]['min']['y'] <= monster[1].y <= guards_thresholds[hero.id]['max']['y']):
            closest_monsters_to_hero.append((monster_hero_dist, monster[1]))
    closest_monsters_to_hero = sorted(closest_monsters_to_hero, key=lambda x: x[0])
    return closest_monsters_to_hero

def get_closest_enemy_to_base(enemy_heroes, base_x, base_y):
    closest_enemy_to_base = None
    closest_enemy_to_base_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_base_dist = math.hypot(base_x - enemy_hero.x, base_y - enemy_hero.y)
        if enemy_base_dist < closest_enemy_to_base_dist:
            closest_enemy_to_base_dist = enemy_base_dist
            closest_enemy_to_base = (enemy_base_dist, enemy_hero)
    return closest_enemy_to_base

def get_closest_enemy_to_hero(enemy_heroes, hero):
    closest_enemy_to_hero = (None, 9999999)
    closest_enemy_to_hero_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_hero_dist = math.hypot(hero.x - enemy_hero.x, hero.y - enemy_hero.y)
        if enemy_hero_dist < closest_enemy_to_hero_dist:
            closest_enemy_to_hero_dist = enemy_hero_dist
            closest_enemy_to_hero = (enemy_hero, enemy_hero_dist)
    return closest_enemy_to_hero

def get_closest_enemy_to_monster(enemy_heroes, monster):
    closest_enemy_to_monster = None
    closest_enemy_to_monster_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_monster_dist = math.hypot(monster.x - enemy_hero.x, monster.y - enemy_hero.y)
        if enemy_monster_dist < closest_enemy_to_monster_dist:
            closest_enemy_to_monster_dist = enemy_monster_dist
            closest_enemy_to_monster = (enemy_monster_dist, enemy_hero)
    return closest_enemy_to_monster

def get_number_of_monsters_in_hero_wind_range(monsters, hero):
    number_of_monsters_in_hero_wind_range = 0
    for monster in monsters:
        monster_hero_dist = math.hypot(hero.x - monster.x, hero.y - monster.y)
        if monster_hero_dist <= 1280 and not monster.shield_life:
            number_of_monsters_in_hero_wind_range += 1
    return number_of_monsters_in_hero_wind_range

def get_number_of_monsters_in_hero_range(monsters, hero):
    number_of_monsters_in_hero_range = 0
    for monster in monsters:
        monster_hero_dist = math.hypot(hero.x - monster.x, hero.y - monster.y)
        if monster_hero_dist <= 2200:
            number_of_monsters_in_hero_range += 1
    return number_of_monsters_in_hero_range

def get_number_of_unshielded_monsters_in_hero_wind_range(monsters, hero):
    number_of_unshielded_monsters_in_hero_wind_range = 0
    for monster in monsters:
        monster_hero_dist = math.hypot(hero.x - monster.x, hero.y - monster.y)
        if monster_hero_dist <= 1280 and not monster.shield_life:
            number_of_unshielded_monsters_in_hero_wind_range += 1
    return number_of_unshielded_monsters_in_hero_wind_range

base_x, base_y = [int(i) for i in input().split()]
enemy_base_x = 17630 - base_x
enemy_base_y = 9000 - base_y
heroes_per_player = int(input()) # Always 3
initial_heroes_position = 'top-left' if base_x == 0 else 'bottom-right'
rounds_count = 0

heroes_strategic_points = {
    0: {'x': 9000, 'y': 7000},
    1: {'x': 7000, 'y': 3000},
    2: {'x': 4000, 'y': 6500},
    3: {'x': base_x - 7000, 'y': base_y - 3000},
    4: {'x': base_x - 4000, 'y': base_y - 6500},
    5: {'x': base_x - 9000, 'y': base_y - 7000}
}

guards_thresholds = {
    1: {
        'min': {'x': 0, 'y': 0},
        'max': {'x': 9000, 'y': 6000}
    },
    2: {
        'min': {'x': 0, 'y': 0},
        'max': {'x': 6000, 'y': 9000}
    },
    3: {
        'min': {'x': base_x - 9000, 'y': base_y - 6000},
        'max': {'x': base_x, 'y': base_y}
    },
    4: {
        'min': {'x': base_x - 6000, 'y': base_y - 9000},
        'max': {'x': base_x, 'y': base_y}
    },
}

i_attacker_strategic_points = 0
attacker_strategic_points = {
    0: [
        (enemy_base_x - 7000, enemy_base_y - 1000),
        (enemy_base_x - 6250, enemy_base_y - 2250),
        (enemy_base_x - 5500, enemy_base_y - 3250),
        (enemy_base_x - 4500, enemy_base_y - 4750),
        (enemy_base_x - 2500, enemy_base_y - 6000),
        (enemy_base_x - 1000, enemy_base_y - 6500),
        (enemy_base_x - 2500, enemy_base_y - 6000),
        (enemy_base_x - 4500, enemy_base_y - 4750),
        (enemy_base_x - 5500, enemy_base_y - 3250),
        (enemy_base_x - 6250, enemy_base_y - 2250),
    ],
    5: [
        (7000, 1000),
        (6250, 2250),
        (5500, 3250),
        (4500, 4750),
        (2500, 6000),
        (1000, 6500),
        (2500, 6000),
        (4500, 4750),
        (5500, 3250),
        (6250, 2250),
    ]
}

i_first_defender_strategic_points = 0
first_defender_strategic_points = {
    1: [
        (7250, 2250),
        (7000, 3000),
        (6750, 3750),
        (7000, 3000),
    ],
    3: [
        (base_x - 7250, base_y - 2250),
        (base_x - 7000, base_y - 3000),
        (base_x - 6750, base_y - 3750),
        (base_x - 7000, base_y - 3000),
    ]
}

i_second_defender_strategic_points = 0
second_defender_strategic_points = {
    2: [
        (4250, 5250),
        (4000, 6000),
        (3750, 6750),
        (4000, 6000),
    ],
    4: [
        (base_x - 4250, base_y - 5250),
        (base_x - 4000, base_y - 6000),
        (base_x - 3750, base_y - 6750),
        (base_x - 4000, base_y - 6000),
    ]
}

move_towards_pushed_monster = False
pushed_monster_id = -1
pushed_monster_coords = {'x': 0, 'y': 0}
pushed_monster_velocity = {'x': 0, 'y': 0}

# game loop
while True:

    # health: Your base health
    # mana: Ignore in the first league; Spend ten mana to cast a spell
    my_health, my_mana = [int(j) for j in input().split()]
    enemy_health, enemy_mana = [int(j) for j in input().split()]

    # entity_count: Amount of heros and monsters you can see
    entity_count = int(input()) 

    # get all entities
    monsters, my_heroes, enemy_heroes = get_entities(entity_count)

    # sort heroes to start with guards first
    if initial_heroes_position == 'top-left':
        my_heroes.sort(key=lambda hero: hero.id, reverse=True)
    else:
        my_heroes.sort(key=lambda hero: hero.id)

    ######### ACTION ###########################################################################################

    # do the first moves of all heroes
    if rounds_count < 7:
        for hero in my_heroes:
            hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']}"

    else:

        # rank monsters by threat level
        monsters_ranked = rank_monsters(monsters, base_x, base_y, enemy_heroes, threat_for=1)
        enemy_monsters_ranked = rank_monsters(monsters, enemy_base_x, enemy_base_y, enemy_heroes, threat_for=2)

        # get the hero of mine which is closest to the biggest threat to my base
        my_closest_hero_to_biggest_threat = -1
        if len(monsters_ranked) > 0:
            my_closest_hero_to_biggest_threat = get_closest_entity_to_entity(my_heroes, monsters_ranked[0])

        # get the hero of mine which is closest to the second biggest threat to my base
        my_closest_hero_to_sec_biggest_threat = -1
        if len(monsters_ranked) > 1:
            my_closest_hero_to_sec_biggest_threat = \
                get_closest_entity_to_entity([hero for hero in my_heroes if hero.id != my_closest_hero_to_biggest_threat], monsters_ranked[1])

        monsters_being_dealt_with = []
        winded_monsters = []

        for hero in my_heroes:

            # if this hero is the attacker
            if hero.id == 0 or hero.id == 5:

                # change next point of the attacker
                x, y = attacker_strategic_points[hero.id][i_attacker_strategic_points % len(attacker_strategic_points[hero.id])]
                heroes_strategic_points[hero.id] = {'x': x, 'y': y}
                enemy_monsters_ranked = [monster for monster in enemy_monsters_ranked if math.hypot(hero.x - monster.x, hero.y - monster.y) <= 2200]

                if move_towards_pushed_monster == True and ( \
                    (not enemy_monsters_ranked) or (enemy_monsters_ranked and pushed_monster_id not in [monster.id for monster in enemy_monsters_ranked]) \
                ):

                    x = pushed_monster_coords['x']
                    y = pushed_monster_coords['y']
                    x = (x - 600) if x > hero.x else (x + 600)
                    y = (y - 600) if y > hero.y else (y + 600)
                    hero.action = f"MOVE {x} {y} mv_to#({x},{y})"
                    enemy_base_hero_dist = math.hypot(hero.x - enemy_base_x, hero.y - enemy_base_y)
                    if (initial_heroes_position == 'top-left' and hero.x >= pushed_monster_coords['x'] and hero.y >= pushed_monster_coords['y']) \
                    or (initial_heroes_position == 'bottom-right' and hero.x <= pushed_monster_coords['x'] and hero.y <= pushed_monster_coords['y']) \
                    or (not enemy_monsters_ranked) \
                    or (enemy_monsters_ranked and enemy_monsters_ranked[0].id == pushed_monster_id) \
                    or enemy_base_hero_dist <= (400 + 2200):
                        move_towards_pushed_monster = False
                    else:
                        pushed_monster_coords['x'] += pushed_monster_velocity['vx']
                        pushed_monster_coords['y'] += pushed_monster_velocity['vy']

                # if there ARE threats to enemy's base
                elif enemy_monsters_ranked:

                    if move_towards_pushed_monster == True and pushed_monster_id in [monster.id for monster in enemy_monsters_ranked]:
                        move_towards_pushed_monster = False

                    # monster = sorted(enemy_monsters_ranked, key=lambda monster: math.hypot(hero.x - monster.x, hero.y - monster.y))[0]
                    monster = enemy_monsters_ranked[0]
                    next_move = None

                    hero_monster_dist = math.hypot(hero.x - monster.x, hero.y - monster.y)
                    enemy_base_monster_dist = math.hypot(enemy_base_x - monster.x, enemy_base_y - monster.y)
                    enemy_base_hero_dist = math.hypot(hero.x - enemy_base_x, hero.y - enemy_base_y)
                    number_of_monsters_in_hero_wind_range = get_number_of_monsters_in_hero_wind_range(monsters, hero)
                    number_of_monsters_in_hero_range = get_number_of_monsters_in_hero_range(monsters, hero)
                    number_of_unshielded_monsters_in_hero_wind_range = get_number_of_unshielded_monsters_in_hero_wind_range(monsters, hero)
                    closest_enemy_to_hero, closest_enemy_to_hero_dist = get_closest_enemy_to_hero(enemy_heroes, hero)
                    closest_enemy_to_hero_monster_dist = 9999999
                    closest_enemy_to_hero_base_dist = 9999999
                    if closest_enemy_to_hero:
                        closest_enemy_to_hero_monster_dist = math.hypot(closest_enemy_to_hero.x - monster.x, closest_enemy_to_hero.y - monster.y)
                        closest_enemy_to_hero_base_dist = math.hypot(closest_enemy_to_hero.x - enemy_base_x, closest_enemy_to_hero.y - enemy_base_y)

                    # shield the monster if it's really close and have enough health
                    if my_mana >= 10 and (not monster.shield_life) and (not monster.is_controlled) and monster.threat_for == 2 \
                    and hero_monster_dist <= 2200 \
                    and any([enemy_base_monster_dist <= 400 * i and monster.health >= 2 * i for i in range(1, 16)]):
                        hero.action = f"SPELL SHIELD {monster.id} shld_mnst#{monster.id}"
                        my_mana -= 10

                    # else, wind enemy out of the base if monsters are around none of them are in wind range (or they are but shielded)
                    elif my_mana >= 10 and closest_enemy_to_hero and not closest_enemy_to_hero.shield_life \
                    and closest_enemy_to_hero_dist <= 1280 \
                    and number_of_unshielded_monsters_in_hero_wind_range == 0 \
                    and monster.threat_for == 2 \
                    and enemy_base_monster_dist <= 6500:
                        hero.action = f"SPELL WIND {closest_enemy_to_hero.x - monster.vx * 2200} \
                            {closest_enemy_to_hero.y - monster.vy * 2200} wnd_out_enm#{closest_enemy_to_hero.id}"
                        my_mana -= 10
                        print(f"dist between hero and enemy {closest_enemy_to_hero.id}: {closest_enemy_to_hero_dist}", file=sys.stderr, flush=True)
                        print(f"number_of_monsters_in_hero_range: {number_of_monsters_in_hero_range}", file=sys.stderr, flush=True)
                        print(f"number_of_monsters_in_hero_wind_range: {number_of_monsters_in_hero_wind_range}", file=sys.stderr, flush=True)

                    # else, control enemy out of the base
                    elif my_mana >= 10 \
                    and closest_enemy_to_hero and (not closest_enemy_to_hero.shield_life) and closest_enemy_to_hero_dist <= 2200 \
                    and closest_enemy_to_hero_base_dist >= enemy_base_monster_dist \
                    and (closest_enemy_to_hero_monster_dist <= hero_monster_dist or closest_enemy_to_hero_monster_dist <= 2400):
                    # and ((closest_enemy_to_hero_dist > 800 * 2 and monster.health >= 2) or (closest_enemy_to_hero_dist <= 800 * 2 and monster.health >= 6)):
                        hero.action = f"SPELL CONTROL {closest_enemy_to_hero.id} {base_x} {base_y} ctrl_out_enm#{closest_enemy_to_hero.id}"
                        my_mana -= 10
                        if enemy_base_monster_dist < enemy_base_hero_dist:
                            move_towards_pushed_monster = True
                            pushed_monster_id = monster.id
                            pushed_monster_coords = {'x': monster.x + monster.vx, 'y': monster.y + monster.vy}
                            pushed_monster_velocity = {'vx': monster.vx, 'vy': monster.vy}
                            print(f"{monster.id}", file=sys.stderr, flush=True)

                    # else, control the monster into the base
                    elif my_mana >= 10 and (not monster.shield_life) and monster.threat_for != 2 and hero_monster_dist <= 2200 \
                    and (\
                            (monster.health * 100 >= enemy_base_monster_dist // 2) \
                            or (monster.health >= 8 and enemy_base_monster_dist > 6000) \
                        )\
                    and ((not closest_enemy_to_hero) or (closest_enemy_to_hero and closest_enemy_to_hero_monster_dist > hero_monster_dist)) \
                    and enemy_base_monster_dist > 5000:
                        hero.action = f"SPELL CONTROL {monster.id} {enemy_base_x} {enemy_base_y} ctrl_in_mnst#{monster.id}"
                        my_mana -= 10

                    # else, wind monster into the base
                    elif my_mana >= 10 and (not monster.shield_life) and hero_monster_dist <= 1280 \
                    and (
                        (not closest_enemy_to_hero) \
                        or (closest_enemy_to_hero and closest_enemy_to_hero_dist > 1280 + 800 and enemy_base_monster_dist <= 8000) \
                    ):
                        x = hero.x + (enemy_base_x - monster.x)
                        y = hero.y + (enemy_base_y - monster.y)
                        new_x = int(monster.x + ((monster.x - enemy_base_x) * -2200) / enemy_base_monster_dist)
                        new_y = int(monster.y + ((monster.y - enemy_base_y) * -2200) / enemy_base_monster_dist)
                        hero.action = f"SPELL WIND {x} {y} wnd_in_mnst#{monster.id}_to#({new_x},{new_y})"
                        print(f"{hero.id}", file=sys.stderr, flush=True)
                        my_mana -= 10
                        move_towards_pushed_monster = True
                        pushed_monster_id = monster.id
                        pushed_monster_coords = {'x': new_x, 'y': new_y}
                        pushed_monster_velocity = {'vx': monster.vx, 'vy': monster.vy}

                    # else, move to the monster... TO-DO: improve movement, if almost wind or control move less
                    elif not monster.shield_life and monster.threat_for == 2 \
                    and ((not closest_enemy_to_hero) or (closest_enemy_to_hero and closest_enemy_to_hero_monster_dist > 800)):
                        x = monster.x + monster.vx
                        y = monster.y + monster.vy
                        x = (x - 850) if x > hero.x else (x + 850)
                        y = (y - 850) if y > hero.y else (y + 850)
                        hero.action = f"MOVE {x} {y} flw_mnst#{monster.id}"

                        # DEBUG INFO
                        # print(f"{hero_monster_dist}", file=sys.stderr, flush=True)
                        # for i in range(1, 16):
                        #     print(enemy_base_monster_dist, 400 * i, file=sys.stderr, flush=True)
                        #     print(monster.health, 2 * i, file=sys.stderr, flush=True)
                        #     print("###", file=sys.stderr, flush=True)
                        # print([enemy_base_monster_dist <= 400 * i and monster.health >= 2 * i for i in range(1, 16)], file=sys.stderr, flush=True)

                    # else, move to next point
                    else:
                        hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#1"
                        i_attacker_strategic_points += 1

                # if there are no threats
                else: # TO-DO: go to parallel monsters

                    hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#3"
                    i_attacker_strategic_points += 1


            # if this hero is a guard
            else:

                # change next point of the guards
                if hero.id == 1 or hero.id == 3:
                    x, y = first_defender_strategic_points[hero.id][i_first_defender_strategic_points % len(first_defender_strategic_points[hero.id])]
                    heroes_strategic_points[hero.id] = {'x': x, 'y': y}
                elif hero.id == 2 or hero.id == 4:
                    x, y = second_defender_strategic_points[hero.id][i_second_defender_strategic_points % len(second_defender_strategic_points[hero.id])]
                    heroes_strategic_points[hero.id] = {'x': x, 'y': y}

                # if there ARE threats
                if monsters_ranked:

                    # if the current hero is the closest to the biggest threat
                    if ((hero.id == my_closest_hero_to_biggest_threat) \
                    or monsters_ranked[0].health > (math.hypot(monsters_ranked[0].x - base_x, monsters_ranked[0].y - base_y) / 400) * 2) \
                    and (guards_thresholds[hero.id]['min']['x'] <= monsters_ranked[0].x <= guards_thresholds[hero.id]['max']['x']) \
                    and (guards_thresholds[hero.id]['min']['y'] <= monsters_ranked[0].y <= guards_thresholds[hero.id]['max']['y']):
                        monster = monsters_ranked[0] # will later be added to monsters_being_dealt_with

                    # else, if a second biggest threat exists, and the closest hero to it is the current one
                    elif (hero.id == my_closest_hero_to_sec_biggest_threat) \
                    and (guards_thresholds[hero.id]['min']['x'] <= monsters_ranked[1].x <= guards_thresholds[hero.id]['max']['x']) \
                    and (guards_thresholds[hero.id]['min']['y'] <= monsters_ranked[1].y <= guards_thresholds[hero.id]['max']['y']):
                        monster = monsters_ranked[1] # will later be added to monsters_being_dealt_with

                    # if this hero is not closest to a threat
                    else:

                        # get the monsters closest to current hero
                        closest_monsters_to_hero = get_closest_monsters_to_hero_from_base(monsters, hero, base_x, base_y, max_monster_base_dist=8000)
                        
                        # get closest monster that's not already being dealt with
                        # if there is none, move to the strategic point
                        if len(closest_monsters_to_hero) >= 2:
                            if closest_monsters_to_hero[0][1].id not in monsters_being_dealt_with:
                                monster = closest_monsters_to_hero[0][1]
                            elif closest_monsters_to_hero[1][1].id not in monsters_being_dealt_with:
                                monster = closest_monsters_to_hero[1][1]
                            else:
                                hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#4"
                                if hero.id == 1 or hero.id == 3:
                                    i_first_defender_strategic_points += 1
                                elif hero.id == 2 or hero.id == 4:
                                    i_second_defender_strategic_points += 1
                                continue

                        elif len(closest_monsters_to_hero) == 1:
                            if closest_monsters_to_hero[0][1].id not in monsters_being_dealt_with:
                                monster = closest_monsters_to_hero[0][1]
                            else:
                                hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#5"
                                if hero.id == 1 or hero.id == 3:
                                    i_first_defender_strategic_points += 1
                                elif hero.id == 2 or hero.id == 4:
                                    i_second_defender_strategic_points += 1
                                continue

                        else:
                            hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#6"
                            if hero.id == 1 or hero.id == 3:
                                i_first_defender_strategic_points += 1
                            elif hero.id == 2 or hero.id == 4:
                                i_second_defender_strategic_points += 1
                            continue

                    hero_monster_dist = math.hypot(hero.x - monster.x, hero.y - monster.y)
                    base_monster_dist = math.hypot(base_x - monster.x, base_y - monster.y)
                    closest_enemy_to_hero = get_closest_enemy_to_monster(enemy_heroes, monster)
                    enemy_monster_dist = 9999999
                    if closest_enemy_to_hero:
                        enemy_monster_dist = closest_enemy_to_hero[0]

                    # cast a spell or move to monster
                    if my_mana >= 10 and (not monster.shield_life) and hero_monster_dist <= 1280 \
                    and ( \
                        (enemy_monster_dist <= 1280 and base_monster_dist <= (2200 + 400)) \
                        or (monster.health > (math.hypot(monster.x - base_x, monster.y - base_y) / 400) * 2) \
                    ) \
                    and monster.id not in winded_monsters:
                        hero.action = f"SPELL WIND {enemy_base_x} {enemy_base_y} wnd_out_mnst#{monster.id}"
                        winded_monsters.append(monster.id)
                        my_mana -= 10
                    else:
                        hero.action = f"MOVE {monster.x} {monster.y} flw_mnst#{monster.id}"

                    # add monster to list of monsters being currently dealt with
                    monsters_being_dealt_with.append(monster.id)

                # if there are no threats
                else: # TO-DO: go to parallel monsters

                    closest_enemy_to_base = get_closest_enemy_to_base(enemy_heroes, base_x, base_y)

                    if closest_enemy_to_base:
                        base_enemy_dist = math.hypot(base_x - closest_enemy_to_base[1].x, base_y - closest_enemy_to_base[1].y)
                        if base_enemy_dist <= 6500:
                            hero.action = f"MOVE {closest_enemy_to_base[1].x} {closest_enemy_to_base[1].y} flw_enm#{closest_enemy_to_base[1].id}"
                        else:
                            hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#7"
                            if hero.id == 1 or hero.id == 3:
                                i_first_defender_strategic_points += 1
                            elif hero.id == 2 or hero.id == 4:
                                i_second_defender_strategic_points += 1

                    else:
                        hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#8"
                        if hero.id == 1 or hero.id == 3:
                            i_first_defender_strategic_points += 1
                        elif hero.id == 2 or hero.id == 4:
                            i_second_defender_strategic_points += 1

    for hero in sorted(my_heroes, key=lambda hero: hero.id):
        print(hero.action)

    rounds_count += 1

# print("Debug messages...", file=sys.stderr, flush=True)