import random
import os
import time
import sys

class Player:
    def __init__(self, name, power, location, fuel):
        self.name = name
        self.power = power
        self.location = location
        self.fuel = fuel
        self.inventory = []
        self.health = 100
        self.max_health = 100  # Max health to prevent exceeding it
        self.defeated_boss = False
        self.level = 1
        self.experience = 0
    
    def collect_item(self, item):
        if len(self.inventory) >= 5:  # Limit to 5 items
            print("Your inventory is full! You can't pick up this item.")
        else:
            print(f"{self.name} collects {item.name}.")
            self.inventory.append(item)

    def display_inventory(self):
        print("\nYour Inventory:")
        if not self.inventory:
            print("  (Empty)")
        else:
            for item in self.inventory:
                print(f"  {item.name} - {item.effect_type.capitalize()} ({item.value})")

    def move(self, direction, planet_size):
        # Only update position without fuel loss
        if direction == "w" and self.location[1] > 0:
            self.location = (self.location[0], self.location[1] - 1)
        elif direction == "s" and self.location[1] < planet_size - 1:
            self.location = (self.location[0], self.location[1] + 1)
        elif direction == "a" and self.location[0] > 0:
            self.location = (self.location[0] - 1, self.location[1])
        elif direction == "d" and self.location[0] < planet_size - 1:
            self.location = (self.location[0] + 1, self.location[1])
        else:
            print("Invalid move or edge of planet reached.")



    def attack(self, enemy):
        print(f"{self.name} attacks with power {self.power}!")
        while enemy.health > 0:
            print(f"\nYour Health: {self.health} | {enemy.name}'s Health: {enemy.health}")
            print("Choose your action:")
            print("1: Normal Attack (reduced damage)")
            print("2: Power Blast (moderate damage, high risk)")
            print("3: Quick Strike (low damage, low risk)")
            print("4: Use an Item")

            choice = input("Enter 1, 2, 3, or 4: ")
            if choice == "1":
                damage = self.power // 2  # Reduced damage
            elif choice == "2":
                damage = int(self.power * 1.5)  # Moderate damage
            elif choice == "3":
                damage = self.power // 3  # Low damage
            elif choice == "4":
                self.use_item()
                continue  # Skip enemy's turn if an item is used
            else:
                print("Invalid choice. Using normal attack.")
                damage = self.power // 2

            enemy.take_damage(damage)
            if enemy.health <= 0:
                print(f"\n{enemy.name} has been defeated!")
                self.defeated_boss = True
                self.experience += 50  # Reward experience for defeating the boss
                self.level_up()  # Level up after defeating the boss
                break

            enemy.attack(self)

            if self.health <= 0:
                print("You have been defeated by the boss!")
                break


    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} takes {damage} damage, health is now {self.health}")
        if self.health < 0:
            self.health = 0  # Ensure health doesn't go below 0

    def level_up(self):
        if self.experience >= self.level * 100:
            self.level += 1
            self.power += 10
            self.health += 20
            if self.health > self.max_health:  # Prevent health from exceeding max limit
                self.health = self.max_health
            print(f"\n{self.name} leveled up! Level {self.level}. Power: {self.power}, Health: {self.health}")

    def use_item(self):
        if not self.inventory:
            print("Your inventory is empty! No items to use.")
            return

        print("\nYour Inventory:")
        for idx, item in enumerate(self.inventory, start=1):
            print(f"{idx}: {item.name} ({item.effect_type.capitalize()} - {item.value})")

        choice = input("Enter the number of the item you want to use: ")

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(self.inventory):
                item = self.inventory[choice_idx]
                item.use(self)
                self.inventory.pop(choice_idx)  # Remove the item after use
            else:
                print("Invalid selection. No item used.")
        except ValueError:
            print("Invalid input. Please enter a number.")



class Item:
    def __init__(self, name, effect_type, value, size=1):
        self.name = name
        self.effect_type = effect_type  # 'damage' or 'heal'
        self.value = value
        self.size = size  # Add size attribute

    def use(self, player):
        if self.effect_type == 'damage':
            print(f"{self.name} increases your attack damage by {self.value}!")
            player.power += self.value  # Increase the player's power (attack damage)
        elif self.effect_type == 'heal':
            print(f"{self.name} heals you for {self.value} health!")
            player.health += self.value
            if player.health > player.max_health:  # Ensure player doesn't exceed max health
                player.health = player.max_health
        else:
            print(f"{self.name} has no effect.")


