import sys
import os

# Add the AntiPattern_Remediator directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def test_ollama_simple():
    """Test Ollama LLM connectivity"""
    try:
        from src.core.llm_models.create_llm import LLMCreator
        
        # Create Ollama LLM instance
        llm = LLMCreator.create_llm(provider="ollama", model_name="granite3.3:8b")
        print("✓ Ollama LLM successfully created")
        
        # Test simple conversation
        response = llm.invoke("Hello, who are you?")
        print(f"✓ Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")
        return False

def test_ibm_simple():
    """Test IBM Watson X LLM connectivity"""
    try:
        from src.core.llm_models.create_llm import LLMCreator

        # Create IBM Watson X LLM instance
        llm = LLMCreator.create_llm("ibm", "ibm/granite-3-3-8b-instruct")
        print("✓ IBM Watson X LLM successfully created")

        # Test simple conversation
        response = llm.invoke("Hello, who are you?")
        print(f"✓ Response: {response}")
        return True
        
    except Exception as e:
        print(f"❌ IBM Watson X test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Running LLM Connectivity Tests")
    print("=" * 40)
    
    # Test Ollama
    print("\n📱 Testing Ollama:")
    ollama_result = test_ollama_simple()
    
    # Test IBM Watson X
    print("\n🔵 Testing IBM Watson X:")
    ibm_result = test_ibm_simple()
    
    if not ollama_result:
        print("  - Ollama test failed")
    if not ibm_result:
        print("  - IBM Watson X test failed")
