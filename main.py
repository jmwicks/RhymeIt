# Copyright (c) 2024 Jason Wicks
# All rights reserved.
#
# Copyright pending.

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)