class Enemy:
    def __init__(self, name, health, power, location):
        self.name = name
        self.health = health
        self.power = power
        self.location = location

    def attack(self, player):
        damage = random.randint(10, 20)
        print(f"{self.name} attacks {player.name} for {damage} damage!")
        player.take_damage(damage)

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} takes {damage} damage, health is now {self.health}")

class Planet:
    def __init__(self, name, size, location):
        self.name = name
        self.size = size
        self.location = location
        self.grid = self.generate_planet()
        self.boss = None
        self.boss_defeated = False

    def generate_planet(self):
        grid = [["empty" for _ in range(self.size)] for _ in range(self.size)]

        # Place 1-2 items randomly on the planet
        num_items = random.randint(1, 2)
        for _ in range(num_items):
            while True:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if grid[y][x] == "empty":  # Place only in empty cells
                    item_type = "heal" if random.random() < 0.5 else "damage"
                    item = Item(
                        name="Healing Potion" if item_type == "heal" else "Power Booster",
                        effect_type=item_type,
                        value=random.randint(10, 20),
                    )
                    grid[y][x] = item  # Store the Item object in the grid
                    break

        # Ensure 3–4 fuel spots
        num_fuel = random.randint(3, 4)
        for _ in range(num_fuel):
            while True:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if grid[y][x] == "empty":
                    grid[y][x] = "fuel"
                    break

        return grid

    def spawn_boss(self, player):
        while True:
            boss_x = random.randint(0, self.size - 1)
            boss_y = random.randint(0, self.size - 1)
            if (boss_x, boss_y) != player.location:
                break
        self.boss = Enemy(name="Planet Boss", health=100, power=25, location=(boss_x, boss_y))

    def display(self, player):
        print(f"\nVisual of {self.name}:")
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if (x, y) == player.location:
                    row += "P "
                elif self.boss and (x, y) == self.boss.location:
                    row += "B "
                elif self.grid[y][x] == 'empty':
                    row += ". "
                elif self.grid[y][x] == 'item':
                    row += "I "
                elif self.grid[y][x] == 'fuel':
                    row += "F "
                else:
                    row += ". "
            print(row)

    def interact(self, player):
        x, y = player.location
        current_cell = self.grid[y][x]

        if isinstance(current_cell, Item):  # Check if the cell contains an Item object
            print(f"You found an item at {player.location}! {current_cell.name} collected.")
            player.collect_item(current_cell)  # Use the player's collect_item method
            self.grid[y][x] = "empty"  # Mark the cell as empty after collection
        elif current_cell == 'fuel':
            fuel = random.randint(1, 5)
            player.fuel += fuel
            print(f"You found {fuel} units of fuel at {player.location}! Total fuel: {player.fuel}")
            self.grid[y][x] = 'empty'
        elif self.boss and self.boss.location == player.location:
            print(f"You encountered the boss {self.boss.name} at {player.location}!")
            player.attack(self.boss)
            if self.boss.health <= 0:
                print(f"\n{self.boss.name} has been defeated!")
                self.boss = None
                self.boss_defeated = True
                print("Planet Boss defeated. Moving on to other planets.")
        else:
            print("There is nothing to interact with here!")




