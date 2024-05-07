"""import requests
import random

def get_synonyms(word):
    synonym_dict = {
        "stone": ["rock", "boulder", "pebble"],
        "throne": ["chair", "seat", "stool"]
    }
    return synonym_dict.get(word, [])

def get_random_words():
    word_pairs = [
        ("stone", "throne")
    ]
    return random.choice(word_pairs)

def rhyming_game():
    score = 0

    while True:
        word1, word2 = get_random_words()
        synonym1 = get_synonyms(word1)[0]
        synonym2 = get_synonyms(word2)[0]


        print(f"Synonym of: {synonym1}")
        print(f"Synonym of: {synonym2}")

        user_input1 = input("Enter the original word for the first synonym (or type 'quit' to exit): ").strip().lower()
        if user_input1 == 'quit':
            print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
            break

        user_input2 = input("Enter the original word for the second synonym (or type 'quit' to exit): ").strip().lower()
        if user_input2 == 'quit':
            print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
            break

        if user_input1 == word1 and user_input2 == word2:
            score += 1
            print(f"Correct! You get a point. Your final score is: {score}. ")
        else:
            print("One or both of your guesses are incorrect!")

            retry_hint = input(
                "Do you want to (1) retry with the same words or (2) ask for a hint? Enter 1 or 2: ").strip()
            if retry_hint == '1':
                print(f"Retrying with the same words:")
                continue
            elif retry_hint == '2':
                # Give the next synonym in the list
                synonym1_new = get_synonyms(word1)[1] if len(get_synonyms(word1)) > 1 else synonym1
                synonym2_new = get_synonyms(word2)[1] if len(get_synonyms(word2)) > 1 else synonym2
                print(f"Here are two new synonyms as hints:")
                print(f"New synonym: {synonym1_new}")
                print(f"New synonym: {synonym2_new}")
            else:
                print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    rhyming_game()"""

"""api_ninja 

def get_synonyms(word):
    url = 'https://api.api-ninjas.com/v1/rhyme?word={}'.format(word)
    response = requests.get(url, headers={'X-Api-Key': '3rOHmfIFv1+jo/eYtcEsCw==82K8qh6CuqOQ8gB1'})

    if response.status_code == 200:
        data = response.json()

        if isinstance(data, list):
            # If the response is a list, assume it directly contains the synonyms
            return data
        else:
            # If the response is a dictionary, use the previous approach
            return data.get('synonyms', []) if data else []
    else:
        print(f"Error fetching synonyms for {word}.")
        return []"""

"""preset list

import requests
import random

synonyms_dict = {
    "stone": ["rock", "boulder", "pebble"],
    "throne": ["chair", "seat", "stool"],
}

preselected_word_pairs = [
    ("stone", "throne"),
    ("love", "above"),
    ("blue", "true"),
]

def get_random_word_pair():
    return random.choice(preselected_word_pairs)

def get_synonyms(word):
    return synonyms_dict.get(word, [])

def rhyming_game():
    score = 0
    game_continue = True  # Initialize the flag to True

    while game_continue:
        word_pair = get_random_word_pair()
        random_word = word_pair[0]
        rhyming_word = word_pair[1]

        f"Random Word: {random_word}"
        f"Rhyming Word: {rhyming_word}"

        synonyms_random_word = get_synonyms(random_word)
        synonyms_rhyming_word = get_synonyms(rhyming_word)

        if synonyms_random_word and synonyms_rhyming_word:
            synonym1 = random.choice(synonyms_random_word)
            synonym2 = random.choice(synonyms_rhyming_word)

            print(f"Synonym of word 1: {synonym1}")
            print(f"Synonym of word 2: {synonym2}")

            user_input1 = input("Enter the original word for the first synonym (or type 'quit' to exit): ").strip().lower()
            if user_input1 == 'quit':
                print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
                game_continue = False  # Exit the loop
                break

            user_input2 = input("Enter the original word for the second synonym (or type 'quit' to exit): ").strip().lower()
            if user_input2 == 'quit':
                print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
                game_continue = False  # Exit the loop
                break

            if user_input1 == random_word and user_input2 == rhyming_word:
                score += 1
                print(f"Correct! You get a point. Your final score is: {score}. ")
            else:
                print("One or both of your guesses are incorrect!")

                retry_hint = input(
                    "Do you want to (1) retry with the same words or (2) ask for a hint? Enter 1 or 2: ").strip()
                if retry_hint == '1':
                    print(f"Retrying with the same words:")
                    continue  # Continue the loop without fetching new words
                elif retry_hint == '2':
                    # Give the next synonym in the list
                    synonym1_new = synonyms_random_word[1] if len(synonyms_random_word) > 1 else synonym1
                    synonym2_new = synonyms_rhyming_word[1] if len(synonyms_rhyming_word) > 1 else synonym2
                    print(f"Here are two new synonyms as hints:")
                    print(f"New synonym: {synonym1_new}")
                    print(f"New synonym: {synonym2_new}")
                    # Exit the loop
                    game_continue = False
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        else:
            print("Error: No synonyms found for one or both words.")
    else:
        print("Exiting the game due to an error.")


if __name__ == "__main__":
    rhyming_game()"""

