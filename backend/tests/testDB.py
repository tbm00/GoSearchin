from app.models.dbConnector import dbConnector

def test_create_schema():
    # Initialize the database connector
    db = dbConnector()

    # Test the create_schema method
    db.create_schema()

if __name__ == "__main__":
    # Run the test_create_schema function when the script is executed directly
    test_create_schema()