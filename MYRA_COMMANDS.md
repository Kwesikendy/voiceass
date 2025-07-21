# 🎤 Myra Voice Assistant - System Commands

## 🖥️ Power Management
- **"Shutdown"** / **"Turn off"** / **"Power off"** - Shuts down PC (with 10-second warning)
- **"Restart"** / **"Reboot"** - Restarts PC (with 10-second warning)  
- **"Sleep"** / **"Hibernate"** - Puts computer to sleep
- **"Lock"** / **"Lock screen"** / **"Lock computer"** - Locks the screen
- **"Cancel"** - Cancels pending shutdown/restart

## 🔆 Display & Audio Controls

### Brightness Control (Dynamic Recognition)
**Make it Brighter:** "increase brightness", "brighter", "bright", "turn up brightness", "more brightness", "boost brightness", "max brightness"

**Make it Darker:** "decrease brightness", "reduce brightness", "darker", "dim", "lower brightness", "less brightness", "minimize brightness"

**Ask for Help:** "change brightness", "adjust brightness" - Myra will ask what you prefer

### Volume Control (Dynamic Recognition)
**Turn Volume Up:** "volume up", "increase volume", "louder", "boost sound", "more volume", "raise \.......................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................volume", "turn up audio"

**Turn Volume Down:** "volume down", "decrease volume", "quieter", "reduce sound", "less volume", "lower volume", "turn down audio", "softer"

**Mute Audio:** "mute", "silence", "quiet", "turn off sound", "shut up"

## 📱 Applications
- **"Open calculator"** / **"Calculator"** - Opens Calculator
- **"Open notepad"** / **"Notepad"** - Opens Notepad
- **"Open file explorer"** / **"Explorer"** - Opens File Explorer
- **"Open task manager"** / **"Task manager"** - Opens Task Manager

## 🤖 AI & Conversation
- **"What's your name?"** / **"Who are you?"** - Myra introduces herself
- **"What can you do?"** - Lists capabilities
- **"Hello"** / **"Hi"** - General conversation
- **Any question** - AI-powered responses using Ollama
- **"Bye"** / **"Goodbye"** / **"Exit"** - Ends conversation

## ⚠️ Safety Features
- **10-second warning** for shutdown/restart commands
- **Cancel option** available for dangerous operations
- **Error handling** if commands fail
- **Permission checks** for system-level operations

## 💡 Usage Tips
1. **Speak clearly** - Myra uses Google Speech Recognition
2. **Wait for response** - Let Myra finish speaking before next command
3. **Be specific** - Say "increase brightness" not just "brightness"
4. **Safety first** - Myra warns before dangerous operations

## 🔧 Technical Notes
- Some commands may require **administrator privileges**
- Brightness control uses **WMI** (Windows Management Instrumentation)
- Volume control uses **Windows Forms SendKeys**
- All system commands are **Windows-specific**

## 🎯 Example Conversations

**Power Management:**
- You: "Turn off my computer"
- Myra: "Shutting down the computer in 10 seconds. Say cancel to stop."

**Quick Tasks:**
- You: "Open calculator"
- Myra: "Calculator opened."

**Brightness:**
- You: "Make the screen brighter"
- Myra: "Brightness increased to maximum."

**General Chat:**
- You: "How's the weather?"
- Myra: [AI-powered response about weather or asking for location]
