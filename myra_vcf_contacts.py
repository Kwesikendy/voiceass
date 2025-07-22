#!/usr/bin/env python3
"""
📞 Myra VCF Contact Manager
Handles parsing and managing contacts from VCF files for WhatsApp integration
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

class VCFContactManager:
    def __init__(self, vcf_file_path: str = "Contacts.vcf"):
        self.vcf_file_path = vcf_file_path
        self.contacts = {}
        self.load_contacts()
    
    def parse_vcf_simple(self, file_path: str) -> Dict[str, Dict[str, str]]:
        """Parse VCF file without external dependencies"""
        contacts = {}
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                current_contact = {}
                
                for line in file:
                    line = line.strip()
                    
                    if line == "BEGIN:VCARD":
                        current_contact = {}
                    
                    elif line == "END:VCARD":
                        if current_contact.get('name') and current_contact.get('phone'):
                            contacts[current_contact['name']] = current_contact
                    
                    elif line.startswith('FN:'):
                        # Full Name
                        name = line[3:].strip()
                        current_contact['name'] = name
                    
                    elif line.startswith('TEL'):
                        # Phone number - extract from various formats
                        phone = self.extract_phone_number(line)
                        if phone:
                            current_contact['phone'] = phone
                    
                    elif line.startswith('N:'):
                        # Structured name - fallback if no FN
                        if 'name' not in current_contact:
                            name_parts = line[2:].split(';')
                            if len(name_parts) >= 2:
                                # Last name, First name format
                                last_name = name_parts[0].strip()
                                first_name = name_parts[1].strip()
                                if first_name and last_name:
                                    current_contact['name'] = f"{first_name} {last_name}"
                                elif first_name:
                                    current_contact['name'] = first_name
                                elif last_name:
                                    current_contact['name'] = last_name
        
        except Exception as e:
            print(f"Error parsing VCF file: {e}")
            
        return contacts
    
    def extract_phone_number(self, tel_line: str) -> Optional[str]:
        """Extract phone number from TEL line"""
        try:
            # Handle different TEL formats
            if ':' in tel_line:
                phone = tel_line.split(':', 1)[1].strip()
            else:
                return None
            
            # Clean up the phone number
            phone = re.sub(r'[^\d+]', '', phone)
            
            # Skip very short or invalid numbers
            if len(phone) < 7:
                return None
                
            return phone
            
        except:
            return None
    
    def load_contacts(self):
        """Load contacts from VCF file"""
        if os.path.exists(self.vcf_file_path):
            self.contacts = self.parse_vcf_simple(self.vcf_file_path)
            print(f"✅ Loaded {len(self.contacts)} contacts from VCF file")
            
            # Display first few contacts for verification
            if self.contacts:
                print("📋 Sample contacts:")
                for i, (name, info) in enumerate(list(self.contacts.items())[:5]):
                    print(f"  {i+1}. {name}: {info.get('phone', 'No phone')}")
                if len(self.contacts) > 5:
                    print(f"  ... and {len(self.contacts) - 5} more contacts")
        else:
            print(f"⚠️ VCF file not found: {self.vcf_file_path}")
    
    def find_contact(self, search_name: str) -> List[Tuple[str, float]]:
        """Find contacts by name with fuzzy matching"""
        matches = []
        search_name_lower = search_name.lower().strip()
        
        for contact_name in self.contacts.keys():
            contact_name_lower = contact_name.lower()
            
            # Exact match
            if search_name_lower == contact_name_lower:
                matches.append((contact_name, 1.0))
                continue
            
            # Partial match
            if search_name_lower in contact_name_lower or contact_name_lower in search_name_lower:
                matches.append((contact_name, 0.8))
                continue
            
            # Word-based matching
            search_words = set(search_name_lower.split())
            contact_words = set(contact_name_lower.split())
            
            if search_words.intersection(contact_words):
                similarity = len(search_words.intersection(contact_words)) / len(search_words.union(contact_words))
                if similarity > 0.5:
                    matches.append((contact_name, similarity))
                    continue
            
            # Fuzzy string matching
            similarity = SequenceMatcher(None, search_name_lower, contact_name_lower).ratio()
            if similarity > 0.6:
                matches.append((contact_name, similarity))
        
        # Sort by similarity score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    def get_contact_phone(self, contact_name: str) -> Optional[str]:
        """Get phone number for a specific contact"""
        if contact_name in self.contacts:
            return self.contacts[contact_name].get('phone')
        return None
    
    def search_and_select_contact(self, search_name: str, speak_function=None, listen_function=None) -> Optional[Tuple[str, str]]:
        """Search for contact and handle multiple matches"""
        matches = self.find_contact(search_name)
        
        if not matches:
            if speak_function:
                speak_function(f"I couldn't find any contacts matching '{search_name}' in your contact list.")
            return None
        
        # MODIFIED: With voice functions, always show choices when multiple matches exist
        # Only auto-select if there's exactly 1 match OR no voice functions
        if len(matches) == 1:
            contact_name = matches[0][0]
            phone = self.get_contact_phone(contact_name)
            if speak_function:
                speak_function(f"Found contact: {contact_name}")
            return (contact_name, phone)
        
        # Force multiple selection when voice functions are present
        # This ensures Myra always asks the user to choose from multiple contacts
        if not (speak_function and listen_function):
            # No voice interface, return best match
            contact_name = matches[0][0]
            phone = self.get_contact_phone(contact_name)
            return (contact_name, phone)
        
        # Multiple matches - ALWAYS ask user to choose
        if speak_function and listen_function:
            speak_function(f"I found {len(matches)} contacts matching '{search_name}':")
            
            for i, (name, similarity) in enumerate(matches, 1):
                speak_function(f"Option {i}: {name}")
            
            speak_function("Which contact would you like? Say the number or the full name.")
            
            # Listen for user's choice
            for attempt in range(3):
                try:
                    response = listen_function()
                    if response:
                        response_lower = response.lower().strip()
                        
                        # Check if user said a number
                        for i, (name, _) in enumerate(matches, 1):
                            if str(i) in response_lower or f"option {i}" in response_lower:
                                phone = self.get_contact_phone(name)
                                return (name, phone)
                        
                        # Check if user said a name
                        for name, _ in matches:
                            if name.lower() in response_lower:
                                phone = self.get_contact_phone(name)
                                return (name, phone)
                        
                        # Fuzzy match the response
                        best_match = None
                        best_similarity = 0
                        for name, _ in matches:
                            similarity = SequenceMatcher(None, response_lower, name.lower()).ratio()
                            if similarity > best_similarity and similarity > 0.6:
                                best_similarity = similarity
                                best_match = name
                        
                        if best_match:
                            phone = self.get_contact_phone(best_match)
                            return (best_match, phone)
                
                except Exception as e:
                    print(f"Error in contact selection: {e}")
                
                if attempt < 2:
                    speak_function("I didn't understand. Please say the number or contact name again.")
            
            # Default to first match
            contact_name = matches[0][0]
            phone = self.get_contact_phone(contact_name)
            speak_function(f"I'll select the first option: {contact_name}")
            return (contact_name, phone)
        
        else:
            # No voice interface, return first match
            contact_name = matches[0][0]
            phone = self.get_contact_phone(contact_name)
            return (contact_name, phone)
    
    def list_all_contacts(self, limit: int = 10) -> List[str]:
        """List all contacts (for debugging/testing)"""
        return list(self.contacts.keys())[:limit]
    
    def get_contact_info(self, contact_name: str) -> Optional[Dict[str, str]]:
        """Get full contact information"""
        return self.contacts.get(contact_name)

# Global contact manager instance
contact_manager = None

def initialize_contact_manager(vcf_path: str = "Contacts.vcf"):
    """Initialize the global contact manager"""
    global contact_manager
    contact_manager = VCFContactManager(vcf_path)
    return contact_manager

def find_contact_by_name(name: str, speak_function=None, listen_function=None) -> Optional[Tuple[str, str]]:
    """Convenience function to find contact"""
    if not contact_manager:
        initialize_contact_manager()
    
    return contact_manager.search_and_select_contact(name, speak_function, listen_function)

if __name__ == "__main__":
    # Test the VCF contact manager
    print("📞 Testing VCF Contact Manager")
    print("=" * 40)
    
    # Initialize manager
    manager = VCFContactManager()
    
    # Test contact search
    test_names = ["John", "Mary", "Service"]
    
    for test_name in test_names:
        print(f"\n🔍 Searching for '{test_name}':")
        matches = manager.find_contact(test_name)
        
        if matches:
            for name, similarity in matches:
                phone = manager.get_contact_phone(name)
                print(f"  - {name}: {phone} (similarity: {similarity:.2f})")
        else:
            print("  No matches found")
