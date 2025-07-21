#!/usr/bin/env python3
"""
🧠 Myra Fuzzy Keyword Matcher
Utility for testing and configuring fuzzy matching
"""
from difflib import SequenceMatcher
import json
import os

class FuzzyKeywordMatcher:
    def __init__(self, keywords_file=None):
        """Initialize with keywords dictionary"""
        if keywords_file and os.path.exists(keywords_file):
            with open(keywords_file, 'r') as f:
                self.keywords = json.load(f)
        else:
            self.keywords = self.get_default_keywords()
    
    def get_default_keywords(self):
        """Default keywords database"""
        return {
            # System commands
            "calculator": ["calc", "calculation", "calculate", "calcu", "math"],
            "notepad": ["note pad", "text editor", "notes", "write"],
            "chrome": ["browser", "internet", "web", "google chrome"],
            "firefox": ["mozilla", "web browser"],
            "edge": ["microsoft edge", "internet explorer"],
            "volume": ["sound", "audio", "loud", "quiet", "speaker"],
            "brightness": ["screen", "display", "bright", "dark", "monitor"],
            "shutdown": ["turn off", "power off", "shut down", "switch off"],
            "restart": ["reboot", "reset", "start again"],
            "time": ["clock", "current time", "what time", "hour"],
            "date": ["today", "current date", "what day", "calendar"],
            
            # File operations
            "open": ["launch", "start", "run", "execute", "load"],
            "search": ["find", "locate", "look for", "hunt"],
            "screenshot": ["capture", "screen shot", "snap", "print screen"],
            "save": ["store", "keep", "preserve"],
            "delete": ["remove", "erase", "trash"],
            "copy": ["duplicate", "clone"],
            "move": ["relocate", "transfer"],
            
            # AI queries
            "what": ["tell me", "explain", "describe", "define"],
            "how": ["show me", "teach me", "guide me", "instruct"],
            "why": ["reason", "because", "cause"],
            "when": ["time", "schedule", "timing"],
            "where": ["location", "place", "position"],
            "weather": ["forecast", "temperature", "climate", "rain", "sunny"],
            "news": ["headlines", "current events", "updates", "breaking"],
            
            # Memory commands
            "remember": ["save", "store", "keep in mind", "memorize"],
            "forget": ["delete", "remove", "erase", "clear"],
            
            # Media controls
            "play": ["start", "begin", "run"],
            "pause": ["stop", "halt", "freeze"],
            "music": ["song", "audio", "tune", "melody"],
            "video": ["movie", "clip", "film"],
            
            # Communication
            "email": ["mail", "message", "send"],
            "call": ["phone", "ring", "dial"],
            "text": ["sms", "message", "chat"],
        }
    
    def add_keyword(self, keyword, variations):
        """Add a new keyword with its variations"""
        self.keywords[keyword] = variations
    
    def fuzzy_match(self, user_input, threshold=0.6, max_results=3):
        """Find similar keywords using fuzzy matching"""
        user_input_lower = user_input.lower().strip()
        matches = []
        
        for keyword, variations in self.keywords.items():
            # Check direct keyword match
            if keyword in user_input_lower:
                matches.append((keyword, 1.0, "direct"))
                continue
                
            # Check variations
            for variation in variations:
                if variation in user_input_lower:
                    matches.append((keyword, 0.9, "variation"))
                    continue
                    
            # Fuzzy matching on keyword
            keyword_similarity = SequenceMatcher(None, user_input_lower, keyword).ratio()
            if keyword_similarity >= threshold:
                matches.append((keyword, keyword_similarity, "fuzzy_keyword"))
                
            # Check against variations with fuzzy matching
            for variation in variations:
                variation_similarity = SequenceMatcher(None, user_input_lower, variation).ratio()
                if variation_similarity >= threshold:
                    matches.append((keyword, variation_similarity, "fuzzy_variation"))
        
        # Sort by similarity score and remove duplicates
        matches = list(set(matches))
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:max_results]
    
    def get_suggestions(self, user_input, threshold=0.6):
        """Get keyword suggestions for user input"""
        matches = self.fuzzy_match(user_input, threshold)
        if matches:
            suggestions = []
            for keyword, similarity, match_type in matches:
                confidence = "High" if similarity > 0.8 else "Medium" if similarity > 0.7 else "Low"
                suggestions.append({
                    "keyword": keyword,
                    "similarity": similarity,
                    "confidence": confidence,
                    "match_type": match_type
                })
            return suggestions
        return []
    
    def test_input(self, user_input):
        """Test fuzzy matching on user input"""
        print(f"\n🔍 Testing: '{user_input}'")
        print("-" * 40)
        
        matches = self.fuzzy_match(user_input, threshold=0.5)
        
        if matches:
            print("✅ Found matches:")
            for i, (keyword, similarity, match_type) in enumerate(matches, 1):
                confidence = "🟢 High" if similarity > 0.8 else "🟡 Medium" if similarity > 0.7 else "🔴 Low"
                print(f"{i}. {keyword} - {confidence} ({similarity:.2f}) [{match_type}]")
        else:
            print("❌ No matches found")
    
    def save_keywords(self, filename="myra_keywords.json"):
        """Save keywords to file"""
        with open(filename, 'w') as f:
            json.dump(self.keywords, f, indent=2)
        print(f"💾 Keywords saved to {filename}")
    
    def interactive_test(self):
        """Interactive testing mode"""
        print("🧠 Myra Fuzzy Keyword Matcher - Interactive Test")
        print("=" * 50)
        print("Type phrases to test fuzzy matching")
        print("Commands: 'quit' to exit, 'add <keyword>' to add new keyword")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💭 Enter phrase to test: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower().startswith('add '):
                    keyword = user_input[4:].strip()
                    variations = input(f"Enter variations for '{keyword}' (comma-separated): ")
                    self.add_keyword(keyword, [v.strip() for v in variations.split(',')])
                    print(f"✅ Added '{keyword}' with variations")
                elif user_input:
                    self.test_input(user_input)
                    
            except KeyboardInterrupt:
                break
        
        print("\n👋 Goodbye!")

def main():
    """Main function for standalone testing"""
    matcher = FuzzyKeywordMatcher()
    
    # Test some examples
    test_cases = [
        "open calcu",
        "start notep",
        "launch browsr",
        "turn up volum",
        "make screen brighter",
        "what's the wether",
        "play some musac",
        "remember this",
        "take a screenshoot"
    ]
    
    print("🧠 Myra Fuzzy Keyword Matcher Test")
    print("=" * 50)
    
    for test_case in test_cases:
        matcher.test_input(test_case)
    
    # Interactive mode
    matcher.interactive_test()

if __name__ == "__main__":
    main()