class Universe:
    def __init__(self, size, player_fuel):
        self.size = size
        self.planets = self.generate_planets()
        self.player_fuel = player_fuel
        self.locked_planet = Planet(name="Locked Planet", size=6, location=(random.randint(0, size - 1), random.randint(0, size - 1)))
        self.visited_planets = 0
        self.defeated_bosses = 0
        self.locked_planet_unlocked = False

    def generate_planets(self):
        planets = []
        for i in range(self.size):
            planet_name = f"Planet {i + 1}"
            planet_size = random.randint(5, 7)
            location = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            planet = Planet(name=planet_name, size=planet_size, location=location)
            planets.append(planet)
        return planets

    def check_locked_planet(self):
        if self.defeated_bosses >= 3 and not self.locked_planet_unlocked:
            print("\nThe Locked Planet has been unlocked! You can now travel to it.")
            self.locked_planet_unlocked = True

    def spawn_locked_boss(self):
        self.boss = Enemy(
        name="Locked Planet Overlord",
        health=200,
        power=30,
        location=(random.randint(0, self.size - 1), random.randint(0, self.size - 1)),
    )

    def display(self, player):
        print("\nUniverse Map:")
        for y in range(self.size):
            row = ""
            for x in range(self.size):
                if self.locked_planet.location == (x, y):
                    if self.locked_planet_unlocked:
                        row += "L "
                    else:
                        row += "? "
                else:
                    planet_found = False
                    for planet in self.planets:
                        if planet.location == (x, y):
                            row += "P "
                            planet_found = True
                            break
                    if not planet_found:
                        row += ". "
            print(row)

    def show_planets(self, player):
        print("\nAvailable Planets on the Universe Map:")
        reachable = False  # To check if the player can reach any planet
        for idx, planet in enumerate(self.planets):
            distance = abs(planet.location[0] - player.location[0]) + abs(planet.location[1] - player.location[1])
            if player.fuel >= distance:
                print(f"{idx + 1}: {planet.name} at {planet.location} (Distance: {distance}) - Fuel Needed: {distance}")
                reachable = True
            else:
                print(f"{idx + 1}: {planet.name} at {planet.location} (Distance: {distance}) - Not enough fuel")
        if self.locked_planet_unlocked:
            distance = abs(self.locked_planet.location[0] - player.location[0]) + abs(self.locked_planet.location[1] - player.location[1])
            if player.fuel >= distance:
                print(f"L: {self.locked_planet.name} at {self.locked_planet.location} (Distance: {distance}) - Fuel Needed: {distance}")
                reachable = True
            else:
                print(f"L: {self.locked_planet.name} at {self.locked_planet.location} (Distance: {distance}) - Not enough fuel")
        return reachable  # Return whether any planets are reachable

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    name = input("Choose your name:\n")
    player = Player(name=name, power=100, location=(0, 0), fuel=10)
    universe = Universe(size=10, player_fuel=player.fuel)

    while True:
        clear_terminal()
        universe.display(player)
        
        # Check if there are reachable planets
        if not universe.show_planets(player):
            print("\nYou have no fuel left to visit any planets. GAME OVER!")
            break

        action = input("\nEnter the number of the planet you want to go to (e.g., 1) or 'L' for Locked Planet, or Q to quit: ").lower()
        if action == "q":
            print("Exiting the game.")
            break
        elif action.isdigit():
            planet_idx = int(action) - 1
            if 0 <= planet_idx < len(universe.planets):
                planet = universe.planets[planet_idx]
                distance = abs(planet.location[0] - player.location[0]) + abs(planet.location[1] - player.location[1])

                if player.fuel >= distance:
                    player.fuel -= distance
                    print(f"Travelling to {planet.name}...")
                    player.location = (0, 0)
                    planet.spawn_boss(player)

                    while not planet.boss_defeated:
                        clear_terminal()
                        planet.display(player)
                        direction = input("\nUse WASD to move around the planet: ").lower()
                        if direction in ["w", "a", "s", "d"]:
                            player.move(direction, planet.size)
                            planet.interact(player)
                        else:
                            print("Invalid input. Use WASD to move.")
                    universe.visited_planets += 1
                    universe.defeated_bosses += 1
                    universe.check_locked_planet()
                    print("\nYou have defeated the boss! You can now leave the planet.")
                    input("\nPress Enter to return to the universe.")
                else:
                    print("Not enough fuel to travel to that planet!")
                    input("\nPress Enter to continue...")
            else:
                print("Invalid planet number!")
                input("\nPress Enter to continue...")
        elif action == "l":
            if universe.locked_planet_unlocked:
                distance = abs(universe.locked_planet.location[0] - player.location[0]) + abs(universe.locked_planet.location[1] - player.location[1])
                if player.fuel >= distance:
                    player.fuel -= distance
                    print(f"Travelling to {universe.locked_planet.name}...")
                    player.location = (0, 0)
                    universe.locked_planet.spawn_boss(player)

                    while not universe.locked_planet.boss_defeated:
                        clear_terminal()
                        universe.locked_planet.display(player)
                        direction = input("\nUse WASD to move around the planet: ").lower()
                        if direction in ["w", "a", "s", "d"]:
                            player.move(direction, universe.locked_planet.size)
                            universe.locked_planet.interact(player)
                        else:
                            print("Invalid input. Use WASD to move.")
                    universe.visited_planets += 1
                    universe.defeated_bosses += 1
                    print("\nYou have defeated the Locked Planet's boss! You can now leave.")
                    input("\nPress Enter to return to the universe.")
                else:
                    print("Not enough fuel to travel to the Locked Planet!")
                    input("\nPress Enter to continue...")
            else:
                print("The Locked Planet is still locked. Defeat more bosses to unlock it!")
                input("\nPress Enter to continue...")
        else:
            print("Invalid option. Please enter a valid planet number, 'L' for Locked Planet, or 'Q' to quit.")
            input("\nPress Enter to continue...")

