import json
from operator import le



class Wordle():
    def __init__(self, lang='ua'):
        self.lang = lang
        self.vocabulary = self.read_vocabulary()
        self.attempts = 6
        self.black = []
        self.yellow = {0: [], 1: [], 2: [], 3: [], 4: []}
        self.green = {}
        self.guessed = set()
        self.colours = []
       


    def get_positions(self, word, positions):
        col = ''
        for index, letter in enumerate(positions):
            if letter == 'Ж':
                self.yellow[index].append(word[index])
                self.guessed.add(word[index])
                col += chr(129000)
            elif letter == 'З':
                self.green[index] = word[index]
                col += chr(129001)
            else:
                if word[index] not in self.yellow:
                    self.black.append(word[index])
                col += chr(11036)
        self.colours.append(col)



    def read_vocabulary(self):
        file = 'wordle/' + self.lang + '.json'
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)

    
    def find_possible_variations(self):
        self.vocabulary = list(filter(lambda word: self._pass_filters(word), self.vocabulary))

    
    def _pass_filters(self, word):
        return all([self._with_positional(word), self._without_waste_letters(word), self._with_guessed_letters(word), self._without_non_positional(word)])



    def _with_positional(self, word):
        return all(word[position] == letter for position, letter in self.green.items())

    def _without_waste_letters(self, word):
        return all(letter not in word for letter in self.black)

    def _with_guessed_letters(self, word):
        return all(letter in word for letter in self.guessed)

    def _without_non_positional(self, word):
        return all(word[i] not in self.yellow[i] for i in self.yellow if self.yellow[i])


