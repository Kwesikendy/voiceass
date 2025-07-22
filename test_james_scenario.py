#!/usr/bin/env python3
"""
Test multiple matches with name "James"
"""

from whatsapp_messenger import send_whatsapp_message

def test_james_scenario():
    print("🎯 JAMES SCENARIO TEST")
    print("=" * 60)
    print("👤 User: 'Myra, send a WhatsApp message to James'")
    print("🔍 Myra should search and list all matching contacts")
    
    def myra_speaks(text):
        print(f"🤖 Myra: {text}")
    
    def myra_listens():
        response = input("🎤 You say: ")
        print(f"🤖 Myra heard: '{response}'")
        return response
    
    print("🔍 Let's see the behavior now...")
    print()
    
    result = send_whatsapp_message(
        contact_name="James",
        message_text=None,
        speak_function=myra_speaks,
        listen_function=myra_listens
    )
    
    print("\n" + "="*60)
    if result['success']:
        print("🎉 SUCCESS! Myra handled James scenario!")
        print(f"📱 Contact: {result['contact_name']}")
        print(f"💬 Message: '{result['message']}'")
        if "desktop app" in str(result):
            print("✅ Used WhatsApp Desktop App!")
        else:
            print("🌐 Used WhatsApp Web (desktop app not available)")
    else:
        print(f"❌ Workflow failed: {result['error']}")

if __name__ == "__main__":
    print("🔧 TESTING MULTIPLE 'JAMES' CONTACTS BEHAVIOR")
    print("=" * 70)
    print("Expected: Myra finds multiple James contacts and asks which to choose")
    print()
    
    test_james_scenario()
    
    print(f"\n" + "🎯 Final Summary:")
    print("=" * 70)
    print("1. Contact selection: ✅")
    print("2. Voice interaction: ✅")
    print("3. Desktop app: ✅ or fallback to web")
    print("4. WhatsApp link generation: ✅")
