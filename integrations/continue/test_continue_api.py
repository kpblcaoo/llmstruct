#!/usr/bin/env python3
"""
Test Continue API Integration
"""

import asyncio
import json
import httpx
import sys

async def test_continue_api():
    """Test Continue API endpoints"""
    
    base_url = "http://localhost:8000/api/continue"
    headers = {"X-API-Key": "dev-key", "Content-Type": "application/json"}
    
    print("🔌 Testing Continue API Integration...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            
            # Test 1: Models endpoint
            print("\n1️⃣ Testing /v1/models...")
            response = await client.get(f"{base_url}/v1/models", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                models = response.json()
                print(f"✅ Found {len(models['data'])} models:")
                for model in models['data']:
                    print(f"   - {model['id']}")
            else:
                print(f"❌ Error: {response.text}")
                
            # Test 2: Chat completion
            print("\n2️⃣ Testing /v1/chat/completions...")
            chat_payload = {
                "model": "claude-3-haiku",
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": "Привет! Напиши простую Python функцию для сложения двух чисел."}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = await client.post(
                f"{base_url}/v1/chat/completions",
                headers=headers,
                json=chat_payload
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ AI Response ({len(content)} chars):")
                print(f"   {content[:100]}...")
                print(f"   Model: {result['model']}")
                print(f"   Usage: {result['usage']}")
            else:
                print(f"❌ Error: {response.text}")
                
            # Test 3: Embeddings (placeholder)
            print("\n3️⃣ Testing /v1/embeddings...")
            embeddings_payload = {
                "model": "text-embedding-ada-002",
                "input": "Hello world"
            }
            
            response = await client.post(
                f"{base_url}/v1/embeddings",
                headers=headers,
                json=embeddings_payload
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Embeddings response: {len(result['data'])} items")
            else:
                print(f"❌ Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Make sure API is running:")
        print("   source venv/bin/activate && python test_api.py &")
        return False
        
    print("\n🎉 Continue API integration test completed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_continue_api()) 