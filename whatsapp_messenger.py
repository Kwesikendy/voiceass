#!/usr/bin/env python3
"""
🤖 Complete WhatsApp Messenger for Myra
Full workflow: Contact search → Message input → Send via WhatsApp
"""

import webbrowser
import urllib.parse
import time
import os
import subprocess
import platform
from whatsapp_contact_helper import get_whatsapp_contact

def send_whatsapp_message(contact_name, message_text=None, speak_function=None, listen_function=None):
    """
    Complete WhatsApp messaging workflow for Myra
    
    Args:
        contact_name (str): Name to search for
        message_text (str, optional): Pre-written message 
        speak_function: Function for Myra to speak (optional)
        listen_function: Function for Myra to listen (optional)
    
    Returns:
        dict: Result of the messaging attempt
    """
    
    # Step 1: Find the contact with voice functions for multiple selection
    if speak_function:
        speak_function(f"Searching for {contact_name} in your contacts...")
    
    # Pass voice functions to enable multiple contact selection
    from myra_vcf_contacts import find_contact_by_name
    
    # Use the direct contact search with voice functions
    contact_search_result = find_contact_by_name(contact_name, speak_function, listen_function)
    
    if not contact_search_result:
        error_msg = f"I couldn't find {contact_name} in your contacts. Could you check the name?"
        if speak_function:
            speak_function(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'step': 'contact_search'
        }
    
    # Extract contact details
    found_name, phone_number = contact_search_result
    
    # Format for WhatsApp
    from whatsapp_contact_helper import clean_phone_for_whatsapp
    whatsapp_phone = clean_phone_for_whatsapp(phone_number)
    
    contact_result = {
        'found': True,
        'name': found_name,
        'phone': phone_number,
        'whatsapp_phone': whatsapp_phone,
        'whatsapp_url': f"https://wa.me/{whatsapp_phone}"
    }
    
    found_name = contact_result['name']
    whatsapp_phone = contact_result['whatsapp_phone']
    
    # Step 2: Confirm contact and get message
    if speak_function:
        speak_function(f"Found contact: {found_name}. What message would you like to send?")
    
    # Get message from user if not provided
    if not message_text:
        if listen_function:
            try:
                message_text = listen_function()
                if not message_text or message_text.strip() == "":
                    error_msg = "I didn't get any message. Please try again."
                    if speak_function:
                        speak_function(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'step': 'message_input'
                    }
            except Exception as e:
                error_msg = f"I couldn't hear your message. Error: {str(e)}"
                if speak_function:
                    speak_function(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'step': 'message_input'
                }
        else:
            # Fallback for testing without voice
            message_text = input(f"Enter message for {found_name}: ")
    
    # Step 3: Create WhatsApp URL with message
    encoded_message = urllib.parse.quote(message_text)
    whatsapp_url = f"https://wa.me/{whatsapp_phone}?text={encoded_message}"
    
    # Step 4: Confirm and send
    if speak_function:
        speak_function(f"Sending message to {found_name}: '{message_text}'")
    
    try:
        # Try to open WhatsApp desktop app first, then fallback to browser
        opened_successfully = open_whatsapp_app(whatsapp_phone, message_text)
        
        if opened_successfully:
            success_msg = f"WhatsApp desktop app opened! Message ready to send to {found_name}."
        else:
            # Fallback to browser if desktop app not available
            webbrowser.open(whatsapp_url)
            success_msg = f"WhatsApp web opened! Message ready to send to {found_name}."
        
        if speak_function:
            speak_function(success_msg)
        
        return {
            'success': True,
            'contact_name': found_name,
            'phone': whatsapp_phone,
            'message': message_text,
            'whatsapp_url': whatsapp_url,
            'step': 'completed'
        }
        
    except Exception as e:
        error_msg = f"Couldn't open WhatsApp. Error: {str(e)}"
        if speak_function:
            speak_function(error_msg)
        return {
            'success': False,
            'error': error_msg,
            'step': 'whatsapp_open',
            'contact_name': found_name,
            'message': message_text
        }