color_codes = {
    "RESET": "\033[0m",
    "RED": "\033[31m",
    "YELLOW": "\033[33m",
    "BLUE": "\033[34m",
    "GREEN": "\033[32m",
    "CYAN": "\033[36m",
    "WHITE": "\033[37m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m"
}

def apply_color(text, color):
    return f"{color_codes[color]}{text}{color_codes['RESET']}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, delay=0.05, newline=True, color="RESET", effect_word=None, effect_color="CYAN"):
    for char in text:
        if effect_word and effect_word.lower() in char.lower():
            char = apply_color(char, effect_color)
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()

def color_specific_words(sentence, color_map):
    words = sentence.split()
    colored_words = []
    
    for word in words:
        for target_word, color in color_map.items():
            if target_word.lower() in word.lower():
                word = apply_color(word, color)
        colored_words.append(word)
    
    return ' '.join(colored_words)

def generate_stars(width, height, star_count):
    stars = []
    for _ in range(star_count):
        x = random.randint(1, width)
        y = random.randint(1, height)
        stars.append([x, y, random.random()])
    return stars

def display_blinking_stars(width, height, stars):
    for star in stars:
        if random.random() < star[2]:
            print(f"\033[{star[1]};{star[0]}H*", end="")
        else:
            print(f"\033[{star[1]};{star[0]}H ", end="")
    time.sleep(0.1)

def spaceship_flying(width, height, spaceship, stars):
    spaceship_width = max(len(line) for line in spaceship.splitlines())
    spaceship_height = len(spaceship.splitlines())

    start_x = (width - spaceship_width) // 2
    start_y = (height - spaceship_height) // 2

    for x in range(start_x, width - spaceship_width, 2):
        clear_screen()
        display_blinking_stars(width, height, stars)
        print(f"\033[{start_y};{x}H{spaceship}")
        time.sleep(0.1)

def introduction():
    clear_screen()

    sentence1 = "The Earth is in chaos."
    sentence2 = "A catastrophic event is unfolding, and humanity's end is imminent."
    sentence3 = "In the nick of time, you escape aboard the spaceship you've secretly built."
    sentence5 = "Your mission: explore unknown planets, gather resources, and survive."
    sentence6 = "The journey begins..."

    color_map = {
        "chaos": "RED",
        "catastrophic": "YELLOW",
        "event": "GREEN",
        "spaceship": "BLUE",
        "survive": "CYAN",
        "space": "WHITE"
    }

    sentence1_colored = color_specific_words(sentence1, color_map)
    sentence2_colored = color_specific_words(sentence2, color_map)
    sentence3_colored = color_specific_words(sentence3, color_map)
    sentence5_colored = color_specific_words(sentence5, color_map)
    sentence6_colored = color_specific_words(sentence6, color_map)

    width = 80
    height = 20
    stars = generate_stars(width, height, 100)

    spaceship = """
    /\  
    ||  
    ||  
   /||\ 
  /:||:\\
  |:||:|  
  |/||\|  
    **  
    **  
    """

    type_text(sentence1_colored, color="RED", delay=0.05)
    time.sleep(2)
    clear_screen()
    type_text(sentence2_colored, color="YELLOW", delay=0.05)
    time.sleep(3)
    clear_screen()
    type_text(sentence3_colored, color="BLUE", delay=0.05)
    time.sleep(3)
    clear_screen()
    type_text(sentence5_colored, color="CYAN", delay=0.05)
    time.sleep(3)
    clear_screen()
    type_text(sentence6_colored, color="CYAN", delay=0.05)
    time.sleep(2)

    type_text("\033[36m...in the quiet void of space.\033[0m", delay=0.05)
    time.sleep(2)

    spaceship_flying(width, height, spaceship, stars)

introduction()
clear_screen()

if __name__ == "__main__":
    main()
