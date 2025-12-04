class Actor:
    def __init__(self, name):
        self.name = name
        self.abilities = {}

    def can(self, ability):
        self.abilities[type(ability)] = ability
        return self

    def ability_to(self, ability_class):
        return self.abilities.get(ability_class)
