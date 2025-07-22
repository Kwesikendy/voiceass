#!/usr/bin/env python3
"""
🔗 WhatsApp Contact Helper for Myra
Simplified interface for WhatsApp messaging integration
"""

from myra_vcf_contacts import find_contact_by_name, initialize_contact_manager
import re

def get_whatsapp_contact(name: str, speak_func=None):
    """
    Simple function for Myra to get contact info for WhatsApp
    
    Args:
        name (str): Name to search for
        speak_func: Optional function to speak messages
        
    Returns:
        dict: Contact info with name and phone, or None if not found
    """
    try:
        # Initialize if needed
        initialize_contact_manager()
        
        # Find contact
        result = find_contact_by_name(name, speak_func)
        
        if result:
            contact_name, phone = result
            
            # Clean phone number for WhatsApp
            clean_phone = clean_phone_for_whatsapp(phone)
            
            return {
                'name': contact_name,
                'phone': phone,
                'whatsapp_phone': clean_phone,
                'whatsapp_url': f"https://wa.me/{clean_phone}",
                'found': True
            }
        else:
            return {
                'name': name,
                'found': False,
                'error': f"No contact found matching '{name}'"
            }
            
    except Exception as e:
        return {
            'name': name,
            'found': False,
            'error': f"Error searching for contact: {str(e)}"
        }

def clean_phone_for_whatsapp(phone: str) -> str:
    """Clean phone number for WhatsApp API format"""
    if not phone:
        return ""
    
    # Remove all non-digits except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Remove leading + if present
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Ensure it starts with country code
    if cleaned.startswith('0') and len(cleaned) > 9:
        # Looks like Ghana number starting with 0, replace with 233
        cleaned = '233' + cleaned[1:]
    elif not cleaned.startswith('233') and len(cleaned) == 9:
        # Looks like Ghana number without country code
        cleaned = '233' + cleaned
    
    return cleaned

def list_recent_contacts(limit: int = 10):
    """Get a list of contacts for Myra to reference"""
    try:
        from myra_vcf_contacts import contact_manager
        if contact_manager:
            return contact_manager.list_all_contacts(limit)
        return []
    except:
        return []

if __name__ == "__main__":
    # Test the WhatsApp helper
    print("🔗 Testing WhatsApp Contact Helper")
    print("=" * 40)
    
    test_names = ["Miss Ofori", "Valeria", "John", "NonExistent"]
    
    for name in test_names:
        print(f"\n📱 Testing: {name}")
        result = get_whatsapp_contact(name)
        
        if result['found']:
            print(f"  ✅ Found: {result['name']}")
            print(f"  📞 Phone: {result['phone']}")
            print(f"  🔗 WhatsApp: {result['whatsapp_url']}")
        else:
            print(f"  ❌ {result['error']}")
