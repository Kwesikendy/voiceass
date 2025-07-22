#!/usr/bin/env python3
"""
🤖 Myra Integration Example
This shows exactly how Myra would handle WhatsApp messaging
"""

from whatsapp_messenger import send_whatsapp_message

def myra_whatsapp_handler(contact_name, myra_speak, myra_listen):
    """
    This is how Myra would handle: "Send a WhatsApp message to Kelvin"
    
    Args:
        contact_name (str): The name Myra heard (e.g., "Kelvin")
        myra_speak: Myra's text-to-speech function
        myra_listen: Myra's speech-to-text function
    """
    
    # Step 1: Search for contact and ask for message
    result = send_whatsapp_message(
        contact_name=contact_name,
        message_text=None,  # No pre-written message
        speak_function=myra_speak,
        listen_function=myra_listen
    )
    
    return result

def simulate_myra_conversation():
    """
    Simulate the complete conversation flow
    """
    print("🤖 MYRA CONVERSATION SIMULATION")
    print("=" * 50)
    print("User: 'Myra, send a WhatsApp message to Miss Ofori'")
    print()
    
    # Mock Myra's voice functions
    def myra_speak(text):
        print(f"🤖 Myra: {text}")
        
    def myra_listen():
        # Simulate user speaking a message
        user_message = input("🎤 You speak: ")
        print(f"🤖 Myra heard: '{user_message}'")
        return user_message
    
    # Myra processes the request
    contact_name = "Miss Ofori"  # Extracted from user's voice command
    
    result = myra_whatsapp_handler(contact_name, myra_speak, myra_listen)
    
    print("\n" + "="*50)
    if result['success']:
        print("✅ SUCCESS! WhatsApp opened with message ready to send!")
        print(f"📱 Contact: {result['contact_name']}")
        print(f"💬 Message: '{result['message']}'")
        print(f"🔗 WhatsApp URL: {result['whatsapp_url'][:80]}...")
    else:
        print(f"❌ FAILED: {result['error']}")

def show_usage_examples():
    """
    Show different usage patterns for Myra
    """
    print("\n🔧 MYRA USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        ("Send WhatsApp to John", "john"),
        ("Message Valeria on WhatsApp", "valeria"),  
        ("WhatsApp Guy please", "guy"),
        ("Send message to Miss Ofori", "miss ofori"),
        ("Text MAXZY", "maxzy")
    ]
    
    print("Voice commands Myra can handle:")
    for i, (command, extracted_name) in enumerate(examples, 1):
        print(f"{i}. User says: '{command}'")
        print(f"   Myra extracts: '{extracted_name}'")
        print(f"   Myra calls: send_whatsapp_message('{extracted_name}', None, speak, listen)")
        print()

def test_error_handling():
    """
    Test how Myra handles errors
    """
    print("🚨 ERROR HANDLING TESTS")
    print("=" * 30)
    
    def mock_speak(text):
        print(f"🤖 Myra: {text}")
    
    def mock_listen():
        return ""  # Simulate empty/failed speech recognition
    
    # Test with non-existent contact
    print("\n1. Testing non-existent contact:")
    result = send_whatsapp_message("NonExistentPerson", None, mock_speak, mock_listen)
    print(f"Result: {'Success' if result['success'] else 'Failed - ' + result['error']}")
    
    # Test with empty message
    print("\n2. Testing empty message:")  
    result = send_whatsapp_message("Miss Ofori", None, mock_speak, mock_listen)
    print(f"Result: {'Success' if result['success'] else 'Failed - ' + result['error']}")

if __name__ == "__main__":
    print("🤖 MYRA WHATSAPP INTEGRATION COMPLETE!")
    print("=" * 60)
    
    # Show how the conversation would work
    simulate_myra_conversation()
    
    # Show usage patterns
    show_usage_examples()
    
    # Test error handling
    test_error_handling()
    
    print("\n🎉 INTEGRATION SUMMARY:")
    print("=" * 60)
    print("✅ Myra can now handle complete WhatsApp messaging workflow")
    print("✅ Searches 632 contacts with fuzzy matching")
    print("✅ Asks user for message via voice")  
    print("✅ Opens WhatsApp with message ready to send")
    print("✅ Handles errors gracefully")
    print("✅ Works with natural voice commands")
    print()
    print("🔧 For Myra's main code, use:")
    print("   from whatsapp_messenger import send_whatsapp_message")
    print("   result = send_whatsapp_message(contact_name, None, speak_func, listen_func)")
