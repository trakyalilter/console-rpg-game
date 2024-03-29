import asyncio
import random
from colorama import Fore, Back, Style
import os
default_role_stats = {
    "Warrior.txt": "150,10,5,25,0,100,1,0,0",  # Example stats for Warrior
    "Archer.txt": "100,15,10,20,0,100,1,0,0",  # Example stats for Archer
    "Mage.txt": "80,20,5,15,0,100,1,0,0",      # Example stats for Mage
}
skill_trees = {
    "Warrior": {
        "Power Strike": {"cost": 1, "description": "A powerful attack dealing 150% damage", "level": 0, "max_level": 3},
        "Fortitude": {"cost": 1, "description": "Increases HP by 20%", "level": 0, "max_level": 5},
    },
    "Archer": {
        "Rapid Fire": {"cost": 1, "description": "Shoot two arrows at once", "level": 0, "max_level": 3},
        "Eagle Eye": {"cost": 1, "description": "Increases critical hit chance", "level": 0, "max_level": 5},
    },
    "Mage": {
        "Fireball": {"cost": 1, "description": "Cast a fireball that deals area damage", "level": 0, "max_level": 3},
        "Mana Shield": {"cost": 1, "description": "Absorbs damage based on your MP", "level": 0, "max_level": 5},
    }
}
class Oyun:
    def __init__(self):
        self.create_role_files_if_missing()
        self.character_stats = {}
        self.goblin_stats = {}
        self.goblin_leader_stats = {}
        self.load_stats()
        self.load_inventory()
        self.load_skills()

    def create_role_files_if_missing(self):
        for role_file, stats in default_role_stats.items():
            if not os.path.exists(role_file):
                with open(role_file, 'w', encoding='utf-8') as file:
                    file.write(stats)
    def load_inventory(self):
        self.inventory = {}
        with open('inventory.txt', 'r', encoding='utf-8') as inv_file:
            for line in inv_file:
                item, details = line.strip().split(':')
                details = details.split(',')
                self.inventory[item] = {'Name': details[0], 'Price': int(details[1]), 'Bonus': int(details[2])}

    def load_stats(self):
        with open('Karakter.txt', 'r', encoding='utf-8') as karakter:
            stats = karakter.read().split(',')
            keys = ['HP', 'MP', 'SP', 'DMG', 'EXP', 'EXPToLevelUp', 'Level', 'Gold', 'Wooden Sword', 'Skill Points',
                    'Role']
            # Load stats except 'Skills', which will be handled separately
            self.character_stats = {key: int(value) if key not in ['Wooden Sword', 'Role'] else value for key, value in
                                    zip(keys, stats)}

        # Preserve 'Skills' or initialize if not present
        self.character_stats.setdefault('Skills', {})
        # Load skills from a separate method or file if needed
        self.load_skills()

    def save_character_stats(self):
        with open('Karakter.txt', 'w', encoding='utf-8') as karakter:
            # Save all stats except 'Skills'
            stats_list = [self.character_stats.get(key, 0) for key in
                          ['HP', 'MP', 'SP', 'DMG', 'EXP', 'EXPToLevelUp', 'Level', 'Gold', 'Wooden Sword',
                           'Skill Points', 'Role']]
            stats = ','.join(map(str, stats_list))
            karakter.write(stats)
        # Save 'Skills' separately to maintain their state
        self.save_skills()

    def load_skills(self):
        try:
            with open('Skills.txt', 'r', encoding='utf-8') as skills_file:
                for line in skills_file:
                    skill, level = line.strip().split(':')
                    if skill in skill_trees[
                        self.character_stats['Role']]:  # Check if the skill belongs to the current role
                        self.character_stats['Skills'][skill] = {'level': int(level)}
        except FileNotFoundError:
            print("Skills file not found. Starting with default skills.")

    def save_skills(self):
        print("Saving skills:", self.character_stats['Skills'])  # Debugging line
        with open('Skills.txt', 'w', encoding='utf-8') as skills_file:
            for skill, level in self.character_stats['Skills'].items():
                print(f"Writing skill to file: {skill}, Level: {level}")  # Debugging line
                skills_file.write(f"{skill}:{level}\n")
    def skill_selection(self):
        role = self.character_stats['Role']  # Assuming you have a 'Role' key
        skill_tree = skill_trees[role]

        print(Fore.YELLOW + "Available Skill Points:", self.character_stats['Skill Points'])
        for skill, details in skill_tree.items():
            print(f"{skill}: {details['description']} (Level: {details['level']}/{details['max_level']})")

        choice = input("Choose a skill to upgrade: ")
        if choice in skill_tree and self.character_stats['Skill Points'] > 0:
            skill = skill_tree[choice]
            if skill['level'] < skill['max_level']:
                skill['level'] += 1
                self.character_stats['Skill Points'] -= 1
                # Update the skill level in the character's skills dictionary
                self.character_stats['Skills'][choice] = skill['level']
                print(Fore.GREEN + f"{choice} upgraded to level {skill['level']}.")
                self.save_skills()  # Save skills after updating
            else:
                print(Fore.RED + "Skill is already at max level.")
    def update_goblin_stats(self, dungeon_level):
        # Base stats for goblins and goblin leaders at level 1
        base_goblin_stats = {'HP': 50, 'DMG': 5, 'EXPGiven': 20, 'GoldGiven': 10}
        base_goblin_leader_stats = {'HP': 80, 'DMG': 10, 'EXPGiven': 50, 'GoldGiven': 25}

        # Scaling factor for each dungeon level (you can adjust these values)
        scaling_factor = 1 + (dungeon_level - 1) * 0.5

        # Update goblin stats based on dungeon level
        self.goblin_stats['HP'] = int(base_goblin_stats['HP'] * scaling_factor)
        self.goblin_stats['DMG'] = int(base_goblin_stats['DMG'] * scaling_factor)
        self.goblin_stats['EXPGiven'] = int(base_goblin_stats['EXPGiven'] * scaling_factor)
        self.goblin_stats['GoldGiven'] = int(base_goblin_stats['GoldGiven'] * scaling_factor)

        # Update goblin leader stats based on dungeon level
        self.goblin_leader_stats['HP'] = int(base_goblin_leader_stats['HP'] * scaling_factor)
        self.goblin_leader_stats['DMG'] = int(base_goblin_leader_stats['DMG'] * scaling_factor)
        self.goblin_leader_stats['EXPGiven'] = int(base_goblin_leader_stats['EXPGiven'] * scaling_factor)
        self.goblin_leader_stats['GoldGiven'] = int(base_goblin_leader_stats['GoldGiven'] * scaling_factor)


    def showstats(self):
            # Show character stats
            print(Fore.YELLOW + f"""
    Karakter
    Lv: {self.character_stats['Level']}
    HP: {self.character_stats['HP']}
    MP: {self.character_stats['MP']}
    SP: {self.character_stats['SP']}
    DMG: {self.character_stats['DMG']}
    EXP: {self.character_stats['EXP']}
    EXP to Level Up: {self.character_stats['EXPToLevelUp']}
    Gold: {self.character_stats['Gold']}
            """)

            # Show Goblin stats
            print(Fore.YELLOW + f"""
    Goblin
    HP: {self.goblin_stats['HP']}
    DMG: {self.goblin_stats['DMG']}
    EXP Given: {self.goblin_stats['EXPGiven']}
            """)

            # Show Goblin Leader stats
            print(Fore.YELLOW + f"""
    Goblin Lideri
    HP: {self.goblin_leader_stats['HP']}
    DMG: {self.goblin_leader_stats['DMG']}
    EXP Given: {self.goblin_leader_stats['EXPGiven']}
            """)
            print(Fore.CYAN + "Skills:")
            role = self.character_stats.get('Role', 'Warrior')  # Default to 'Warrior' if 'Role' key is not found
            if role in skill_trees:  # Check if the role exists in the skill trees
                for skill, details in skill_trees[role].items():
                    skill_level = self.character_stats['Skills'].get(skill, {'level': 0})['level']
                    print(f"{skill}: Level {skill_level}/{details['max_level']} - {details['description']}")
            else:
                print("No skills available for this role.")

            self.menu()
    async def fight(self, enemy_stats):
        print(Fore.RED + "Fight started!")
        player_turn = True
        enemy_hp = enemy_stats['HP']
        fight_duration = 15  # Set a maximum number of rounds

        for _ in range(fight_duration):
            if self.character_stats['HP'] <= 0 or enemy_hp <= 0:
                break  # Exit the loop if either the player or the enemy is defeated

            if player_turn:
                damage_dealt = random.randint(0, self.character_stats['DMG'])
                enemy_hp -= damage_dealt
                print(Fore.GREEN + f"You hit the enemy for {damage_dealt} damage. Enemy HP is now {max(0, enemy_hp)}.")
            else:
                damage_taken = random.randint(0, enemy_stats['DMG'])
                self.character_stats['HP'] -= damage_taken
                print(Fore.RED + f"The enemy hits you for {damage_taken} damage. Your HP is now {max(0, self.character_stats['HP'])}.")

            player_turn = not player_turn
            await asyncio.sleep(0.75)  # Wait for 2 seconds between turns

        if self.character_stats['HP'] <= 0:
            print(Fore.RED + "You have been defeated.")
        elif enemy_hp <= 0:
            gold_gain = enemy_stats['GoldGiven']
            self.character_stats['Gold'] += gold_gain
            exp_gain = enemy_stats['EXPGiven']
            self.character_stats['EXP'] += exp_gain
            print(Fore.MAGENTA + f"You have defeated the enemy and gained {exp_gain} EXP and {gold_gain} Gold.")
            if self.character_stats['EXP'] >= self.character_stats['EXPToLevelUp']:
                self.character_stats['Level'] += 1
                self.character_stats['HP'] += 20  # Example HP increase
                self.character_stats['DMG'] += 5  # Example DMG increase
                self.character_stats['EXP'] -= self.character_stats['EXPToLevelUp']  # Subtract EXPToLevelUp from EXP
                self.character_stats['EXPToLevelUp'] += 50  # Example increase in EXP required for next level
                print(Fore.GREEN + f"Congratulations! You've leveled up to Level {self.character_stats['Level']}.")
                self.character_stats['Skill Points'] += 1  # Award a skill point
                self.skill_selection()

        print(Fore.YELLOW + "Fight ended. Press any key to continue...")
        input()

        self.save_character_stats()
        self.load_stats()  # Reload stats to reflect any changes

    def menu(self):
        while True:
            menu = Fore.YELLOW + """
    1) Karakter Seçimi
    2) Savaş
    3) Statları Gör
    4) Market
    5) Quit
            """
            print(menu)
            secim = input("Seçiminiz: ")
            if secim == "1":
                self.character_selection()
            elif secim == "2":
                asyncio.run(self.fight_choice())  # Directly go to fight_choice to select dungeon level and enemies
            elif secim == "3":
                self.showstats()
            elif secim == "4":
                self.market()
            elif secim == "5":
                print(Fore.CYAN + "Quitting the game...")
                break

    def character_selection(self):
        print(Fore.YELLOW + "Select your role:")
        print("1) Warrior")
        print("2) Archer")
        print("3) Mage")
        print("4) Return to Main Menu")

        choice = input("Choose a role (1-4): ")
        role_files = {"1": "Warrior.txt", "2": "Archer.txt", "3": "Mage.txt"}

        if choice in role_files:
            role_file = role_files[choice]
            with open(role_file, 'r', encoding='utf-8') as file:
                stats = file.read()
            with open('Karakter.txt', 'w', encoding='utf-8') as file:
                file.write(stats)
            self.load_stats()  # Reload the character stats from the updated Karakter.txt
            print(Fore.GREEN + f"You have selected the role: {role_file.split('.')[0]}")
        elif choice == "4":
            return  # Return to main menu without changing the role
        else:
            print(Fore.RED + "Invalid selection. Please choose a valid role.")

    async def fight_choice(self):
        max_dungeon_level = (self.character_stats[
                                 'Level'] + 1) // 2  # For example, a new dungeon every 2 character levels
        max_dungeon_level = max(1, max_dungeon_level)  # Ensure there's at least one dungeon level

        print(Fore.YELLOW + "\nSelect Dungeon Level:")
        for i in range(1, max_dungeon_level + 1):
            print(f"{i}) Level {i}")
        print(f"{max_dungeon_level + 1}) Return to Main Menu")

        choice = input("\nChoose dungeon level: ")
        try:
            choice = int(choice)
            if choice == max_dungeon_level + 1:
                return  # Return to main menu
            elif 1 <= choice <= max_dungeon_level:
                dungeon_level = choice
            else:
                print(Fore.RED + "Invalid dungeon level. Returning to main menu.")
                return
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number.")
            return

        self.update_goblin_stats(dungeon_level)

        print(Fore.YELLOW + """
    1) Fight Goblin
    2) Fight Goblin Leader
    3) Return to Main Menu
        """)
        choice = input("Choose your opponent: ")
        if choice == "1":
            await self.fight(self.goblin_stats)  # Use await for async function calls
        elif choice == "2":
            await self.fight(self.goblin_leader_stats)

    def market(self):
        while True:
            print(Fore.YELLOW + f"Gold: {self.character_stats['Gold']}\n")
            print("Available items for purchase:")
            for item, details in self.inventory.items():
                print(f"{item}: {details['Name']} - {details['Price']} Gold, Bonus: {details['Bonus']}")
            print("3) Return to Main Menu")

            choice = input("\nChoose an option: ")
            if choice in self.inventory:
                item_details = self.inventory[choice]
                if self.character_stats['Gold'] >= item_details['Price']:
                    self.character_stats['Gold'] -= item_details['Price']
                    if choice == 'Sword':
                        self.character_stats['DMG'] += item_details['Bonus']
                    elif choice == 'Ring':
                        # Assuming the ring gives an HP bonus for this example
                        self.character_stats['DMG'] += item_details['Bonus']
                    print(Fore.GREEN + f"You've bought a {item_details['Name']}. Bonus applied.")
                else:
                    print(Fore.RED + "Not enough gold.")
            elif choice == "3":
                break
            else:
                print(Fore.RED + "Invalid option.")
        self.save_character_stats()
        print("Wooden Sword Status:", self.character_stats['Wooden Sword'])


if __name__ == '__main__':
    game = Oyun()
    game.menu()
