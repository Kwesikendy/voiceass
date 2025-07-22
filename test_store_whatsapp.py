#!/usr/bin/env python3
"""
Test updated WhatsApp Store version integration
"""

from whatsapp_messenger import send_whatsapp_message

def test_store_whatsapp():
    print("🏪 TESTING WINDOWS STORE WHATSAPP INTEGRATION")
    print("=" * 60)
    print("👤 User: 'Myra, send a WhatsApp message to Kelvin'")
    print("🎯 Expected: Myra should open Windows Store WhatsApp (not the old version)")
    print()
    
    def myra_speaks(text):
        print(f"🤖 Myra: {text}")
    
    def myra_listens():
        response = input("🎤 You say: ")
        print(f"🤖 Myra heard: '{response}'")
        return response
    
    print("🔍 Starting the workflow...")
    print()
    
    result = send_whatsapp_message(
        contact_name="Kelvin",
        message_text=None,
        speak_function=myra_speaks,
        listen_function=myra_listens
    )
    
    print("\n" + "="*60)
    if result['success']:
        print("🎉 SUCCESS! WhatsApp workflow completed!")
        print(f"📱 Contact: {result['contact_name']}")
        print(f"💬 Message: '{result['message']}'")
        print(f"🔗 WhatsApp URL: {result['whatsapp_url'][:80]}...")
        print()
        print("🏪 Check if the correct Windows Store WhatsApp opened!")
        print("✅ If it's the modern app (no update prompts) - SUCCESS!")
        print("❌ If it's the old desktop app (asks for updates) - Need more tweaks")
    else:
        print(f"❌ Workflow failed: {result['error']}")

if __name__ == "__main__":
    print("🧪 WINDOWS STORE WHATSAPP TEST")
    print("=" * 70)
    print("This test will help determine if Myra opens the correct WhatsApp version")
    print()
    
    test_store_whatsapp()
    
    print(f"\n📋 WHAT TO CHECK:")
    print("=" * 70)
    print("After the test runs:")
    print("1. ✅ Does WhatsApp open without asking for updates?")
    print("2. ✅ Is it the modern Windows Store interface?")
    print("3. ✅ Is the message pre-filled correctly?")
    print("4. ✅ Can you send the message normally?")
    print()
    print("If all ✅ - Myra is using the correct WhatsApp!")
    print("If any ❌ - We may need to adjust the launch method.")
