import csv
from datetime import datetime

from app import db, create_app
from app.models import WordPair, Synonym, User, UserWordPair

app = create_app()

def import_word_pairs(file_path):
    """Import word pairs and their synonyms from a CSV file into the database."""
    with app.app_context():
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                word1 = row['word1']
                word2 = row['word2']
                synonym1_word = row.get('word1_synonym1', '')
                synonym2_word = row.get('word1_synonym2', '')
                synonym3_word = row.get('word2_synonym1', '')
                synonym4_word = row.get('word2_synonym2', '')
                date_available_str = row.get('date_available', None)

                # Convert date string to a Python date object
                if date_available_str:
                    date_available = datetime.strptime(date_available_str, '%Y-%m-%d').date()
                else:
                    date_available = None  # Set to None if no date provided

                # Fetch or create synonyms
                for synonym_word in [synonym1_word, synonym2_word, synonym3_word, synonym4_word]:
                    if synonym_word:
                        synonym_entry = Synonym.query.filter_by(word=synonym_word).first()
                        if not synonym_entry:
                            synonym_entry = Synonym(word=synonym_word)
                            db.session.add(synonym_entry)

                # Add or update the word pair
                word_pair = WordPair.query.filter_by(
                    word1=word1, word2=word2
                ).first()

                if not word_pair:
                    word_pair = WordPair(
                        word1=word1,
                        word2=word2,
                        word1_synonym1=synonym1_word,
                        word1_synonym2=synonym2_word,
                        word2_synonym1=synonym3_word,
                        word2_synonym2=synonym4_word,
                        date_available=date_available  # Add the date object here
                    )
                    db.session.add(word_pair)
                    db.session.commit()

                # Add user_word_pair entries for each user
                add_user_word_pairs(word_pair.id)

def add_user_word_pairs(word_pair_id):
    """Add user-word pair relationships for each user."""
    with app.app_context():
        users = User.query.all()
        for user in users:
            user_word_pair = UserWordPair.query.filter_by(
                user_id=user.id, word_pair_id=word_pair_id
            ).first()
            if not user_word_pair:
                user_word_pair = UserWordPair(
                    user_id=user.id,
                    word_pair_id=word_pair_id
                )
                db.session.add(user_word_pair)
        db.session.commit()

def import_synonyms(file_path):
    """Import synonyms from a CSV file into the database."""
    with app.app_context():
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                word = row['word']
                synonym = row['synonym']
                synonym_entry = Synonym.query.filter_by(word=word).first()

                if not synonym_entry:
                    synonym_entry = Synonym(word=word, synonyms='')
                    db.session.add(synonym_entry)

                if synonym_entry.synonyms:
                    synonym_entry.synonyms += ',' + synonym
                else:
                    synonym_entry.synonyms = synonym

        db.session.commit()

#def insert_data():
#    """Insert example data into the database."""
#    with app.app_context():
#        users = User.query.all()
#        word_pairs = [
#            {'word1': 'happy', 'word1_synonym1': 'joyful', 'word1_synonym2': 'content', 'word2': 'sad',
#             'word2_synonym1': 'unhappy', 'word2_synonym2': 'down'},
#            {'word1': 'big', 'word1_synonym1': 'large', 'word1_synonym2': 'huge', 'word2': 'small',
#             'word2_synonym1': 'tiny', 'word2_synonym2': 'little'}
#        ]

#        for user in users:
#            for pair in word_pairs:
#                word_pair = WordPair(
#                    word1=pair['word1'],
#                    word1_synonym1=pair['word1_synonym1'],
#                    word1_synonym2=pair['word1_synonym2'],
#                    word2=pair['word2'],
#                    word2_synonym1=pair['word2_synonym1'],
#                    word2_synonym2=pair['word2_synonym2']
#                )
#                db.session.add(word_pair)
#                db.session.commit()
#                add_user_word_pairs(word_pair.id)
#
#        print("Data inserted successfully.")

if __name__ == "__main__":
    import_word_pairs('data/word_pairs.csv')
    # Uncomment the line below to import synonyms if needed
    # import_synonyms('path/to/synonyms.csv')
    # Uncomment the line below to insert example data if needed
    # insert_data()
