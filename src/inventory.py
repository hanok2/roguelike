import tcod

class Inventory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []


    def add_item(self, item):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'msg': 'You cannot carry any more, your inventory is full.'
            })
        else:
            results.append({
                'item_added': item,
                'msg': 'You pick up the {}!'.format(item.name)
            })

            self.items.append(item)

        return results

    def use(self, item_entity, **kwargs):
        results = []
        item_comp = item_entity.item

        if item_comp.use_func is None:
            equippable_comp = item_entity.equippable

            if equippable_comp:
                results.append({'equip': item_entity})
            else:
                results.append({
                    'msg': 'The {} cannot be used.'.format(item_entity.name),
                })
        else:
            # How does this work? Is there a cleaner way to do this??
            # kwargs = {**item_comp.func_kwargs, **kwargs}  #

            # Check if the item has targeting set to True, and if it does, also
            # check if we received the target x/y variables.
            # If we didn't get coordinates, we can assume that the target has
            # not yet been selected, and the gamestate needs to switch to
            # targeting.

            if item_comp.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({
                    'targeting': item_entity
                })
            else:
                kwargs.update(item_comp.func_kwargs)

                item_use_results = item_comp.use_func(self.owner, **kwargs)

                for result in item_use_results:
                    if result.get('consumed'):
                        self.rm_item(item_entity)

                results.extend(item_use_results)

        return results

    def rm_item(self, item):
        self.items.remove(item)

    def drop(self, item):
        results = []

        # Check if a piece of equipment is equipped. If it is, dequip it before dropping.
        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.rm_item(item)

        results.append({
            'item_dropped': item,
            'msg': 'You dropped the {}.'.format(item.name)
        })

        return results
