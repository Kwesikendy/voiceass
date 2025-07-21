#!/usr/bin/env python3
"""
🧠 Myra Session Manager
Handles session state, timeout, and continuous listening
"""
import time
import threading
from datetime import datetime, timedelta
from enum import Enum

class SessionState(Enum):
    SLEEPING = "sleeping"
    AWAKE = "awake"
    LISTENING = "listening"
    PROCESSING = "processing"
    TIMEOUT_WARNING = "timeout_warning"

class MyraSessionManager:
    def __init__(self, timeout_seconds=30, warning_seconds=5):
        """
        Initialize session manager
        
        Args:
            timeout_seconds: Seconds of inactivity before going to sleep
            warning_seconds: Seconds before timeout to warn user
        """
        self.timeout_seconds = timeout_seconds
        self.warning_seconds = warning_seconds
        self.state = SessionState.SLEEPING
        self.last_activity = time.time()
        self.session_start_time = None
        self.total_commands = 0
        self.auto_sleep_enabled = True
        self.warning_given = False
        
        # Session statistics
        self.session_stats = {
            "commands_processed": 0,
            "session_duration": 0,
            "wake_ups": 0,
            "timeouts": 0,
            "manual_sleeps": 0
        }
    
    def wake_up(self):
        """Wake up Myra and start session"""
        if self.state == SessionState.SLEEPING:
            self.state = SessionState.AWAKE
            self.session_start_time = time.time()
            self.last_activity = time.time()
            self.warning_given = False
            self.session_stats["wake_ups"] += 1
            print("🌅 Session started")
            return True
        return False
    
    def go_to_sleep(self, reason="manual"):
        """Put Myra to sleep"""
        if self.state != SessionState.SLEEPING:
            # Update session statistics
            if self.session_start_time:
                session_duration = time.time() - self.session_start_time
                self.session_stats["session_duration"] += session_duration
                print(f"📊 Session lasted {session_duration:.1f} seconds")
            
            self.state = SessionState.SLEEPING
            self.session_start_time = None
            
            if reason == "timeout":
                self.session_stats["timeouts"] += 1
                print("😴 Going to sleep due to inactivity")
            elif reason == "manual":
                self.session_stats["manual_sleeps"] += 1
                print("😴 Going to sleep manually")
            
            return True
        return False
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
        self.warning_given = False
        if self.state == SessionState.AWAKE:
            self.session_stats["commands_processed"] += 1
    
    def set_state(self, new_state):
        """Set the current session state"""
        if new_state != self.state:
            print(f"🔄 State change: {self.state.value} → {new_state.value}")
            self.state = new_state
    
    def is_awake(self):
        """Check if Myra is currently awake"""
        return self.state != SessionState.SLEEPING
    
    def is_sleeping(self):
        """Check if Myra is currently sleeping"""
        return self.state == SessionState.SLEEPING
    
    def should_timeout(self):
        """Check if session should timeout"""
        if not self.auto_sleep_enabled or self.state == SessionState.SLEEPING:
            return False
            
        time_since_activity = time.time() - self.last_activity
        return time_since_activity >= self.timeout_seconds
    
    def should_warn_timeout(self):
        """Check if we should warn about upcoming timeout"""
        if not self.auto_sleep_enabled or self.state == SessionState.SLEEPING or self.warning_given:
            return False
            
        time_since_activity = time.time() - self.last_activity
        warning_threshold = self.timeout_seconds - self.warning_seconds
        
        if time_since_activity >= warning_threshold:
            self.warning_given = True
            return True
        return False
    
    def get_time_until_timeout(self):
        """Get seconds until timeout"""
        if self.state == SessionState.SLEEPING:
            return 0
            
        time_since_activity = time.time() - self.last_activity
        time_remaining = self.timeout_seconds - time_since_activity
        return max(0, time_remaining)
    
    def extend_session(self, additional_seconds=30):
        """Extend the current session by additional time"""
        if self.is_awake():
            self.last_activity = time.time() + additional_seconds
            self.warning_given = False
            print(f"⏰ Session extended by {additional_seconds} seconds")
            return True
        return False
    
    def toggle_auto_sleep(self):
        """Toggle automatic sleep feature"""
        self.auto_sleep_enabled = not self.auto_sleep_enabled
        status = "enabled" if self.auto_sleep_enabled else "disabled"
        print(f"🔄 Auto-sleep {status}")
        return self.auto_sleep_enabled
    
    def get_session_info(self):
        """Get current session information"""
        if self.state == SessionState.SLEEPING:
            return {
                "state": "sleeping",
                "time_until_timeout": 0,
                "session_duration": 0,
                "auto_sleep": self.auto_sleep_enabled
            }
        
        current_time = time.time()
        session_duration = current_time - self.session_start_time if self.session_start_time else 0
        time_until_timeout = self.get_time_until_timeout()
        
        return {
            "state": self.state.value,
            "session_duration": session_duration,
            "time_until_timeout": time_until_timeout,
            "commands_processed": self.session_stats["commands_processed"],
            "auto_sleep": self.auto_sleep_enabled
        }
    
    def get_stats(self):
        """Get session statistics"""
        current_session_duration = 0
        if self.session_start_time and self.is_awake():
            current_session_duration = time.time() - self.session_start_time
        
        total_duration = self.session_stats["session_duration"] + current_session_duration
        
        return {
            "total_wake_ups": self.session_stats["wake_ups"],
            "total_commands": self.session_stats["commands_processed"],
            "total_session_time": total_duration,
            "total_timeouts": self.session_stats["timeouts"],
            "total_manual_sleeps": self.session_stats["manual_sleeps"],
            "average_session_time": total_duration / max(1, self.session_stats["wake_ups"]),
            "current_session_duration": current_session_duration
        }
    
    def print_stats(self):
        """Print session statistics"""
        stats = self.get_stats()
        print("\n📊 Myra Session Statistics")
        print("=" * 30)
        print(f"Total Wake-ups: {stats['total_wake_ups']}")
        print(f"Total Commands: {stats['total_commands']}")
        print(f"Total Active Time: {stats['total_session_time']:.1f}s")
        print(f"Average Session: {stats['average_session_time']:.1f}s")
        print(f"Timeouts: {stats['total_timeouts']}")
        print(f"Manual Sleeps: {stats['total_manual_sleeps']}")
        if self.is_awake():
            print(f"Current Session: {stats['current_session_duration']:.1f}s")
    
    def handle_timeout_check(self, speak_callback=None):
        """
        Handle timeout checking logic
        Returns action to take: 'continue', 'warn', 'sleep', or None
        """
        if self.is_sleeping():
            return None
            
        if self.should_timeout():
            if speak_callback:
                speak_callback("I haven't heard from you for a while. Going back to sleep.")
            self.go_to_sleep(reason="timeout")
            return 'sleep'
        
        elif self.should_warn_timeout():
            time_left = int(self.get_time_until_timeout())
            if speak_callback:
                speak_callback(f"I'll go to sleep in {time_left} seconds if you don't need anything else.")
            return 'warn'
        
        return 'continue'