"""issues with option 1
import requests
import random

synonyms_dict = {
    "stone": ["rock", "boulder", "pebble"],
    "throne": ["chair", "seat", "stool"],
    "love": ["affection", "passion", "devotion"],
    "above": ["over", "higher", "up"],
    "blue": ["azure", "sapphire", "navy"],
    "true": ["accurate", "correct", "genuine"],
}

preselected_word_pairs = [
    ("stone", "throne"),
    ("love", "above"),
    ("blue", "true"),
]

def get_random_words():
    return random.choice(preselected_word_pairs)

def get_synonyms(word):
    return synonyms_dict.get(word, [])

def rhyming_game():
    score = 0
    initial_synonyms_word1 = []
    initial_synonyms_word2 = []
    word1 = ""
    word2 = ""

    while True:
        if not word1 or not word2:
            word1, word2 = get_random_words()
            initial_synonyms_word1 = get_synonyms(word1).copy()
            initial_synonyms_word2 = get_synonyms(word2).copy()

        while True:
            if not initial_synonyms_word1:
                print("Out of initial synonyms for word 1. Generating new ones.")
                initial_synonyms_word1 = get_synonyms(word1).copy()

            if not initial_synonyms_word2:
                print("Out of initial synonyms for word 2. Generating new ones.")
                initial_synonyms_word2 = get_synonyms(word2).copy()

            initial_synonym1 = initial_synonyms_word1.pop(0)
            initial_synonym2 = initial_synonyms_word2.pop(0)

            print(f"Synonym of word 1: {initial_synonym1}")
            print(f"Synonym of word 2: {initial_synonym2}")

            user_input1 = input("Enter the original word for the first synonym (or type 'quit' to exit): ").strip().lower()
            if user_input1 == 'quit':
                print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
                return

            user_input2 = input("Enter the original word for the second synonym (or type 'quit' to exit): ").strip().lower()
            if user_input2 == 'quit':
                print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
                return

            if user_input1 == word1 and user_input2 == word2:
                score += 1
                print(f"Correct! You get a point. Your final score is: {score}. ")
                break
            else:
                print("One or both of your guesses are incorrect!")

                retry_hint = input(
                    "Do you want to (1) retry with the same words or (2) ask for a hint? Enter 1 or 2: ").strip()
                if retry_hint == '1':
                    print(f"Retrying with the same words:")
                    break
                elif retry_hint == '2':
                    # Give the next synonym in the list if available
                    synonym1_new = random.choice(get_synonyms(word1))
                    synonym2_new = random.choice(get_synonyms(word2))
                    print(f"Here are two new synonyms as hints:")
                    print(f"New synonym of word 1: {synonym1_new}")
                    print(f"New synonym of word 2: {synonym2_new}")
                    break
                else:
                    print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    rhyming_game()
"""

"""okay working?
import requests
import random
import os

synonyms_dict = {
    "stone": ["rock", "boulder", "pebble"],
    "throne": ["chair", "seat", "stool"],
    "love": ["affection", "passion", "devotion"],
    "above": ["over", "higher", "up"],
    "blue": ["azure", "sapphire", "navy"],
    "true": ["accurate", "correct", "genuine"],
}

preselected_word_pairs = [
    ("stone", "throne"),
    ("love", "above"),
    ("blue", "true"),
]

def get_random_words():
    return random.choice(preselected_word_pairs)

def get_synonyms(word):
    return synonyms_dict.get(word, [])

def rhyming_game():
    score = 0
    current_words = None

    while True:
        if not current_words:
            word1, word2 = get_random_words()
            current_words = (word1, word2)
        else:
            word1, word2 = current_words

        initial_synonyms_word1 = get_synonyms(word1).copy()
        initial_synonyms_word2 = get_synonyms(word2).copy()

        if not initial_synonyms_word1 or not initial_synonyms_word2:
            print("Error: No synonyms found for one or both words.")
            break

        synonym1 = initial_synonyms_word1.pop(0)
        synonym2 = initial_synonyms_word2.pop(0)

        print(f"Synonym of word 1: {synonym1}")
        print(f"Synonym of word 2: {synonym2}")

        user_input1 = input("Enter the original word for the first synonym (or type 'quit' to exit): ").strip().lower()
        if user_input1 == 'quit':
            print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
            break

        user_input2 = input("Enter the original word for the second synonym (or type 'quit' to exit): ").strip().lower()
        if user_input2 == 'quit':
            print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
            break

        if user_input1 == word1 and user_input2 == word2:
            score += 1
            print(f"Correct! You get a point. Your current score is: {score}. ")
            continue
        else:
            print("One or both of your guesses are incorrect!")

            retry_hint = input(
                "Do you want to (1) retry with the same words or (2) ask for a hint? Enter 1 or 2: ").strip()
            if retry_hint == '1':
                print(f"Retrying with the same words:")
                continue
            elif retry_hint == '2':
                # Give the next synonym in the list if available
                synonym1_new = initial_synonyms_word1[0] if initial_synonyms_word1 else get_synonyms(word1)[1]
                synonym2_new = initial_synonyms_word2[0] if initial_synonyms_word2 else get_synonyms(word2)[1]
                print(f"Here are two new synonyms as hints:")
                print(f"New synonym of word 1: {synonym1_new}")
                print(f"New synonym of word 2: {synonym2_new}")
            else:
                print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    rhyming_game()
"""

