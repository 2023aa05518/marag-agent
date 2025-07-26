"""
Test API endpoints with environmental query similar to test_simple_pipeline.py
"""

import requests
import json
import time
from src.utils.logging_config import setup_logging

# Setup logging to see debug messages
setup_logging()

# API base URL - matches main.py default
BASE_URL = "http://localhost:8100"


def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check connection error: {e}")
        return False


def test_query_endpoint():
    """Test the query processing endpoint with environmental query"""
    print("\nTesting query endpoint...")
    
    # Same query as test_simple_pipeline.py
    query_data = {
        # "query_text": "What are the primary environmental challenges India is facing?",
        "query_text": "Why is the sky blue?",
        "collection_name": "docs",
        "k": 2,
        "enable_validation": True
    }
    
    print(f"Processing query: {query_data['query_text']}")
    print(f"Collection: {query_data['collection_name']}")
    print(f"Results count (k): {query_data['k']}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=180
        )
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Query processed successfully")
            print(f"Status: {result.get('status', 'unknown')}")
            print(f"API response time: {end_time - start_time:.2f}s")
            print(f"Server execution time: {result.get('metadata', {}).get('execution_time_seconds', 'N/A')}s")
            print(f"Agents used: {result.get('metadata', {}).get('agents_used', [])}")
            print("-" * 50)
            print("Result:")
            print(result.get('result', 'No result available'))
            
            # Print validation scores if available
            if 'validation' in result and result['validation']:
                print("-" * 50)
                print("RAGAS Validation:")
                validation = result['validation']
                print(f"Passed: {validation.get('passed', 'N/A')}")
                print(f"Overall Score: {validation.get('overall_score', 'N/A')}")
                if 'metrics' in validation:
                    print("Metrics:")
                    for metric, score in validation['metrics'].items():
                        print(f"  {metric}: {score:.3f}")
            else:
                print("-" * 50)
                print("RAGAS Validation: Not available")
            
            return True
            
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Query connection error: {e}")
        return False


def test_api_info_endpoint():
    """Test the API information endpoint"""
    print("\nTesting API info endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/", timeout=10)
        
        if response.status_code == 200:
            info_data = response.json()
            print(f"✅ API info retrieved successfully")
            print(f"Available endpoints: {len(info_data.get('endpoints', []))}")
            print(f"Available agents: {info_data.get('agents', [])}")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API info connection error: {e}")
        return False


def main():
    """Main test runner"""
    print("=" * 60)
    print("Multi-Agent RAG Pipeline API Integration Test")
    print("=" * 60)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the API server is running: python main.py")
    print("=" * 60)
    
    # Run health check first
    health_ok = test_health_endpoint()
    if not health_ok:
        print("\n❌ Health check failed. API server is not reachable or unhealthy.")
        print("Exiting tests early. Please start the API server and retry.")
        exit(1)
    # Only run further tests if health check passes
    info_ok = test_api_info_endpoint()
    query_ok = test_query_endpoint()
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"API Info: {'✅ PASS' if info_ok else '❌ FAIL'}")
    print(f"Query Processing: {'✅ PASS' if query_ok else '❌ FAIL'}")
    if all([health_ok, info_ok, query_ok]):
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check API server status.")
        return 1


if __name__ == "__main__":
    exit(main())
