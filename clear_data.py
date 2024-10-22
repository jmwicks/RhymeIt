# Copyright (c) 2024 Jason Wicks
# All rights reserved.
#
# Copyright pending.

from app import create_app, db
from app.models import User, UserWordPair, WordPair

# = create_app()

#def clear_word_pair_table():
 #   """Delete all data from the WordPair table."""
 #   with app.app_context():
 #       db.session.query(WordPair).delete()
 #       db.session.commit()

#def clear_user_word_pair_table():
#    with app.app_context():
#        db.session.query(UserWordPair).delete()
#        db.session.commit()

#if __name__ == '__main__':
#    clear_user_word_pair_table()
