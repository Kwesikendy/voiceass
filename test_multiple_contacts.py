#!/usr/bin/env python3
"""
Test how Myra handles multiple contact matches
"""

from myra_vcf_contacts import VCFContactManager
from whatsapp_messenger import send_whatsapp_message

def test_multiple_matches():
    print("🔍 TESTING MULTIPLE CONTACT MATCHES")
    print("=" * 50)
    
    manager = VCFContactManager()
    
    # Test names that might have multiple matches
    test_names = ["John", "Mary", "Rev", "Prince", "Miss"]
    
    for name in test_names:
        print(f"\n🔍 Searching for '{name}':")
        matches = manager.find_contact(name)
        
        if len(matches) > 1:
            print(f"  Found {len(matches)} matches:")
            for i, (contact_name, similarity) in enumerate(matches, 1):
                phone = manager.get_contact_phone(contact_name)
                print(f"    {i}. {contact_name} - {phone} (similarity: {similarity:.2f})")
        elif len(matches) == 1:
            contact_name, similarity = matches[0]
            phone = manager.get_contact_phone(contact_name)
            print(f"  ✅ Single match: {contact_name} - {phone}")
        else:
            print(f"  ❌ No matches found")

def demo_myra_handling_multiple_contacts():
    print("\n\n🤖 MYRA HANDLING MULTIPLE CONTACTS DEMO")
    print("=" * 60)
    print("User: 'Myra, send WhatsApp message to John'")
    print()
    
    def myra_speaks(text):
        print(f"🤖 Myra: {text}")
    
    def myra_listens():
        response = input("🎤 You say: ")
        print(f"🤖 Myra heard: '{response}'")
        return response
    
    # Test with a name that has multiple matches
    contact_name = "John"
    
    print("🔍 Myra processing...")
    print()
    
    result = send_whatsapp_message(
        contact_name=contact_name,
        message_text=None,
        speak_function=myra_speaks,
        listen_function=myra_listens
    )
    
    print("\n" + "="*50)
    if result['success']:
        print("✅ SUCCESS! Contact selected and message ready!")
        print(f"📱 Selected contact: {result['contact_name']}")
        print(f"💬 Message: '{result['message']}'")
    else:
        print(f"❌ Process stopped: {result['error']}")

def test_contact_selection_logic():
    print("\n\n🧠 CONTACT SELECTION LOGIC TEST")
    print("=" * 50)
    
    manager = VCFContactManager()
    
    # Simulate what happens when multiple contacts are found
    test_scenarios = [
        ("Rev", "Looking for contacts with 'Rev'"),
        ("Prince", "Looking for contacts with 'Prince'"), 
        ("Miss", "Looking for contacts with 'Miss'")
    ]
    
    for search_term, description in test_scenarios:
        print(f"\n📋 {description}:")
        matches = manager.find_contact(search_term)
        
        if len(matches) > 1:
            print(f"  Multiple matches found ({len(matches)}):")
            for i, (name, similarity) in enumerate(matches[:3], 1):  # Show top 3
                print(f"    {i}. {name} (confidence: {similarity:.2f})")
            
            print(f"\n💡 Myra would say:")
            print(f"     'I found {len(matches)} contacts matching {search_term}:'")
            for i, (name, _) in enumerate(matches[:3], 1):
                print(f"     'Option {i}: {name}'")
            print(f"     'Which contact would you like? Say the number or full name.'")
            
        elif len(matches) == 1:
            name = matches[0][0]
            print(f"  ✅ Single match: {name}")
            print(f"  💡 Myra would say: 'Found contact: {name}. What message?'")
        else:
            print(f"  ❌ No matches")
            print(f"  💡 Myra would say: 'I couldn't find {search_term} in your contacts.'")

if __name__ == "__main__":
    print("🤖 MYRA MULTIPLE CONTACTS HANDLING")
    print("=" * 60)
    
    # Test what multiple matches look like
    test_multiple_matches()
    
    # Test the selection logic
    test_contact_selection_logic()
    
    print(f"\n📋 HOW MYRA HANDLES MULTIPLE CONTACTS:")
    print("=" * 60)
    print("1️⃣ User says: 'Send message to John'")
    print("2️⃣ Myra searches and finds multiple 'John's")
    print("3️⃣ Myra lists options: 'I found 3 contacts: 1. Johnson, 2. John Smith...'")
    print("4️⃣ Myra asks: 'Which contact? Say the number or full name.'")
    print("5️⃣ User responds: 'Number 2' or 'John Smith'")
    print("6️⃣ Myra selects contact and asks for message")
    print("7️⃣ Process continues normally")
    
    print(f"\n🔧 The system already handles this automatically!")
    print("✅ Multiple matches → Myra lists options")
    print("✅ User selects → Process continues")
    print("✅ Single match → Goes straight to message")
    print("✅ No matches → Asks user to check name")
    
    # Run interactive demo
    print(f"\n🎮 Want to try the interactive demo? (y/n)")
    if input().lower().startswith('y'):
        demo_myra_handling_multiple_contacts()
