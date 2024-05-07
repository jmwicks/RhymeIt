from flask import Flask, render_template, request, redirect, url_for
import random
import os

app = Flask(__name__)

# File paths
word_pairs_file = "word_pairs.txt"
used_word_pairs_file = "used_word_pairs.txt"
synonyms_file = "synonyms.txt"
used_synonyms_file = "used_synonyms.txt"


def load_word_pair():
    try:
        with open(word_pairs_file, "r") as file:
            line = file.readline()
            word_pair = tuple(line.strip().split(","))

            # Check if the word pair is already in used_word_pairs.txt
            if word_pair_in_used(word_pair):
                print("You have already guessed today's word pair. Check back again tomorrow for a new word pair!")
                #return load_word_pair()
            else:
                return word_pair
    except FileNotFoundError:
        print(f"Error: File {word_pairs_file} not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def word_pair_in_used(word_pair):
    try:
        with open(used_word_pairs_file, "r") as file:
            return ",".join(word_pair) in file.read()
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def load_synonyms():
    synonyms_dict = {}
    try:
        with open(synonyms_file, "r") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    word, synonyms = parts[0], parts[1].split(",")
                    synonyms_dict[word] = synonyms
    except FileNotFoundError:
        print(f"Error: File {synonyms_file} not found.")
    except Exception as e:
        print(f"Error: {e}")
    return synonyms_dict


def get_synonyms(word, synonyms_dict):
    return synonyms_dict.get(word, [])


def move_word_pair_to_used(word_pair):
    with open(used_word_pairs_file, "a") as file:
        file.write(",".join(word_pair) + "\n")


def move_synonyms_to_used(word_pair, synonyms_dict):
    with open(used_synonyms_file, "a") as file:
        for word in word_pair:
            if word in synonyms_dict:
                file.write(f"{word}:{','.join(synonyms_dict[word])}\n")
                del synonyms_dict[word]


def remove_word_pair_from_file(word_pair):
    try:
        with open(word_pairs_file, "r") as file:
            lines = file.readlines()
        with open(word_pairs_file, "w") as file:
            for line in lines:
                if line.strip() != ",".join(word_pair):
                    file.write(line)
    except FileNotFoundError:
        print(f"Error: File {word_pairs_file} not found.")
    except Exception as e:
        print(f"Error: {e}")


def remove_synonyms_from_file(word_pair):
    try:
        with open(synonyms_file, "r") as file:
            lines = file.readlines()
        with open(synonyms_file, "w") as file:
            for line in lines:
                parts = line.strip().split(":")
                if len(parts) == 2 and parts[0] not in word_pair:
                    file.write(line)
    except FileNotFoundError:
        print(f"Error: File {synonyms_file} not found.")
    except Exception as e:
        print(f"Error: {e}")


def rhyming_game():
    word_pair = load_word_pair()

    if not word_pair:
        return

    word1, word2 = word_pair
    synonyms_dict = load_synonyms()
    used_word_pair = False
    score = 0

    while not used_word_pair:
        initial_synonyms_word1 = get_synonyms(word1, synonyms_dict).copy()
        initial_synonyms_word2 = get_synonyms(word2, synonyms_dict).copy()

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
            used_word_pair = True
            move_word_pair_to_used(word_pair)
            move_synonyms_to_used(word_pair, synonyms_dict)
            remove_word_pair_from_file(word_pair)
            remove_synonyms_from_file(word_pair)
        else:
            print("One or both of your guesses are incorrect!")

            retry_hint = input(
                "Do you want to (1) retry with the same words or (2) ask for a hint? Enter 1 or 2: ").strip()
            if retry_hint == '1':
                print(f"Retrying with the same words:")
            elif retry_hint == '2':
                # Give the next synonym in the list if available
                synonym1_new = initial_synonyms_word1[0] if initial_synonyms_word1 else get_synonyms(word1)[1] if len(
                    get_synonyms(word1)) > 1 else synonym1
                synonym2_new = initial_synonyms_word2[0] if initial_synonyms_word2 else get_synonyms(word2)[1] if len(
                    get_synonyms(word2)) > 1 else synonym2
                print(f"Here are two new synonyms as hints:")
                print(f"New synonym of word 1: {synonym1_new}")
                print(f"New synonym of word 2: {synonym2_new}")
            else:
                print("Invalid choice. Please enter 1 or 2.")

@app.route('/get_hint')
def get_hint():
    word_pair = load_word_pair()

    if not word_pair:
        return render_template('game_over.html')

    word1, word2 = word_pair
    synonyms_dict = load_synonyms()

    # Get both synonyms for the chosen words
    synonyms_word1 = synonyms_dict.get(word1, ["No synonyms found"])
    synonyms_word2 = synonyms_dict.get(word2, ["No synonyms found"])

    return render_template('second_play.html', word1=word1, word2=word2, synonyms_word1=synonyms_word1, synonyms_word2=synonyms_word2)


def load_word_pair_from_synonyms():
    try:
        with open("synonyms.txt", "r") as file:
            lines = file.readlines()
            if lines:
                # Choose a random line (word pair) from the file
                line = random.choice(lines)
                # Split the line into words
                words = line.strip().split(":")[0].split(",")
                # Ensure that there are at least two words
                if len(words) >= 2:
                    return tuple(words[:2])  # Return the first two words as a tuple
    except FileNotFoundError:
        print("Error: File synonyms.txt not found.")
    except Exception as e:
        print(f"Error: {e}")

    # Return None if there was an error or not enough words
    return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/play', methods=['POST', 'GET'])
def play():
    word_pair = load_word_pair()

    if not word_pair:
        return render_template('game_over.html')

    word1, word2 = word_pair
    synonyms_dict = load_synonyms()

    # Get the first synonym of each word
    synonym_word1 = synonyms_dict.get(word1, ["No synonyms found"])[0]
    synonym_word2 = synonyms_dict.get(word2, ["No synonyms found"])[0]

    return render_template('play.html', word1=word1, word2=word2, synonym_word1=synonym_word1, synonym_word2=synonym_word2)

@app.route('/check_guess', methods=['POST'])
def check_guess():
    user_input1 = request.form.get('user_input1', '').strip().lower()
    user_input2 = request.form.get('user_input2', '').strip().lower()
    word1 = request.form.get('word1', '')
    word2 = request.form.get('word2', '')

    word_pair = (word1, word2)  # Define word_pair here

    if user_input1 == word1 and user_input2 == word2:
        move_word_pair_to_used((word1, word2))
        move_synonyms_to_used(word_pair, load_synonyms())  # Move synonyms to used_synonyms.txt
        remove_synonyms_from_file(word_pair)
        remove_word_pair_from_file((word1, word2))
        return render_template('correct_guess.html')
    else:
        return render_template('incorrect_guess.html')


if __name__ == "__main__":
    app.run(debug=True)

#add instructions?