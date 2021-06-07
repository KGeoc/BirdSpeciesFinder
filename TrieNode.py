class TrieNode:

    def __init__(self):
        self.root = {"*": "*"}

    def add_word(self, word):
        current_node = self.root
        for letter in word:
            if letter not in current_node:
                current_node[letter] = {}
            current_node = current_node[letter]
        current_node[""] = "*"

    def find_word(self, word):
        current_node = self.root
        for letter in word:
            if letter not in current_node:
                return False
            else:
                current_node = current_node[letter]
        if "*" in current_node:
            return True
        else:
            return False


if __name__ == "__main__":
    root = TrieNode()
    root.add_word("test")
    root.add_word('testing')

    print(root.find_word('test'))
    print(root.find_word('tes'))
    print(root.find_word('testing'))
    print(root.find_word('tester'))
    print(root.find_word('hammer'))
