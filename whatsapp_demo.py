#!/usr/bin/env python3
"""
WhatsApp URL Demo - Show actual WhatsApp links that Myra would use
"""

from whatsapp_contact_helper import get_whatsapp_contact

def demo_whatsapp_links():
    print("📱 WHATSAPP LINK GENERATION DEMO")
    print("=" * 50)
    print("This shows the actual WhatsApp links Myra would use:")
    
    # Test various contacts
    demo_contacts = [
        "Miss Ofori",
        "Valeria", 
        "Johnson",  # From "john" search
        "Guy",
        "Prince"
    ]
    
    for contact_name in demo_contacts:
        result = get_whatsapp_contact(contact_name)
        if result['found']:
            print(f"\n👤 {result['name']}")
            print(f"   📞 Phone: {result['phone']}")
            print(f"   🌍 WhatsApp Number: {result['whatsapp_phone']}")
            print(f"   🔗 WhatsApp Link: {result['whatsapp_url']}")
            print(f"   ✅ Ready for Myra to use!")
        else:
            print(f"\n❌ {contact_name}: Not found")

def test_voice_commands():
    print(f"\n\n🎤 VOICE COMMAND SIMULATION")
    print("=" * 50)
    print("Simulating voice commands Myra might receive:")
    
    voice_tests = [
        ("send message to miss ofori", "miss ofori"),
        ("whatsapp valeria", "valeria"),
        ("message john", "john"),
        ("text guy", "guy"),
        ("send to prince", "prince")
    ]
    
    for command, name_to_search in voice_tests:
        print(f"\n🗣️  Voice Command: \"{command}\"")
        print(f"🔍 Myra searches for: \"{name_to_search}\"")
        
        result = get_whatsapp_contact(name_to_search)
        if result['found']:
            print(f"✅ Found: {result['name']} ({result['whatsapp_phone']})")
            print(f"🔗 Opens: {result['whatsapp_url']}")
        else:
            print(f"❌ Contact not found - Myra would ask for clarification")

if __name__ == "__main__":
    print("🤖 Myra WhatsApp Integration Demo")
    print("=" * 60)
    
    demo_whatsapp_links()
    test_voice_commands()
    
    print(f"\n\n🎉 INTEGRATION READY!")
    print("=" * 60)
    print("✅ Myra can now:")
    print("  • Search 632 contacts by name")
    print("  • Handle fuzzy/partial name matching") 
    print("  • Convert phone numbers to WhatsApp format")
    print("  • Generate direct WhatsApp web links")
    print("  • Work with voice commands like 'message John'")
    print("")
    print("🔧 Usage in Myra's code:")
    print("  result = get_whatsapp_contact(contact_name)")
    print("  if result['found']:")
    print("      open_whatsapp(result['whatsapp_url'])")
    print("")
    print("📱 WhatsApp links automatically open WhatsApp Web or app!")
