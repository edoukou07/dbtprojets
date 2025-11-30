"""
Test script for RH API endpoints
Tests all endpoints in the RhViewSet
"""
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000/api/rh"
TOKEN = "6b6ddbda652f1c007215f84737959215a98cc764"  # Your auth token

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

def print_response(endpoint_name, response):
    """Pretty print API response"""
    print(f"\n{'='*80}")
    print(f"ENDPOINT: {endpoint_name}")
    print(f"{'='*80}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
    
    print(f"{'='*80}\n")

def test_agents_productivite():
    """Test agents_productivite endpoint"""
    url = f"{BASE_URL}/agents_productivite/"
    response = requests.get(url, headers=headers)
    print_response("GET /api/rh/agents_productivite/", response)
    return response

def test_top_agents():
    """Test top_agents endpoint with different metrics"""
    metrics = ['montant_recouvre', 'taux_recouvrement', 'nombre_collectes', 'taux_cloture']
    
    for metric in metrics:
        url = f"{BASE_URL}/top_agents/?limit=5&metric={metric}"
        response = requests.get(url, headers=headers)
        print_response(f"GET /api/rh/top_agents/?metric={metric}&limit=5", response)

def test_performance_by_type():
    """Test performance_by_type endpoint"""
    url = f"{BASE_URL}/performance_by_type/"
    response = requests.get(url, headers=headers)
    print_response("GET /api/rh/performance_by_type/", response)
    return response

def test_collectes_analysis():
    """Test collectes_analysis endpoint"""
    url = f"{BASE_URL}/collectes_analysis/"
    response = requests.get(url, headers=headers)
    print_response("GET /api/rh/collectes_analysis/", response)
    return response

def test_agent_details():
    """Test agent_details endpoint"""
    # First get an agent ID from agents_productivite
    response = requests.get(f"{BASE_URL}/agents_productivite/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('agents') and len(data['agents']) > 0:
            agent_id = data['agents'][0]['agent_id']
            
            url = f"{BASE_URL}/agent_details/?agent_id={agent_id}"
            response = requests.get(url, headers=headers)
            print_response(f"GET /api/rh/agent_details/?agent_id={agent_id}", response)
        else:
            print("No agents found in database")
    else:
        print(f"Failed to get agents list: {response.status_code}")

def test_efficiency_metrics():
    """Test efficiency_metrics endpoint"""
    url = f"{BASE_URL}/efficiency_metrics/"
    response = requests.get(url, headers=headers)
    print_response("GET /api/rh/efficiency_metrics/", response)
    return response

def run_all_tests():
    """Run all RH endpoint tests"""
    print("\n" + "="*80)
    print("TESTING RH API ENDPOINTS")
    print("="*80)
    
    try:
        # Test all endpoints
        test_agents_productivite()
        test_top_agents()
        test_performance_by_type()
        test_collectes_analysis()
        test_agent_details()
        test_efficiency_metrics()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server at http://127.0.0.1:8000")
        print("Make sure Django server is running: python manage.py runserver 8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