def open_whatsapp_app(phone_number, message):
    """
    Try to open WhatsApp desktop app with pre-filled message
    
    Args:
        phone_number (str): Phone number in international format (without +)
        message (str): Message to pre-fill
    
    Returns:
        bool: True if successfully opened desktop app, False otherwise
    """
    try:
        encoded_message = urllib.parse.quote(message)
        whatsapp_url = f"whatsapp://send?phone={phone_number}&text={encoded_message}"
        
        system = platform.system().lower()
        
        if system == "windows":
            # Since Windows Store WhatsApp doesn't handle URL protocols well,
            # we'll use the web browser as the most reliable method
            print("Debug: Using web browser for best compatibility with Windows Store WhatsApp")
            return False  # This will trigger the web browser fallback
            
            # Method 4: Last resort - try to find and launch traditional WhatsApp.exe
            possible_paths = [
                os.path.expanduser("~\\AppData\\Local\\WhatsApp\\WhatsApp.exe"),
                "C:\\Program Files\\WhatsApp\\WhatsApp.exe",
                "C:\\Program Files (x86)\\WhatsApp\\WhatsApp.exe",
                os.path.expanduser("~\\AppData\\Local\\Programs\\WhatsApp\\WhatsApp.exe")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    subprocess.Popen([path])
                    time.sleep(2)  # Give WhatsApp time to start
                    # Try to send the URL after WhatsApp starts
                    try:
                        subprocess.run(["cmd", "/c", "start", whatsapp_url], 
                                     capture_output=True, timeout=3)
                        return True
                    except:
                        pass
            
            return False
                
        elif system == "darwin":  # macOS
            subprocess.run(["open", whatsapp_url], check=True, timeout=5)
            return True
            
        elif system == "linux":
            subprocess.run(["xdg-open", whatsapp_url], check=True, timeout=5)
            return True
            
        else:
            return False
            
    except Exception as e:
        print(f"Debug: Failed to open WhatsApp desktop app: {e}")
        return False

def quick_send_whatsapp(contact_name, message_text):
    """
    Quick send function for Myra (no voice functions)
    """
    return send_whatsapp_message(contact_name, message_text)

def demo_voice_workflow():
    """
    Demo of the complete workflow (simulating voice functions)
    """
    print("🤖 MYRA WHATSAPP WORKFLOW DEMO")
    print("=" * 50)
    
    def mock_speak(text):
        print(f"🗣️ Myra: {text}")
    
    def mock_listen():
        return input("🎤 You: ")
    
    # Demo scenarios
    test_contacts = ["Miss Ofori", "Valeria", "Guy"]
    
    for contact in test_contacts:
        print(f"\n📱 Demo: Send WhatsApp to {contact}")
        print("-" * 30)
        
        result = send_whatsapp_message(
            contact_name=contact,
            speak_function=mock_speak,
            listen_function=mock_listen
        )
        
        if result['success']:
            print(f"✅ Success! WhatsApp URL: {result['whatsapp_url'][:60]}...")
        else:
            print(f"❌ Failed: {result['error']}")
        
        print("\n" + "="*50)

def test_quick_send():
    """
    Test quick sending with pre-written messages
    """
    print("⚡ QUICK SEND TEST")
    print("=" * 30)
    
    test_cases = [
        ("Miss Ofori", "Hi! How are you doing?"),
        ("Valeria", "Can we meet tomorrow?"),
        ("Guy", "Thanks for your help earlier!")
    ]
    
    for contact, message in test_cases:
        print(f"\n📤 Sending to {contact}: '{message[:30]}...'")
        result = quick_send_whatsapp(contact, message)
        
        if result['success']:
            print(f"✅ WhatsApp opened for {result['contact_name']}")
            print(f"🔗 URL: {result['whatsapp_url'][:80]}...")
        else:
            print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    print("🤖 Myra WhatsApp Messenger - Complete Workflow")
    print("=" * 60)
    
    print("Choose test mode:")
    print("1. Interactive Demo (simulates voice workflow)")
    print("2. Quick Send Test (pre-written messages)")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_voice_workflow()
    elif choice == "2":
        test_quick_send()  
    elif choice == "3":
        test_quick_send()
        print("\n" + "="*60)
        demo_voice_workflow()
    else:
        print("Running quick test by default...")
        test_quick_send()
