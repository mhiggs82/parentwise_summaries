import requests
import sys
from datetime import datetime

class BookSummariesAPITester:
    def __init__(self, base_url="https://summary-generator-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    self.test_results.append({
                        'test': name,
                        'status': 'PASSED',
                        'response_size': len(str(response_data)) if response_data else 0
                    })
                    return True, response_data
                except:
                    self.test_results.append({
                        'test': name,
                        'status': 'PASSED',
                        'response_size': len(response.text)
                    })
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.test_results.append({
                    'test': name,
                    'status': 'FAILED',
                    'error': f"Status {response.status_code}, expected {expected_status}"
                })
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                'test': name,
                'status': 'FAILED',
                'error': str(e)
            })
            return False, {}

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root",
            "GET",
            "",
            200
        )
        return success

    def test_get_stats(self):
        """Test stats endpoint"""
        success, response = self.run_test(
            "Get Stats",
            "GET",
            "stats",
            200
        )
        if success:
            print(f"   📊 Total summaries: {response.get('total_summaries', 'N/A')}")
            print(f"   👥 Total authors: {response.get('total_authors', 'N/A')}")
            print(f"   📂 Total categories: {response.get('total_categories', 'N/A')}")
        return success, response

    def test_get_categories(self):
        """Test categories endpoint"""
        success, response = self.run_test(
            "Get Categories",
            "GET",
            "categories",
            200
        )
        if success and isinstance(response, list):
            print(f"   📂 Found {len(response)} categories")
            for cat in response[:3]:  # Show first 3
                print(f"      - {cat.get('name', 'N/A')} ({cat.get('count', 0)} summaries)")
        return success, response

    def test_get_summaries(self):
        """Test summaries endpoint"""
        success, response = self.run_test(
            "Get Summaries (All)",
            "GET",
            "summaries",
            200
        )
        if success:
            summaries = response.get('summaries', [])
            total = response.get('total', 0)
            print(f"   📚 Found {len(summaries)} summaries (total: {total})")
            if summaries:
                print(f"      First: {summaries[0].get('title', 'N/A')} by {summaries[0].get('author', 'N/A')}")
        return success, response

    def test_get_summaries_with_limit(self):
        """Test summaries with limit"""
        success, response = self.run_test(
            "Get Summaries (Limited)",
            "GET",
            "summaries",
            200,
            params={'limit': 6}
        )
        if success:
            summaries = response.get('summaries', [])
            print(f"   📚 Limited to {len(summaries)} summaries")
        return success, response

    def test_get_summaries_by_category(self, category_code):
        """Test summaries filtered by category"""
        success, response = self.run_test(
            f"Get Summaries (Category: {category_code})",
            "GET",
            "summaries",
            200,
            params={'category': category_code}
        )
        if success:
            summaries = response.get('summaries', [])
            total = response.get('total', 0)
            print(f"   📂 Found {len(summaries)} summaries in {category_code} (total: {total})")
        return success, response

    def test_search_summaries(self, search_term):
        """Test summaries search"""
        success, response = self.run_test(
            f"Search Summaries ('{search_term}')",
            "GET",
            "summaries",
            200,
            params={'search': search_term}
        )
        if success:
            summaries = response.get('summaries', [])
            total = response.get('total', 0)
            print(f"   🔍 Found {len(summaries)} summaries for '{search_term}' (total: {total})")
        return success, response

    def test_get_summary_detail(self, slug):
        """Test individual summary detail"""
        success, response = self.run_test(
            f"Get Summary Detail ({slug})",
            "GET",
            f"summaries/{slug}",
            200
        )
        if success:
            print(f"   📖 Title: {response.get('title', 'N/A')}")
            print(f"   ✍️  Author: {response.get('author', 'N/A')}")
            print(f"   📂 Category: {response.get('category_name', 'N/A')}")
            content_length = len(response.get('content_html', ''))
            print(f"   📄 Content length: {content_length} chars")
        return success, response

    def test_invalid_summary(self):
        """Test non-existent summary"""
        success, response = self.run_test(
            "Get Invalid Summary",
            "GET",
            "summaries/non-existent-slug",
            404
        )
        return success

def main():
    print("🚀 Starting ParentWise Book Summaries API Tests")
    print("=" * 60)
    
    tester = BookSummariesAPITester()
    
    # Test API root
    if not tester.test_api_root():
        print("❌ API root failed, stopping tests")
        return 1

    # Test stats
    stats_success, stats_data = tester.test_get_stats()
    if not stats_success:
        print("❌ Stats endpoint failed")
        return 1

    # Test categories
    categories_success, categories_data = tester.test_get_categories()
    if not categories_success:
        print("❌ Categories endpoint failed")
        return 1

    # Test summaries
    summaries_success, summaries_data = tester.test_get_summaries()
    if not summaries_success:
        print("❌ Summaries endpoint failed")
        return 1

    # Test summaries with limit
    tester.test_get_summaries_with_limit()

    # Test category filtering (use first category if available)
    if categories_data and len(categories_data) > 0:
        first_category = categories_data[0]['code']
        tester.test_get_summaries_by_category(first_category)

    # Test search functionality
    tester.test_search_summaries("parenting")

    # Test individual summary detail (use first summary if available)
    if summaries_data and summaries_data.get('summaries'):
        first_summary = summaries_data['summaries'][0]
        slug = first_summary.get('slug')
        if slug:
            tester.test_get_summary_detail(slug)

    # Test invalid summary
    tester.test_invalid_summary()

    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        failed_tests = [r for r in tester.test_results if r['status'] == 'FAILED']
        print(f"Failed tests: {len(failed_tests)}")
        for test in failed_tests:
            print(f"  - {test['test']}: {test.get('error', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())