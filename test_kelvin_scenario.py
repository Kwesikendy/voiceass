#!/usr/bin/env python3
"""
Test Myra handling multiple Kelvin contacts
Exact scenario: User says "Myra, send a message to Kelvin"
"""

from myra_vcf_contacts import VCFContactManager
from whatsapp_messenger import send_whatsapp_message

def check_kelvin_contacts():
    """First, let's see what Kelvin contacts exist"""
    print("🔍 CHECKING FOR KELVIN CONTACTS")
    print("=" * 50)
    
    manager = VCFContactManager()
    matches = manager.find_contact("Kelvin")
    
    print(f"Found {len(matches)} contacts matching 'Kelvin':")
    for i, (name, similarity) in enumerate(matches, 1):
        phone = manager.get_contact_phone(name)
        print(f"  {i}. {name} - {phone} (similarity: {similarity:.2f})")
    
    return matches

def simulate_myra_kelvin_scenario():
    """
    Simulate the exact scenario:
    User: "Myra, send a message to Kelvin" 
    """
    print("\n\n🤖 MYRA KELVIN SCENARIO SIMULATION")
    print("=" * 60)
    print("👤 User: 'Myra, send a message to Kelvin'")
    print()
    
    def myra_speaks(text):
        print(f"🤖 Myra: {text}")
    
    def myra_listens():
        response = input("🎤 You respond: ")
        print(f"🤖 Myra heard: '{response}'")
        return response
    
    print("🔍 Myra is processing your request...")
    print()
    
    # This is exactly what Myra would do
    result = send_whatsapp_message(
        contact_name="Kelvin",
        message_text=None,  # Will ask for message
        speak_function=myra_speaks,
        listen_function=myra_listens
    )
    
    print("\n" + "="*60)
    if result['success']:
        print("🎉 SUCCESS! Myra completed the workflow!")
        print(f"📱 Selected contact: {result['contact_name']}")
        print(f"📞 Phone: {result['phone']}")
        print(f"💬 Message: '{result['message']}'")
        print(f"🔗 WhatsApp URL generated: {result['whatsapp_url'][:80]}...")
        print("\n✅ WhatsApp will open with the message ready to send!")
    else:
        print(f"❌ Workflow failed: {result['error']}")
        print(f"🔧 Failed at step: {result.get('step', 'unknown')}")

def show_expected_flow():
    """Show what should happen"""
    print("\n\n📋 EXPECTED WORKFLOW")
    print("=" * 50)
    print("1️⃣ User: 'Myra, send a message to Kelvin'")
    print("2️⃣ Myra: 'Searching for Kelvin in your contacts...'")
    print("3️⃣ Myra: 'I found X contacts matching Kelvin:'")
    print("   'Option 1: Kelvin Johnson'")
    print("   'Option 2: Kelvin Smith'") 
    print("   'Option 3: Kelvin Doe'")
    print("   'Which contact would you like? Say the number or full name.'")
    print("4️⃣ User: 'Number 1' or 'Kelvin Johnson'")
    print("5️⃣ Myra: 'Found contact: Kelvin Johnson. What message would you like to send?'")
    print("6️⃣ User: 'Hey Kelvin, how are you?'")
    print("7️⃣ Myra: 'Sending message to Kelvin Johnson: Hey Kelvin, how are you?'")
    print("8️⃣ Myra: 'WhatsApp opened! Message ready to send to Kelvin Johnson.'")
    print("9️⃣ WhatsApp opens with message pre-filled → User clicks SEND")

if __name__ == "__main__":
    print("🎯 TESTING KELVIN SCENARIO")
    print("=" * 60)
    print("This tests exactly what you described:")
    print("User says: 'Myra, send a message to Kelvin'")
    print("Multiple Kelvins exist → Myra handles the selection")
    print()
    
    # First check what Kelvin contacts exist
    kelvin_matches = check_kelvin_contacts()
    
    if len(kelvin_matches) == 0:
        print("\n❌ No Kelvin contacts found in your database.")
        print("💡 You can add a Kelvin contact to test, or try another name like 'John' or 'Rev'")
    elif len(kelvin_matches) == 1:
        print(f"\n✅ Only one Kelvin found: {kelvin_matches[0][0]}")
        print("💡 Myra would go straight to asking for the message")
        print("\n🎮 Let's test the workflow:")
        simulate_myra_kelvin_scenario()
    else:
        print(f"\n✅ Perfect! Found {len(kelvin_matches)} Kelvin contacts")
        print("💡 Myra will ask you to choose which one")
        print("\n🎮 Let's test the multiple contact selection:")
        simulate_myra_kelvin_scenario()
    
    # Show what the expected flow should be
    show_expected_flow()
