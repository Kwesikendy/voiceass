import requests
import json

def test_ollama_connection():
    """Test if Ollama is running and what models are available"""
    try:
        # Test if Ollama is running
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json()
            print("✅ Ollama is running!")
            print("Available models:")
            if models.get('models'):
                for model in models['models']:
                    print(f"  - {model['name']} (Size: {model.get('size', 'Unknown')})")
            else:
                print("  No models installed yet")
            return models.get('models', [])
        else:
            print("❌ Ollama is not responding")
            return []
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Is it running?")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_model(model_name, prompt="Hello, how are you?"):
    """Test a specific model with a simple prompt"""
    print(f"\n🧪 Testing model: {model_name}")
    try:
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False  # Get complete response at once for testing
        }
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model {model_name} works!")
            print(f"Response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Model {model_name} failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Ollama Setup...")
    models = test_ollama_connection()
    
    if models:
        print(f"\n📝 Found {len(models)} models. Testing them:")
        for model in models:
            test_model(model['name'])
    else:
        print("\n💡 Suggested models to install:")
        print("  For fast/light: ollama pull llama3.2:1b")
        print("  For better quality: ollama pull llama3.2:3b") 
        print("  For best quality: ollama pull llama3.1:8b")
        print("\nRun one of these commands and then run this script again.")