"""issues options
import random
import os

# File paths
word_pairs_file = "word_pairs.txt"
synonyms_file = "synonyms.txt"

def load_word_pairs():
    with open(word_pairs_file, "r") as file:
        lines = file.readlines()
        return [tuple(line.strip().split(",")) for line in lines]

def load_synonyms():
    synonyms_dict = {}
    with open(synonyms_file, "r") as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                word, synonyms = parts[0], parts[1].split(",")
                synonyms_dict[word] = synonyms
    return synonyms_dict

def get_random_word_pair(word_pairs, used_word_pairs):
    remaining_word_pairs = [pair for pair in word_pairs if pair not in used_word_pairs]

    return random.choice(remaining_word_pairs)

def get_synonyms(word, synonyms_dict):
    return synonyms_dict.get(word, [])

def rhyming_game():
    word_pairs = load_word_pairs()
    synonyms_dict = load_synonyms()
    used_word_pairs = set()
    used_synonyms = {}
    score = 0

    while True:
        word_pair = get_random_word_pair(word_pairs, used_word_pairs)
        if not word_pair:
            break

        word1, word2 = word_pair

        if word_pair not in used_synonyms or word_pair in used_word_pairs:
            used_synonyms[word_pair] = {
                word1: get_synonyms(word1, synonyms_dict).copy(),
                word2: get_synonyms(word2, synonyms_dict).copy()
            }

        initial_synonyms_word1 = used_synonyms[word_pair][word1]
        initial_synonyms_word2 = used_synonyms[word_pair][word2]

        if not initial_synonyms_word1 or not initial_synonyms_word2:
            print("Error: No synonyms found for one or both words.")
            break

        synonym1 = initial_synonyms_word1.pop(0)
        synonym2 = initial_synonyms_word2.pop(0)

        print(f"Synonym of word 1: {synonym1}")
        print(f"Synonym of word 2: {synonym2}")

        user_input1 = input("Enter the original word for the first synonym (or type 'quit' to exit): ").strip().lower()
        if user_input1 == 'quit':
            print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
            break

        user_input2 = input("Enter the original word for the second synonym (or type 'quit' to exit): ").strip().lower()
        if user_input2 == 'quit':
            print(f"Thanks for playing! Your final score is: {score}. Goodbye.")
            break

        if user_input1 == word1 and user_input2 == word2:
            score += 1
            print(f"Correct! You get a point. Your current score is: {score}. ")
            used_word_pairs.add(word_pair)
        else:
            print("One or both of your guesses are incorrect!")

            retry_hint = input(
                "Do you want to (1) retry with the same words or (2) ask for a hint? Enter 1 or 2: ").strip()
            if retry_hint == '1':
                print(f"Retrying with the same words:")
                continue
            elif retry_hint == '2':
                # Give the next synonym in the list if available
                #synonym1_new = synonym1 if initial_synonyms_word1 else initial_synonyms_word1[0]
                #synonym2_new = synonym2 if initial_synonyms_word2 else initial_synonyms_word2[0]
                synonym1_new = get_synonyms(word1)[1] if len(get_synonyms(word1)) > 1 else synonym1
                synonym2_new = get_synonyms(word2)[1] if len(get_synonyms(word2)) > 1 else synonym2
                print(f"Here are two new synonyms as hints:")
                print(f"New synonym of word 1: {synonym1_new}")
                print(f"New synonym of word 2: {synonym2_new}")
            else:
                print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    rhyming_game()
"""