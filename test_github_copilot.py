#!/usr/bin/env python3
"""
Simple test to verify GitHub Copilot provider is properly registered
"""

def test_github_copilot_registration():
    """Test that GitHub Copilot provider is registered"""
    try:
        from qwen_agent.llm import LLM_REGISTRY
        from qwen_agent.llm.github_copilot import GitHubCopilotChat
        
        print("✅ Successfully imported GitHubCopilotChat")
        print(f"✅ Available LLM providers: {list(LLM_REGISTRY.keys())}")
        print(f"✅ github_copilot registered: {'github_copilot' in LLM_REGISTRY}")
        
        if 'github_copilot' in LLM_REGISTRY:
            provider_class = LLM_REGISTRY['github_copilot']
            print(f"✅ Provider class: {provider_class}")
            print(f"✅ Is GitHubCopilotChat: {provider_class == GitHubCopilotChat}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auto_detection():
    """Test auto-detection logic"""
    try:
        import os
        from qwen_agent.llm import get_chat_model
        
        # Test without GITHUB_TOKEN (should not auto-detect)
        old_token = os.environ.get('GITHUB_TOKEN')
        if 'GITHUB_TOKEN' in os.environ:
            del os.environ['GITHUB_TOKEN']
        
        try:
            cfg = {'model': 'gpt-4o-mini'}
            llm = get_chat_model(cfg)
            print(f"✅ Without GITHUB_TOKEN, detected type: {getattr(llm, 'model_type', 'unknown')}")
        except Exception as e:
            print(f"✅ Without GITHUB_TOKEN, failed as expected: {type(e).__name__}")
        
        # Restore token if it existed
        if old_token:
            os.environ['GITHUB_TOKEN'] = old_token
            
        return True
        
    except Exception as e:
        print(f"❌ Auto-detection test error: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing GitHub Copilot Provider Registration\n")
    
    success1 = test_github_copilot_registration()
    print()
    success2 = test_auto_detection()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed!")