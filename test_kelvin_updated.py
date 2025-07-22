#!/usr/bin/env python3
"""
Test the updated Kelvin scenario - Myra should now ask you to choose
"""

from whatsapp_messenger import send_whatsapp_message

def test_kelvin_multiple_selection():
    print("🎯 UPDATED KELVIN SELECTION TEST")
    print("=" * 60)
    print("👤 User: 'Myra, send a WhatsApp message to Kelvin'")
    print("🔧 System has been updated to ALWAYS ask when multiple matches exist")
    print()
    
    def myra_speaks(text):
        print(f"🤖 Myra: {text}")
    
    def myra_listens():
        response = input("🎤 You say: ")
        print(f"🤖 Myra heard: '{response}'")
        return response
    
    print("🔍 Let's see what happens now...")
    print()
    
    result = send_whatsapp_message(
        contact_name="Kelvin",
        message_text=None,
        speak_function=myra_speaks,
        listen_function=myra_listens
    )
    
    print("\n" + "="*60)
    if result['success']:
        print("🎉 SUCCESS! Myra asked you to choose!")
        print(f"📱 You selected: {result['contact_name']}")
        print(f"💬 Message: '{result['message']}'")
        print(f"🔗 WhatsApp URL: {result['whatsapp_url'][:80]}...")
        print("\n✅ Perfect! This is exactly what you wanted!")
    else:
        print(f"❌ Something went wrong: {result['error']}")

if __name__ == "__main__":
    print("🔧 TESTING UPDATED MULTIPLE SELECTION BEHAVIOR")
    print("=" * 70)
    print()
    print("Expected behavior:")
    print("1. Myra searches for 'Kelvin'")
    print("2. Myra finds multiple Kelvin contacts")
    print("3. Myra says: 'I found X contacts matching Kelvin:'")
    print("4. Myra lists: 'Option 1: Kelvin', 'Option 2: KELVIN LAMPTEY', etc.")
    print("5. Myra asks: 'Which contact would you like?'")
    print("6. You choose by saying number or name")
    print("7. Myra asks for your message")
    print("8. Workflow continues normally")
    print()
    print("Let's test it:")
    print("="*70)
    
    test_kelvin_multiple_selection()
