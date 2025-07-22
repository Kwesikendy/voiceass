#!/usr/bin/env python3
"""
Force the multiple Kelvin selection scenario
"""

from whatsapp_messenger import send_whatsapp_message

def test_multiple_kelvin_selection():
    """
    Test what happens when we search in a way that forces multiple selection
    """
    print("🧪 FORCING MULTIPLE KELVIN SELECTION")
    print("=" * 60)
    print("Let's see what happens when we search for 'Kel' instead of exact 'Kelvin'")
    print("This should trigger the multiple selection dialog")
    print()
    
    def myra_speaks(text):
        print(f"🤖 Myra: {text}")
    
    def myra_listens():
        response = input("🎤 You say: ")
        print(f"🤖 Myra heard: '{response}'")
        return response
    
    # Search for "Kel" to get multiple Kelvin matches
    contact_search = "Kel"
    
    print(f"👤 User: 'Myra, send WhatsApp to {contact_search}'")
    print("🔍 This should show multiple Kelvin options...")
    print()
    
    result = send_whatsapp_message(
        contact_name=contact_search,
        message_text=None,
        speak_function=myra_speaks,
        listen_function=myra_listens
    )
    
    print("\n" + "="*60)
    if result['success']:
        print("🎉 SUCCESS! Multiple selection workflow worked!")
        print(f"📱 Final selected contact: {result['contact_name']}")
        print(f"💬 Message: '{result['message']}'")
        print(f"🔗 WhatsApp URL: {result['whatsapp_url'][:80]}...")
    else:
        print(f"❌ Failed: {result['error']}")

def show_all_kelvin_matches():
    """Show all the Kelvin contacts found"""
    from myra_vcf_contacts import VCFContactManager
    
    print("\n📋 ALL KELVIN-RELATED CONTACTS:")
    print("=" * 50)
    
    manager = VCFContactManager()
    kelvin_matches = manager.find_contact("Kelvin")
    
    print("🔍 Searching for 'Kelvin' (exact):")
    for i, (name, similarity) in enumerate(kelvin_matches, 1):
        phone = manager.get_contact_phone(name)
        print(f"  {i}. {name} - {phone} (similarity: {similarity:.2f})")
    
    print(f"\n🔍 Searching for 'Kel' (partial):")
    kel_matches = manager.find_contact("Kel")
    for i, (name, similarity) in enumerate(kel_matches, 1):
        phone = manager.get_contact_phone(name)
        print(f"  {i}. {name} - {phone} (similarity: {similarity:.2f})")

if __name__ == "__main__":
    print("🎯 MULTIPLE KELVIN SELECTION TEST")
    print("=" * 60)
    
    # First show what contacts exist
    show_all_kelvin_matches()
    
    print(f"\n💡 EXPLANATION:")
    print("When you said 'send to Kelvin', the system found an EXACT match")
    print("('Kelvin' with 1.00 similarity) so it selected it automatically.")
    print("To trigger multiple selection, we need a less exact search...")
    print()
    
    # Test the multiple selection
    test_multiple_kelvin_selection()
