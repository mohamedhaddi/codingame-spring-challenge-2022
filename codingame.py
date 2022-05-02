"""
Disclaimer: I'm not proud of this code, it's unclean and full of hardcoding (some of it I did at last minute) and I didn't focus on making it clean, so don't judge T_T
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
        # if threat_for == 1 and monster.threat_for == threat_for:
        if monster.threat_for == threat_for:
            threat_level *= 2
        if threat_for == 1:
            for enemy in enemy_heroes:
                base_enemy_dist = math.hypot(base_x - enemy.x, base_y - enemy.y)
                if base_enemy_dist <= 7000:
                    monster_enemy_dist = math.hypot(monster.x - enemy.x, monster.y - enemy.y)
                    if monster_enemy_dist <= 1280 + 800:
                        threat_level *= 2
        #    threat_level += sum(math.hypot(monster.x - enemy_hero.x, monster.y - enemy_hero.y) for enemy_hero in enemy_heroes)
        monsters_ranked[threat_level] = monster
    monsters_ranked = list(dict(sorted(monsters_ranked.items(), reverse=True)).values())
    return monsters_ranked

def get_my_closest_hero_to_biggest_threat(monsters_ranked, my_heroes):
    if len(monsters_ranked) >= 1:
        dists_to_biggest_threat = []
        for hero in my_heroes:
            dist = math.hypot(hero.x - monsters_ranked[0].x, hero.y - monsters_ranked[0].y)
            dists_to_biggest_threat.append((dist, hero.id))
        closest_hero_to_biggest_threat = min(dists_to_biggest_threat)[1]
        return closest_hero_to_biggest_threat
    return -1

def get_my_closest_hero_to_second_biggest_threat(monsters_ranked, my_heroes, closest_hero_to_biggest_threat):
    if len(monsters_ranked) >= 2:
        dists_to_sec_biggest_threat = []
        for hero in my_heroes:
            dist = math.hypot(hero.x - monsters_ranked[1].x, hero.y - monsters_ranked[1].y)
            if hero.id != closest_hero_to_biggest_threat:
                dists_to_sec_biggest_threat.append((dist, hero.id))
        closest_hero_to_sec_biggest_threat = min(dists_to_sec_biggest_threat)[1]
        return closest_hero_to_sec_biggest_threat
    return -1

def get_nearest_monsters_to_base(monsters, base_x, base_y, max_monster_base_dist):
    nearest_monsters_to_base = []
    for monster in monsters:
        monster_base_dist = math.hypot(base_x - monster.x, base_y - monster.y)
        if monster_base_dist <= max_monster_base_dist:
            nearest_monsters_to_base.append((monster_base_dist, monster))
    nearest_monsters_to_base = sorted(nearest_monsters_to_base, key=lambda x: x[0])
    return nearest_monsters_to_base

def get_nearest_enemy_to_base(enemy_heroes, base_x, base_y):
    nearest_enemy_to_base = None
    nearest_enemy_to_base_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_base_dist = math.hypot(base_x - enemy_hero.x, base_y - enemy_hero.y)
        if enemy_base_dist < nearest_enemy_to_base_dist:
            nearest_enemy_to_base_dist = enemy_base_dist
            nearest_enemy_to_base = (enemy_base_dist, enemy_hero)
    return nearest_enemy_to_base

def get_nearest_monsters_to_hero_from_base(monsters, hero, base_x, base_y, max_monster_base_dist):
    nearest_monsters_to_base = get_nearest_monsters_to_base(monsters, base_x, base_y, max_monster_base_dist)
    nearest_monsters_to_hero = []
    for monster in nearest_monsters_to_base:
        monster_hero_dist = math.hypot(hero.x - monster[1].x, hero.y - monster[1].y)
        if hero.id == 0 or hero.id == 5:
            nearest_monsters_to_hero.append((monster_hero_dist, monster[1]))
        elif (guards_thresholds[hero.id]['min']['x'] <= monster[1].x <= guards_thresholds[hero.id]['max']['x']) and \
           (guards_thresholds[hero.id]['min']['y'] <= monster[1].y <= guards_thresholds[hero.id]['max']['y']):
            nearest_monsters_to_hero.append((monster_hero_dist, monster[1]))
        #if monster_hero_dist <= 2000:
        #    nearest_monsters_to_hero.append((monster_hero_dist, monster[1]))
    nearest_monsters_to_hero = sorted(nearest_monsters_to_hero, key=lambda x: x[0])
    return nearest_monsters_to_hero

def get_closest_enemy_to_their_base(enemy_heroes, base_x, base_y):
    closest_enemy_to_their_base = None
    closest_enemy_to_their_base_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_base_dist = math.hypot(base_x - enemy_hero.x, base_y - enemy_hero.y)
        if enemy_base_dist < closest_enemy_to_their_base_dist:
            closest_enemy_to_their_base_dist = enemy_base_dist
            closest_enemy_to_their_base = (enemy_base_dist, enemy_hero)
    return closest_enemy_to_their_base

def get_nearest_enemy_to_hero(enemy_heroes, hero):
    nearest_enemy_to_hero = None
    nearest_enemy_to_hero_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_hero_dist = math.hypot(hero.x - enemy_hero.x, hero.y - enemy_hero.y)
        if enemy_hero_dist < nearest_enemy_to_hero_dist:
            nearest_enemy_to_hero_dist = enemy_hero_dist
            nearest_enemy_to_hero = (enemy_hero_dist, enemy_hero)
    return nearest_enemy_to_hero

def get_nearest_enemy_to_monster(enemy_heroes, monster):
    nearest_enemy_to_monster = None
    nearest_enemy_to_monster_dist = 9999999
    for enemy_hero in enemy_heroes:
        enemy_monster_dist = math.hypot(monster.x - enemy_hero.x, monster.y - enemy_hero.y)
        if enemy_monster_dist < nearest_enemy_to_monster_dist:
            nearest_enemy_to_monster_dist = enemy_monster_dist
            nearest_enemy_to_monster = (enemy_monster_dist, enemy_hero)
    return nearest_enemy_to_monster

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

base_x, base_y = [int(i) for i in input().split()]
e_base_x = 17630 - base_x
e_base_y = 9000 - base_y
heroes_per_player = int(input()) # Always 3
initial_heroes_position = 'top-left' if base_x < 9000 else 'bottom-right'
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
        (e_base_x - 8750, e_base_y - 250),
        (e_base_x - 7750, e_base_y - 1250),
        (e_base_x - 6750, e_base_y - 2250),
        (e_base_x - 5750, e_base_y - 3250),
        (e_base_x - 4750, e_base_y - 4250),
        (e_base_x - 3750, e_base_y - 5250),
        (e_base_x - 2750, e_base_y - 6250),
        (e_base_x - 3750, e_base_y - 5250),
        (e_base_x - 4750, e_base_y - 4250),
        (e_base_x - 5750, e_base_y - 3250),
        (e_base_x - 6750, e_base_y - 2250),
        (e_base_x - 7750, e_base_y - 1250),
    ],
    5: [
        (8750, 250),
        (7750, 1250),
        (6750, 2250),
        (5750, 3250),
        (4750, 4250),
        (3750, 5250),
        (2750, 6250),
        (3750, 5250),
        (4750, 4250),
        (5750, 3250),
        (6750, 2250),
        (7750, 1250),
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
pushed_monster_coords = {'x': 0, 'y': 0}

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

    # rank monsters by threat level
    monsters_ranked = rank_monsters(monsters, base_x, base_y, enemy_heroes, threat_for=1)
    e_monsters_ranked = rank_monsters(monsters, e_base_x, e_base_y, enemy_heroes, threat_for=2)
    print(f"e_monsters_ranked:", file=sys.stderr, flush=True)
    for monster in e_monsters_ranked:
        print(f"monster.id: {monster.id}", file=sys.stderr, flush=True)

    ######### ACTION ##########################################################################

    # do the first moves of all heroes
    if rounds_count < 7:
        for hero in my_heroes:
            hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']}"

    else:

        # get the hero of mine which is closest to the biggest threat to my base
        closest_hero_to_biggest_threat = get_my_closest_hero_to_biggest_threat(monsters_ranked, my_heroes)

        # get the hero of mine which is closest to the second biggest threat to my base
        closest_hero_to_sec_biggest_threat = get_my_closest_hero_to_second_biggest_threat(monsters_ranked, my_heroes, closest_hero_to_biggest_threat)

        monsters_being_dealt_with = []
        winded_monsters = []

        for hero in my_heroes:

            # if this hero is the attacker
            if hero.id == 0 or hero.id == 5:

                # change next point of the attacker
                x, y = attacker_strategic_points[hero.id][i_attacker_strategic_points % len(attacker_strategic_points[hero.id])]
                heroes_strategic_points[hero.id] = {'x': x, 'y': y}
                e_monsters_ranked = [monster for monster in e_monsters_ranked if math.hypot(hero.x - monster.x, hero.y - monster.y) <= 2200]

                if move_towards_pushed_monster:
                        hero.action = f"MOVE {pushed_monster_coords['x']} {pushed_monster_coords['y']} mv_to#({pushed_monster_coords['x']},{pushed_monster_coords['y']})"
                        e_base_hero_dist = math.hypot(hero.x - e_base_x, hero.y - e_base_y)
                        if e_base_hero_dist <= (400 + 2200) \
                        or (e_monsters_ranked and math.hypot(hero.x - e_monsters_ranked[0].x, hero.y - e_monsters_ranked[0].y) <= 2200): # removing this makes it better?
                            move_towards_pushed_monster = False

                # if there ARE threats to enemy's base
                elif e_monsters_ranked:

                    # monster = sorted(e_monsters_ranked, key=lambda monster: math.hypot(hero.x - monster.x, hero.y - monster.y))[0]
                    monster = e_monsters_ranked[0]
                    next_move = None

                    hero_monster_dist = math.hypot(hero.x - monster.x, hero.y - monster.y)
                    base_monster_dist = math.hypot(e_base_x - monster.x, e_base_y - monster.y)
                    print(f"base_monster_dist: {base_monster_dist}", file=sys.stderr, flush=True)
                    e_base_hero_dist = math.hypot(hero.x - e_base_x, hero.y - e_base_y)
                    closest_enemy_to_their_base = get_closest_enemy_to_their_base(enemy_heroes, e_base_x, e_base_y)
                    nearest_enemy_to_hero = get_nearest_enemy_to_hero(enemy_heroes, hero)
                    number_of_monsters_in_hero_wind_range = get_number_of_monsters_in_hero_wind_range(monsters, hero)
                    number_of_monsters_in_hero_range = get_number_of_monsters_in_hero_range(monsters, hero)

                    # shield the monster if it's really close and have enough health
                    if my_mana >= 10 and (not monster.shield_life) and (not monster.is_controlled) and monster.threat_for == 2 \
                    and hero_monster_dist <= 2200 \
                    and (
                        (base_monster_dist <= 400 and monster.health >= 2) \
                        or (base_monster_dist <= 800 and monster.health >= 4) \
                        or (base_monster_dist <= 1200 and monster.health >= 6) \
                        or (base_monster_dist <= 1600 and monster.health >= 8) \
                        or (base_monster_dist <= 2000 and monster.health >= 10) \
                        or (base_monster_dist <= 2400 and monster.health >= 12) \
                        or (base_monster_dist <= 2800 and monster.health >= 14) \
                        or (base_monster_dist <= 3200 and monster.health >= 16) \
                        or (base_monster_dist <= 3600 and monster.health >= 18) \
                        or (base_monster_dist <= 4000 and monster.health >= 20) \
                        or (base_monster_dist <= 4400 and monster.health >= 22) \
                        or (base_monster_dist <= 4800 and monster.health >= 24) \
                        or (base_monster_dist <= 5200 and monster.health >= 26) \
                        or (base_monster_dist <= 5600 and monster.health >= 28) \
                        or (base_monster_dist <= 6000 and monster.health >= 30) \
                    ):
                            hero.action = f"SPELL SHIELD {monster.id} shld_mnst#{monster.id}"
                            my_mana -= 10
                    # else, wind enemy out of the base if monsters are around none of them are in wind range (or they are but shielded)
                    elif my_mana >= 20 and nearest_enemy_to_hero and not nearest_enemy_to_hero[1].shield_life \
                    and math.hypot(nearest_enemy_to_hero[1].x - hero.x, nearest_enemy_to_hero[1].y - hero.y) + 800 <= 1280 \
                    and number_of_monsters_in_hero_range > 0 \
                    and number_of_monsters_in_hero_wind_range < number_of_monsters_in_hero_range \
                    and monster.threat_for == 2 \
                    and base_monster_dist <= 6500:
                            hero.action = f"SPELL WIND {nearest_enemy_to_hero[1].x - monster.vx * 2200} \
                            {nearest_enemy_to_hero[1].y - monster.vy * 2200} \
                            wnd_out_enm#{nearest_enemy_to_hero[1].id}"
                            my_mana -= 10
                            x = monster.x + monster.vx
                            y = monster.y + monster.vy
                            if x > hero.x:
                                x -= 850
                            else:
                                x += 850
                            if y > hero.y:
                                y -= 850
                            else:
                                y += 850
                            move_towards_pushed_monster = True
                            pushed_monster_coords = {'x': x, 'y': y}
                    # else, control enemy out of the base
                    elif my_mana >= 20 and nearest_enemy_to_hero and not nearest_enemy_to_hero[1].shield_life \
                    and math.hypot(nearest_enemy_to_hero[1].x - hero.x, nearest_enemy_to_hero[1].y - hero.y) <= 2200 \
                    and base_monster_dist <= 6500 \
                    and ( \
                        (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) > 800 * 2 and monster.health >= 2) \
                        or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 2 and monster.health >= 6) \
                    ):
                    # and monster.threat_for == 2 \
                    # and ( \
                    #     (monster.threat_for == 2 and ( \
                    #         (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) > 800 * 2 and monster.health >= 2) \
                    #         or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 2 and monster.health >= 4) \
                    #         or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 3 and monster.health >= 8) \
                    #         or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 4 and monster.health >= 10) \
                    #         or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 5 and monster.health >= 12) \
                    #         or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 6 and monster.health >= 14) \
                    #         or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 7 and monster.health >= 16) \
                    #     )) \
                    #     or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 2 and monster.health >= 6) \
                    # ):
                            hero.action = f"SPELL CONTROL {nearest_enemy_to_hero[1].id} {base_x} {base_y} ctrl_out_enm#{nearest_enemy_to_hero[1].id}"
                            my_mana -= 10
                            x = monster.x + monster.vx
                            y = monster.y + monster.vy
                            if x > hero.x:
                                x -= 850
                            else:
                                x += 850
                            if y > hero.y:
                                y -= 850
                            else:
                                y += 850
                            move_towards_pushed_monster = True
                            pushed_monster_coords = {'x': x, 'y': y}
                    # else, wind monster into the base
                    elif my_mana >= 20 and (not monster.shield_life) and hero_monster_dist <= 1280 \
                    and base_monster_dist <= 8000 \
                    and nearest_enemy_to_hero and math.hypot(nearest_enemy_to_hero[1].x - hero.x, nearest_enemy_to_hero[1].y - hero.y) > 1280:
                            # x = e_base_x
                            # y = e_base_y
                            # if hero.y >= 5500:
                            #   x = hero.x + (e_base_x - monster.x)
                            # else:
                            #   y = hero.y + (e_base_y - monster.y)
                            x = hero.x + (e_base_x - monster.x)
                            y = hero.y + (e_base_y - monster.y)
                            new_x = int(monster.x + ((monster.x - e_base_x) * -2200) / base_monster_dist)
                            new_y = int(monster.y + ((monster.y - e_base_y) * -2200) / base_monster_dist)
                            hero.action = f"SPELL WIND {x} {y} wnd_in_mnst#{monster.id}_to#({new_x},{new_y})"
                            move_towards_pushed_monster = True
                            print('pushed to: ', new_x, new_y, file=sys.stderr, flush=True)
                            if new_x > hero.x:
                                new_x -= 600
                            else:
                                new_x += 600
                            if new_y > hero.y:
                                new_y -= 600
                            else:
                                new_y += 600
                            # if initial_heroes_position == 'top-left':
                            #     if new_x > hero.x:
                            #         new_x -= 600
                            #     else:
                            #         new_x += 600
                            #     if new_y > hero.y:
                            #         new_y -= 600
                            #     else:
                            #         new_y += 600
                            # else:
                            #     if new_x > hero.x:
                            #         new_x += 600
                            #     else:
                            #         new_x -= 600
                            #     if new_y > hero.y:
                            #         new_y += 600
                            #     else:
                            #         new_y -= 600
                            print('going to: ', new_x, new_y, file=sys.stderr, flush=True)
                            pushed_monster_coords = {'x': new_x, 'y': new_y}
                            my_mana -= 10
                    # else, control the monster into the base
                    elif my_mana >= 20 and (not monster.shield_life) and monster.threat_for != 2 and hero_monster_dist <= 2200 \
                    and nearest_enemy_to_hero and ( \
                        (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 2 and monster.health >= 6) \
                        or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 3 and monster.health >= 8) \
                        or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 4 and monster.health >= 10) \
                        or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 5 and monster.health >= 12) \
                        or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 6 and monster.health >= 14) \
                        or (math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) <= 800 * 7 and monster.health >= 16) \
                    ) \
                    and hero_monster_dist >= math.hypot(nearest_enemy_to_hero[1].x - monster.x, nearest_enemy_to_hero[1].y - monster.y) \
                    and 6500 >= base_monster_dist > 5000:
                    # and ( \
                    #     ( \
                    #         initial_heroes_position == 'top-left' \
                    #         and ((nearest_enemy_to_hero[1].x < (monster.x - 800) and nearest_enemy_to_hero[1].y < (monster.y - 800)) \
                    #         or (nearest_enemy_to_hero[1].x < (monster.x - 800) and nearest_enemy_to_hero[1].y == monster.y) \
                    #         or (nearest_enemy_to_hero[1].x == monster.x and nearest_enemy_to_hero[1].y < (monster.y - 800))) \
                    #     ) \
                    #     or \
                    #     ( \
                    #         initial_heroes_position == 'bottom-right' \
                    #         and ((nearest_enemy_to_hero[1].x > (monster.x + 800) and nearest_enemy_to_hero[1].y > (monster.y + 800)) \
                    #         or (nearest_enemy_to_hero[1].x > (monster.x + 800) and nearest_enemy_to_hero[1].y == monster.y) \
                    #         or (nearest_enemy_to_hero[1].x == monster.x and nearest_enemy_to_hero[1].y > (monster.y + 800))) \
                    #     ) \
                    # ) \
                    # and nearest_enemy_to_hero and math.hypot(nearest_enemy_to_hero[1].x - hero.x, nearest_enemy_to_hero[1].y - hero.y) > 800 * 2 \
                    # and monster.health >= 10:
                            hero.action = f"SPELL CONTROL {monster.id} {e_base_x} {e_base_y} ctrl_in_mnst#{monster.id}"
                            my_mana -= 10
                            x = monster.x + monster.vx
                            y = monster.y + monster.vy
                            if x > hero.x:
                                x -= 850
                            else:
                                x += 850
                            if y > hero.y:
                                y -= 850
                            else:
                                y += 850
                            move_towards_pushed_monster = True
                            pushed_monster_coords = {'x': x, 'y': y}
                    # else, move to the monster... TO-DO: improve movement, if almost wind or control move less
                    elif base_monster_dist <= 9000 and not monster.shield_life: 
                            x = monster.x + monster.vx
                            y = monster.y + monster.vy
                            if x > hero.x:
                                x -= 850
                            else:
                                x += 850
                            if y > hero.y:
                                y -= 850
                            else:
                                y += 850
                            # if initial_heroes_position == 'top-left':
                            #     if x > hero.x:
                            #         x -= 850
                            #     else:
                            #         x += 850
                            #     if y > hero.y:
                            #         y -= 850
                            #     else:
                            #         y += 850
                            # else:
                            #     if x > hero.x:
                            #         x += 850
                            #     else:
                            #         x -= 850
                            #     if y > hero.y:
                            #         y += 850
                            #     else:
                            #         y -= 850
                            hero.action = f"MOVE {x} {y} flw_mnst#{monster.id}"

                            # hero_monster_dist = math.hypot(hero.x - monster.x, hero.y - monster.y) + 1
                            # hero_to_monster_vector = {'x': hero.x - monster.x, 'y': hero.y - monster.y}
                            # direction = {
                            #     'x': int(hero_to_monster_vector['x'] / hero_monster_dist),
                            #     'y': int(hero_to_monster_vector['y'] / hero_monster_dist)
                            # }
                            # desired_distance = int(hero_monster_dist)
                            # x = monster.x + direction['x'] * desired_distance
                            # y = monster.y + direction['y'] * desired_distance
                            # hero.action = f"MOVE {x} {y} flw_mnst#{monster.id}"

                            # direction_vector = {
                            #     'vx': monster.x + monster.vx - hero.x / hero_monster_dist,
                            #     'vy': monster.y + monster.vy - hero.y / hero_monster_dist
                            # }
                            # movement = hero_monster_dist - 2200
                            # x = hero.x + round(direction_vector['vx'] * movement)
                            # y = hero.y + round(direction_vector['vy'] * movement)
                    # else, move to next point
                    else:
                            hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#1"
                            i_attacker_strategic_points += 1

                # if there are no threats
                else: # TO-DO: go to parallel monsters

                    nearest_enemy_to_hero = get_nearest_enemy_to_hero(enemy_heroes, hero)

                    if nearest_enemy_to_hero:
                        e_base_enemy_dist = math.hypot(e_base_x - nearest_enemy_to_hero[1].x, e_base_y - nearest_enemy_to_hero[1].y)
                        if e_base_enemy_dist <= 9000:
                            hero.action = f"MOVE {nearest_enemy_to_hero[1].x} {nearest_enemy_to_hero[1].y} flw_enm#{nearest_enemy_to_hero[1].id}"
                        else:
                            hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#2"
                            i_attacker_strategic_points += 1

                    else:
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
                    if ((hero.id == closest_hero_to_biggest_threat) \
                    or monsters_ranked[0].health > (math.hypot(monsters_ranked[0].x - base_x, monsters_ranked[0].y - base_y)/400)*2) \
                    and (guards_thresholds[hero.id]['min']['x'] <= monsters_ranked[0].x <= guards_thresholds[hero.id]['max']['x']) \
                    and (guards_thresholds[hero.id]['min']['y'] <= monsters_ranked[0].y <= guards_thresholds[hero.id]['max']['y']):
                        monster = monsters_ranked[0] # will later be added to monsters_being_dealt_with
                    # else, if a second biggest threat exists, and the closest hero to it is the current one
                    elif (hero.id == closest_hero_to_sec_biggest_threat) \
                    and (guards_thresholds[hero.id]['min']['x'] <= monsters_ranked[1].x <= guards_thresholds[hero.id]['max']['x']) \
                    and (guards_thresholds[hero.id]['min']['y'] <= monsters_ranked[1].y <= guards_thresholds[hero.id]['max']['y']):
                        monster = monsters_ranked[1] # will later be added to monsters_being_dealt_with
                    # if this hero is not closest to a threat
                    else:

                        # get the monsters nearest to current hero
                        nearest_monsters_to_hero = get_nearest_monsters_to_hero_from_base(monsters, hero, base_x, base_y, max_monster_base_dist=8000)
                        
                        # get nearest monster that's not already being dealt with
                        # if there is none, move to the strategic point
                        if len(nearest_monsters_to_hero) >= 2:

                            if nearest_monsters_to_hero[0][1].id not in monsters_being_dealt_with:
                                monster = nearest_monsters_to_hero[0][1]
                            elif nearest_monsters_to_hero[1][1].id not in monsters_being_dealt_with:
                                monster = nearest_monsters_to_hero[1][1]
                            else:
                                hero.action = f"MOVE {heroes_strategic_points[hero.id]['x']} {heroes_strategic_points[hero.id]['y']} nxt_pt#4"
                                if hero.id == 1 or hero.id == 3:
                                    i_first_defender_strategic_points += 1
                                elif hero.id == 2 or hero.id == 4:
                                    i_second_defender_strategic_points += 1
                                continue

                        elif len(nearest_monsters_to_hero) == 1:

                            if nearest_monsters_to_hero[0][1].id not in monsters_being_dealt_with:
                                monster = nearest_monsters_to_hero[0][1]
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
                    nearest_enemy_to_hero = get_nearest_enemy_to_monster(enemy_heroes, monster)
                    enemy_monster_dist = 9999999
                    if nearest_enemy_to_hero:
                        enemy_monster_dist = nearest_enemy_to_hero[0]

                    # cast a spell or move to monster
                    if my_mana >= 10 and (not monster.shield_life) and hero_monster_dist <= 1280 \
                    and ( \
                        (enemy_monster_dist <= 1280 and base_monster_dist <= (2200 + 400)) \
                        or (monster.health > (math.hypot(monster.x - base_x, monster.y - base_y)/400)*2) \
                    ) \
                    and monster.id not in winded_monsters:
                        hero.action = f"SPELL WIND {e_base_x} {e_base_y} wnd_out_mnst#{monster.id}"
                        winded_monsters.append(monster.id)
                        my_mana -= 10
                    else:
                        hero.action = f"MOVE {monster.x} {monster.y} flw_mnst#{monster.id}"

                    # add monster to list of monsters being currently dealt with
                    monsters_being_dealt_with.append(monster.id)

                # if there are no threats
                else: # TO-DO: go to parallel monsters

                    nearest_enemy_to_base = get_nearest_enemy_to_base(enemy_heroes, base_x, base_y)

                    if nearest_enemy_to_base:
                        base_enemy_dist = math.hypot(base_x - nearest_enemy_to_base[1].x, base_y - nearest_enemy_to_base[1].y)
                        if base_enemy_dist <= 6500:
                            hero.action = f"MOVE {nearest_enemy_to_base[1].x} {nearest_enemy_to_base[1].y} flw_enm#{nearest_enemy_to_base[1].id}"
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

    for hero in my_heroes:
        print(hero.action)

    rounds_count += 1

# print("Debug messages...", file=sys.stderr, flush=True)
