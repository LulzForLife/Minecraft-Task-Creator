from __future__ import annotations
import json
import os
from math import ceil

class Material:
    def __init__(self, type: str, material: str, count: int) -> None:#
        self.type = type
        self.material = material
        self.count = count
        self._completed = False
    def __eq__(self, value: object) -> bool:
        '''
        Compares the material of this object to another object's material.
        If the other object is not of type 'Material', it will return false.
        '''
        if isinstance(value, Material):
            return self.material == value.material
        return False
    def __int__(self) -> int:
        '''
        Returns self.count.
        '''
        return self.count
    def __str__(self) -> str:
        '''
        Returns self.material.
        '''
        return self.material
    def __bool__(self) -> bool:
        '''
        Returns self._completed.
        Note: self._completed is used when making tasks. Do not use for your own purposes.
        '''
        return self._completed
    def __repr__(self) -> str:
        '''
        Returns a string in the format:

        f'{self.type} {self.count} {self.material}{'s' if plural else ''}'
        '''
        plural = self.count > 1 and not self.material.endswith('s')
        return f'{self.type} {self.count} {self.material}{'s' if plural else ''}'

def load_items() -> None:
    global tools, workstations
    current_dir = os.path.dirname(os.path.abspath(__file__))
    recipes_dir = os.path.join(current_dir, 'recipes')
    tools_dir = os.path.join(current_dir, 'tools.json')
    workstations_dir = os.path.join(current_dir, 'workstations.json')

    recipe_filenames = list(os.walk(recipes_dir))[0][2]
    for dir in recipe_filenames:
        if not dir.startswith('__'):
            with open(os.path.join(recipes_dir, dir), 'r') as f:
                data = json.load(f)
                materials[os.path.basename(dir).split('.')[0]] = data
    
    with open(tools_dir, 'r') as f:
        data = json.load(f)
        tools = data
    
    with open(workstations_dir, 'r') as f:
        data = json.load(f)
        workstations = data

def get_order() -> None:
    if all(tasks):
        return
    idx = 0
    while (task := tasks[idx])._completed:
        idx += 1
    data = materials[task.material]
    if data['type'] == 'craft':
        for item in data['recipe']:
            tasks.append(Material(materials[item['name']]['type'], item['name'], 0))
        if data['location'] == 'crafting_table':
            tasks.append(Material('craft', 'crafting_table', 0))
    elif data['type'] == 'mine':
        if not data['minimum'] == 'hand':
            tasks.append(Material('craft', data['minimum'], 0))
    elif data['type'] == 'smelt':
        tasks.append(Material(materials[data['item']]['type'], data['item'], 0))
        tasks.append(Material('mine', 'coal', 0))
        tasks.append(Material('craft', 'furnace', 0))
    elif data['type'] == 'drop':
        if not data['recommended'][0] == 'hand':
            for recommended in data['recommended']:
                tasks.append(Material(materials[recommended['name']]['type'], recommended['name'], 0))
    tasks[idx]._completed = True
    get_order()

def merge_order() -> None:
    global tasks
    fixed_tasks: list[Material] = []
    for task in tasks:
        task._completed = False
        if str(task) in map(str, fixed_tasks):
            fixed_tasks.append(task)
            index = list(map(str, fixed_tasks)).index(str(task))
            fixed_tasks.pop(index)
        else:
            fixed_tasks.append(task)
    tasks = fixed_tasks

def get_tasks() -> None:
    global tasks
    def add_task(material: str, count: int) -> None:
        index = list(map(str, tasks)).index(material)
        tasks[index].count += count
    fuel = 0
    for n, task in enumerate(tasks):
        if n != 0:
            if (task.material in workstations or 
                task.material in tools['sword'] or
                task.material in tools['pickaxe'] or
                task.material in tools['helmet'] or
                task.material in tools['chestplate'] or
                task.material in tools['leggings'] or
                task.material in tools['boots']):
                task.count = 1
        data = materials[task.material]
        if task.type == 'craft':
            count = ceil(task.count / data['count'])
            for item in data['recipe']:
                add_task(item['name'], item['count'] * count)
        elif task.type == 'mine':
            if data['minimum'] != 'hand':
                add_task(data['minimum'], 1)
            task.material = data['block']
            if task.material == 'coal_ore':
                task.count = ceil(fuel / 8)
        elif task.type == 'smelt':
            add_task(data['item'], task.count)
            fuel += task.count
        elif task.type == 'drop':
            if not data['recommended'][0] == 'hand':
                for recommended in data['recommended']:
                    add_task(recommended['name'], recommended['count'])
        task._completed = True

def get_inventory() -> None:
    for task in tasks:
        if task.type == 'craft':
            data = materials[task.material]
            rounded_up = ceil(task.count / data['count']) * data['count']
            if rounded_up - task.count:
                inventory.append(Material('inventory', task.material, rounded_up - task.count))
            task.count = rounded_up

def make_tasks() -> None:
    get_order()
    merge_order()
    get_tasks()
    get_inventory()

if __name__ == '__main__':
    SHOW_COMPLETED = False

    materials: dict[str, dict] = dict()
    tools: dict[str, list[str]] = dict()
    workstations: list[str] = []
    load_items()

    item_and_count = input().split()
    if len(item_and_count) >= 2:
        item_to_get, count = item_and_count
        count = int(count)
    else:
        item_to_get, count = item_and_count[0], 1

    if not item_to_get in materials.keys():
        print(f'Unknown item or block: {item_to_get}')
        #exit()

    tasks: list[Material] = [Material(materials[item_to_get]['type'], item_to_get, count)]
    inventory: list[Material] = []

    make_tasks()

    print(tasks)
    print(inventory)