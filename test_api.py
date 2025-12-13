#!/usr/bin/env python3
"""
Test script to verify the backend API endpoints are working correctly.
"""
import requests
import json
import time

# Backend URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health_endpoint():
    """Test the health endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health endpoint failed: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint with a simple query."""
    print("\nTesting query endpoint...")
    try:
        payload = {
            "question": "What is Physical AI?",
            "book_id": "physical-ai-humanoid-robotics",
            "session_token": "test-session-123"
        }
        response = requests.post(f"{BASE_URL}/query", json=payload)
        print(f"Query endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            if "response" in data:
                print(f"Response preview: {data['response'][:100]}...")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Query endpoint failed: {e}")
        return False

def test_selection_endpoint():
    """Test the selection endpoint with a simple query."""
    print("\nTesting selection endpoint...")
    try:
        payload = {
            "question": "Explain this concept",
            "selected_text": "Physical AI is a field that combines artificial intelligence with physical systems.",
            "book_id": "physical-ai-humanoid-robotics",
            "session_token": "test-session-123"
        }
        response = requests.post(f"{BASE_URL}/query/selection", json=payload)
        print(f"Selection endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            if "response" in data:
                print(f"Response preview: {data['response'][:100]}...")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Selection endpoint failed: {e}")
        return False

def main():
    print("Testing RAG Chatbot API endpoints...\n")

    # Test health first
    health_ok = test_health_endpoint()

    if health_ok:
        print("\n✓ Backend is running and accessible")

        # Give a moment for the model to initialize if needed
        time.sleep(2)

        # Test query endpoints
        query_ok = test_query_endpoint()
        selection_ok = test_selection_endpoint()

        print(f"\nSummary:")
        print(f"- Health endpoint: {'✓' if health_ok else '✗'}")
        print(f"- Query endpoint: {'✓' if query_ok else '✗'}")
        print(f"- Selection endpoint: {'✓' if selection_ok else '✗'}")

        if query_ok and selection_ok:
            print("\n✓ All API endpoints are working correctly!")
        else:
            print("\n⚠ Some endpoints may have issues (this could be due to model initialization time or API key limits)")
    else:
        print("\n✗ Backend is not accessible")

if __name__ == "__main__":
    main()