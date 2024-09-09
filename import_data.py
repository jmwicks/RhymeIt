import csv
from datetime import datetime

from app import db, create_app
from app.models import WordPair, User, UserWordPair

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
                try:
                    date_available = datetime.strptime(date_available_str,
                                                       '%Y-%m-%d').date() if date_available_str else None
                except ValueError:
                    print(f"Invalid date format for word pair: {word1} - {word2}. Skipping.")
                    continue

                # Add or update the word pair
                word_pair = WordPair.query.filter_by(
                    word1=word1, word2=word2
                ).first()

                if not word_pair:
                    word_pair = WordPair(
                        word1=word1,
                        word1_synonym1=synonym1_word,
                        word1_synonym2=synonym2_word,
                        word2=word2,
                        word2_synonym1=synonym3_word,
                        word2_synonym2=synonym4_word,
                        date_available=date_available
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




if __name__ == "__main__":
    import_word_pairs('data/word_pairs.csv')
