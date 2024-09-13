from app import create_app
from app.utils import create_token, verify_token

app = create_app()


if __name__ == "__main__":
    app.run(debug=False)