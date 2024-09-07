import random
import logging

from flask_login import current_user

from app import db
from app.models import WordPair, UserWordPair

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_word_pair(user_id):
    # Fetch unguessed word pairs for the user
    user_word_pairs = db.session.query(UserWordPair).filter_by(user_id=user_id, guessed=False).all()

    if not user_word_pairs:
        return None

    # Select the first unguessed word pair (or implement your own selection logic)
    user_word_pair = user_word_pairs[0]

    # Retrieve the word pair from the WordPair table
    word_pair = db.session.query(WordPair).get(user_word_pair.word_pair_id)

    if not word_pair:
        return None

    return db.session.query(WordPair).join(UserWordPair).filter(UserWordPair.user_id == user_id, UserWordPair.guessed == False).first()

def load_synonyms(word_pair):
    synonyms_dict = {}
    word1 = word_pair.word1
    word2 = word_pair.word2

    # Extract synonyms for word1
    synonyms_dict[word1] = [word_pair.word1_synonym1, word_pair.word1_synonym2]
    # Extract synonyms for word2
    synonyms_dict[word2] = [word_pair.word2_synonym1, word_pair.word2_synonym2]

    return synonyms_dict

def get_synonyms(word, synonyms_dict):
    synonyms = synonyms_dict.get(word, [])
    logger.debug(f"Synonyms for {word}: {synonyms}")
    return synonyms

def mark_word_pair_as_guessed(user_id, word_pair_id):
    user_word_pair = UserWordPair(user_id=user_id, word_pair_id=word_pair_id, guessed=True)
    db.session.add(user_word_pair)
    db.session.commit()

def move_word_pair_to_used(word_pair):
    word_pair_to_update = db.session.query(WordPair).filter_by(word1=word_pair[0], word2=word_pair[1]).first()
    if word_pair_to_update:
        word_pair_to_update.used = True
        db.session.commit()

def move_synonyms_to_used(word_pair):
    # Synonyms are already in the database, so no action needed
    pass


def rhyming_game():
    user_id = current_user.id  # Get the current user's ID
    logger.debug(f"Starting rhyming game for user_id: {user_id}")

    word_pair = load_word_pair(user_id)

    if not word_pair:
        logger.debug("No word pair found, exiting rhyming game")
        return

    word1, word2 = word_pair
    logger.debug(f"Loaded word pair: {word1} - {word2}")

    synonyms_dict = load_synonyms()
    used_word_pair = False
    score = 0

    while not used_word_pair:
        initial_synonyms_word1 = get_synonyms(word1, synonyms_dict).copy()
        initial_synonyms_word2 = get_synonyms(word2, synonyms_dict).copy()

        if not initial_synonyms_word1 or not initial_synonyms_word2:
            logger.error("No synonyms found for one or both words.")
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
            logger.debug(f"User {user_id} guessed correctly: {word1} - {word2}. Score: {score}")
            print(f"Correct! You get a point. Your current score is: {score}. ")
            used_word_pair = True
            move_word_pair_to_used(word_pair)
        else:
            logger.debug(f"User {user_id} guessed incorrectly: {user_input1} - {user_input2}")
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
                logger.debug(f"Providing hint to user {user_id}: {synonym1_new} - {synonym2_new}")
                print(f"Here are two new synonyms as hints:")
                print(f"New synonym of word 1: {synonym1_new}")
                print(f"New synonym of word 2: {synonym2_new}")
            else:
                print("Invalid choice. Please enter 1 or 2.")

def load_word_pair_from_synonyms():
    word_pairs = db.session.query(WordPair).all()
    if word_pairs:
        pair = random.choice(word_pairs)
        return (pair.word1, pair.word2)
    return None

def record_user_guess(user_id, word_pair_id):
    user_word_pair = UserWordPair.query.filter_by(user_id=user_id, word_pair_id=word_pair_id).first()
    if not user_word_pair:
        user_word_pair = UserWordPair(user_id=user_id, word_pair_id=word_pair_id, guessed=True)
        db.session.add(user_word_pair)
    db.session.commit()
    logger.debug("Recorded user guess for user_id %d and word_pair_id %d", user_id, word_pair_id)