#!/usr/bin/env python3
"""
🎤 Enhanced Microphone Test for Myra
Tests microphone sensitivity and audio levels for long-distance listening
"""
import pyaudio
import wave
import numpy as np
import time
import threading
from datetime import datetime

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 30  # Long test duration

class MicrophoneMonitor:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.monitoring = False
        self.peak_levels = []
        self.avg_levels = []
        
    def list_microphones(self):
        """List all available microphones"""
        print("🎤 Available Microphones:")
        print("=" * 50)
        
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"Device {i}: {info['name']}")
                print(f"  - Max Input Channels: {info['maxInputChannels']}")
                print(f"  - Default Sample Rate: {info['defaultSampleRate']}")
                print(f"  - Host API: {self.audio.get_host_api_info_by_index(info['hostApi'])['name']}")
                print()
    
    def test_microphone_levels(self, device_index=None):
        """Test microphone audio levels in real-time"""
        print("🔊 Starting Microphone Level Test...")
        print("=" * 50)
        print("📢 Speak at different distances to test sensitivity")
        print("📊 Audio levels will be displayed in real-time")
        print("🛑 Press Ctrl+C to stop")
        print()
        
        try:
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=CHUNK
            )
            
            self.monitoring = True
            start_time = time.time()
            
            while self.monitoring and (time.time() - start_time < RECORD_SECONDS):
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    
                    # Calculate audio levels
                    rms = np.sqrt(np.mean(audio_data**2))
                    peak = np.max(np.abs(audio_data))
                    
                    # Store for analysis
                    self.peak_levels.append(peak)
                    self.avg_levels.append(rms)
                    
                    # Visual feedback
                    level_bar = self.create_level_bar(rms, 5000)  # Max expected RMS level
                    peak_bar = self.create_level_bar(peak, 32767)  # Max possible peak
                    
                    print(f"\r🔊 RMS: {level_bar} ({rms:6.0f}) | Peak: {peak_bar} ({peak:5.0f})", end="", flush=True)
                    
                    time.sleep(0.1)  # Update every 100ms
                    
                except Exception as e:
                    print(f"\n⚠️ Error reading audio: {e}")
                    break
            
            print("\n\n📊 Test Results:")
            self.analyze_results()
            
        except Exception as e:
            print(f"❌ Error opening microphone: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
    
    def create_level_bar(self, value, max_value, length=20):
        """Create a visual level bar"""
        filled = int((value / max_value) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    def analyze_results(self):
        """Analyze the collected audio data"""
        if not self.peak_levels:
            print("❌ No audio data collected")
            return
        
        avg_peak = np.mean(self.peak_levels)
        max_peak = np.max(self.peak_levels)
        avg_rms = np.mean(self.avg_levels)
        max_rms = np.max(self.avg_levels)
        
        print(f"📈 Average RMS Level: {avg_rms:.0f}")
        print(f"📈 Maximum RMS Level: {max_rms:.0f}")
        print(f"📈 Average Peak Level: {avg_peak:.0f}")
        print(f"📈 Maximum Peak Level: {max_peak:.0f}")
        
        # Provide recommendations
        print("\n💡 Recommendations:")
        
        if avg_rms < 500:
            print("🔴 LOW SENSITIVITY: Consider increasing microphone gain")
            print("   - Check Windows Sound Settings > Microphone > Levels")
            print("   - Move closer to microphone or speak louder")
        elif avg_rms > 3000:
            print("🟡 HIGH SENSITIVITY: May pick up too much noise")
            print("   - Consider reducing microphone gain slightly")
            print("   - Enable noise suppression if available")
        else:
            print("🟢 GOOD SENSITIVITY: Microphone levels look optimal")
        
        if max_peak > 30000:
            print("⚠️ CLIPPING DETECTED: Audio may be distorted")
            print("   - Reduce microphone gain to prevent clipping")
        
        # Distance recommendations
        if avg_rms > 2000:
            print("📏 DISTANCE: Should work well up to 5-10 meters")
        elif avg_rms > 1000:
            print("📏 DISTANCE: Should work well up to 3-5 meters") 
        elif avg_rms > 500:
            print("📏 DISTANCE: Works best within 1-3 meters")
        else:
            print("📏 DISTANCE: Stay within 1 meter for best results")
    
    def record_test_sample(self, filename="mic_test.wav", duration=5):
        """Record a test sample for playback"""
        print(f"🎙️ Recording {duration} second test sample...")
        print("📢 Speak now!")
        
        try:
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            
            frames = []
            for i in range(0, int(RATE / CHUNK * duration)):
                data = self.stream.read(CHUNK)
                frames.append(data)
                
                # Show countdown
                remaining = duration - (i * CHUNK / RATE)
                print(f"\r⏱️ Recording... {remaining:.1f}s remaining", end="", flush=True)
            
            print(f"\n✅ Recording complete! Saved as {filename}")
            
            # Save the recording
            wf = wave.open(filename, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
        except Exception as e:
            print(f"❌ Recording error: {e}")
        finally:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

def main():
    print("🎤 Myra Microphone Test Tool")
    print("=" * 50)
    
    monitor = MicrophoneMonitor()
    
    try:
        # List available microphones
        monitor.list_microphones()
        
        # Ask user to select microphone
        print("📋 Select microphone (press Enter for default):")
        choice = input("Device number (or Enter): ").strip()
        
        device_index = None
        if choice.isdigit():
            device_index = int(choice)
            print(f"Using device {device_index}")
        else:
            print("Using default microphone")
        
        print("\n🔧 Choose test type:")
        print("1. Real-time level monitoring (recommended)")
        print("2. Record test sample")
        print("3. Both tests")
        
        test_choice = input("Enter choice (1-3): ").strip()
        
        if test_choice in ['1', '3']:
            print(f"\n📍 Testing Tips:")
            print("- Stand at different distances (1m, 3m, 5m, 10m+)")
            print("- Try speaking at normal volume")
            print("- Test in quiet and noisy environments")
            print("- Say 'Myra' and other wake words")
            print("\nStarting in 3 seconds...")
            time.sleep(3)
            
            monitor.test_microphone_levels(device_index)
        
        if test_choice in ['2', '3']:
            print("\n🎙️ Recording test sample...")
            monitor.record_test_sample()
            
            # Play back the recording
            try:
                import os
                print("🔊 Playing back recording...")
                os.system("start mic_test.wav")
            except:
                print("Recording saved as mic_test.wav - play it manually to check quality")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user")
    except Exception as e:
        print(f"❌ Test error: {e}")
    finally:
        monitor.cleanup()
        print("\n👋 Microphone test complete!")

if __name__ == "__main__":
    main()
