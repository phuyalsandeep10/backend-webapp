# #!/usr/bin/env python3
# """
# Simple test script to check if conversations can be created and retrieved
# """
# import sys
# import os

# # Add the src directory to the Python path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# from src.models import Conversation, Customer
# from src.db.config import init_db

# def test_conversation_creation():
#     """Test creating and retrieving a conversation"""
#     print("Testing conversation creation and retrieval...")
    
#     # Initialize the database (this will import all models)
#     init_db()
    
#     # Check if there are any existing conversations
#     existing_conversations = Conversation.get_all()
#     print(f"Existing conversations: {len(existing_conversations)}")
    
#     if existing_conversations:
#         print(f"Existing conversation IDs: {[c.id for c in existing_conversations]}")
#         # Try to get the first conversation
#         first_conv = Conversation.get(existing_conversations[0].id)
#         if first_conv:
#             print(f"Successfully retrieved conversation {first_conv.id}")
#         else:
#             print("Failed to retrieve existing conversation")
    
#     # Try to create a new conversation (this might fail if we don't have proper data)
#     try:
#         # First create a customer
#         customer = Customer.create(
#             name="test-customer",
#             organization_id=1,  # Assuming organization 1 exists
#             ip_address="127.0.0.1"
#         )
#         print(f"Created customer with ID: {customer.id}")
        
#         # Then create a conversation
#         conversation = Conversation.create(
#             name="test-conversation",
#             customer_id=customer.id,
#             organization_id=1,
#             ip_address="127.0.0.1"
#         )
#         print(f"Created conversation with ID: {conversation.id}")
        
#         # Try to retrieve it
#         retrieved_conv = Conversation.get(conversation.id)
#         if retrieved_conv:
#             print(f"Successfully retrieved conversation {retrieved_conv.id}")
#         else:
#             print("Failed to retrieve newly created conversation")
            
#     except Exception as e:
#         print(f"Error creating test data: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     test_conversation_creation() 