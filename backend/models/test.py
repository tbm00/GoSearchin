# Import the User class from the user module
from user import User

# Create a test function to perform various operations
def test_user_operations():
    # Create a User object with a test username
    test_user = User("test_user")

    # Insert the user into the Accounts table
    test_user.insert_user()

    # Insert a search query
    test_user.insert_query("test_query")

    # Retrieve all search queries for the user
    queries = test_user.retrieve_queries()
    print("Retrieved queries:", queries)

    # Delete the test query
    test_user.delete_query("test_query")

    # Retrieve all search queries again to verify deletion
    queries = test_user.retrieve_queries()
    print("Retrieved queries after deletion:", queries)

    # Update user location
    if test_user.update_location():
        print("Location updated successfully")
    else:
        print("Failed to update location")

    # Retrieve user location
    location = test_user.retrieve_location()
    print("Retrieved location:", location)

    # Insert a search result
    test_user.insert_search_result("test_query", "test_result")

    # Retrieve search results for the test query
    results = test_user.retrieve_search_results("test_query")
    print("Retrieved search results:", results)

    # Delete the search result
    test_user.delete_search_result("test_query", "test_result")

    # Retrieve search results again to verify deletion
    results = test_user.retrieve_search_results("test_query")
    print("Retrieved search results after deletion:", results)

# Execute the test function
test_user_operations()
