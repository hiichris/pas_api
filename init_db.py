from app import db, app


if __name__ == "__main__":
    # Initialize the database
    with app.app_context():
        db.create_all()
        print("Database initialized")