def create_session_manager(timeout_seconds=30, warning_seconds=5):
    """Factory function to create a session manager"""
    return MyraSessionManager(timeout_seconds, warning_seconds)

# Example usage and testing
def test_session_manager():
    """Test the session manager"""
    print("🧪 Testing Myra Session Manager")
    print("=" * 40)
    
    # Create session manager with short timeout for testing
    session = MyraSessionManager(timeout_seconds=10, warning_seconds=3)
    
    # Test wake up
    print("\n1. Testing wake up...")
    session.wake_up()
    session.print_stats()
    
    # Test activity updates
    print("\n2. Simulating commands...")
    for i in range(3):
        time.sleep(1)
        session.update_activity()
        print(f"Command {i+1} processed")
    
    # Test session info
    print("\n3. Session info:")
    info = session.get_session_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Test timeout warning
    print("\n4. Testing timeout warning...")
    print("Waiting for timeout warning...")
    start_time = time.time()
    while time.time() - start_time < 15:
        action = session.handle_timeout_check(
            speak_callback=lambda msg: print(f"🤖 Myra: {msg}")
        )
        if action == 'warn':
            print("⚠️ Timeout warning triggered!")
        elif action == 'sleep':
            print("😴 Timeout sleep triggered!")
            break
        time.sleep(1)
    
    # Final stats
    print("\n5. Final statistics:")
    session.print_stats()

if __name__ == "__main__":
    test_session_manager()
