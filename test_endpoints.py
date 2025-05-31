#!/usr/bin/env python3
"""
Comprehensive test script for Ergo Price MCP Server endpoints.

This script tests all available endpoints with realistic inputs to validate
functionality and document example usage patterns.

Usage:
    python test_endpoints.py [--base-url http://localhost:8000] [--api-key secret]
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
import argparse
import sys

import httpx


class EndpointTester:
    """Test runner for MCP server endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "secret"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def call_endpoint(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to an MCP endpoint."""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        try:
            if params:
                response = await self.client.post(url, json=params, headers=headers)
            else:
                response = await self.client.post(url, headers=headers)
            
            response.raise_for_status()
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json()
            }
            
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
            except:
                error_data = {"error": e.response.text[:500]}
            
            return {
                "success": False,
                "status_code": e.response.status_code,
                "error": f"HTTP {e.response.status_code}",
                "data": error_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "status_code": None,
                "error": str(e),
                "data": None
            }
    
    async def test_endpoint(self, name: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                          description: str = "", expected_success: bool = True) -> Dict[str, Any]:
        """Test a single endpoint and record results."""
        print(f"\n🧪 Testing {name}")
        print(f"   Endpoint: POST /{endpoint}")
        if params:
            print(f"   Params: {json.dumps(params, indent=6)}")
        else:
            print(f"   Params: None")
        print(f"   Description: {description}")
        
        start_time = time.time()
        result = await self.call_endpoint(endpoint, params)
        duration = time.time() - start_time
        
        result.update({
            "test_name": name,
            "endpoint": endpoint,
            "params": params,
            "description": description,
            "duration_ms": round(duration * 1000, 2),
            "expected_success": expected_success
        })
        
        # Print result
        if result["success"]:
            print(f"   ✅ SUCCESS ({result['duration_ms']}ms)")
            if isinstance(result["data"], dict) and "error" in result["data"]:
                print(f"   ⚠️  API Error: {result['data']['error']}")
            else:
                print(f"   📊 Response preview: {str(result['data'])[:200]}...")
        else:
            print(f"   ❌ FAILED ({result['duration_ms']}ms): {result['error']}")
        
        self.results.append(result)
        return result
    
    async def run_all_tests(self):
        """Run comprehensive tests for all endpoints."""
        print("🚀 Starting Ergo Price MCP Server Endpoint Tests")
        print(f"🔗 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Current timestamp in milliseconds for testing
        current_time_ms = int(time.time() * 1000)
        current_time_s = int(time.time())
        
        # Test token IDs (real Ergo tokens)
        test_tokens = {
            "SigUSD": "fcfca7654fb0da57ecf9a3f489bcbeb1d43b56dce7e73b352f7bc6f2561d2a1b",
            "Djed (Unstable)": "52f4544ce8a420d484ece16f9b984d81c23e46971ef5e37c29382ac50f80d5bd",
            "ERG": "0000000000000000000000000000000000000000000000000000000000000000"  # ERG native token
        }
        
        # ===================================
        # Price Tools Tests
        # ===================================
        
        await self.test_endpoint(
            "Get ERG Price",
            "get_erg_price",
            None,
            "Get current ERG price from CoinGecko with USD/BTC prices, market cap, and 24h change"
        )
        
        await self.test_endpoint(
            "Get ERG History (30 days)",
            "get_erg_history",
            {
                "countback": 30,
                "resolution": "1D"
            },
            "Get 30 days of daily ERG price history"
        )
        
        await self.test_endpoint(
            "Get ERG History (7 days with timestamps)",
            "get_erg_history",
            {
                "countback": 7,
                "resolution": "1D",
                "from_timestamp": current_time_s - (7 * 24 * 3600),
                "to_timestamp": current_time_s
            },
            "Get 7 days of ERG history with explicit timestamp range"
        )
        
        await self.test_endpoint(
            "Get ERG History (24 hours)",
            "get_erg_history",
            {
                "countback": 7,
                "resolution": "1D"
            },
            "Get last 7 days of daily ERG price data (daily resolution is most reliable)"
        )
        
        await self.test_endpoint(
            "Get Spectrum Price (SigUSD)",
            "get_spectrum_price",
            {
                "token_id": test_tokens["SigUSD"]
            },
            "Get current SigUSD price from Spectrum DEX (Note: endpoint may have 502 issues)"
        )
        
        await self.test_endpoint(
            "Get Spectrum Price (SigUSD, specific time)",
            "get_spectrum_price",
            {
                "token_id": test_tokens["SigUSD"],
                "time_point": current_time_ms - (24 * 60 * 60 * 1000)  # 24 hours ago in milliseconds
            },
            "Get SigUSD price from 24 hours ago"
        )
        
        await self.test_endpoint(
            "Get Spectrum Price Stats (SigUSD)",
            "get_spectrum_price_stats",
            {
                "token_id": test_tokens["SigUSD"]
            },
            "Get SigUSD price statistics (min/max/avg) for last 24 hours"
        )
        
        await self.test_endpoint(
            "Get Spectrum Price Stats (SigUSD, 7 days)",
            "get_spectrum_price_stats",
            {
                "token_id": test_tokens["SigUSD"],
                "time_window": 604800  # 7 days in seconds
            },
            "Get SigUSD price statistics over 7-day window"
        )
        
        await self.test_endpoint(
            "Get Spectrum Price Stats (Djed)",
            "get_spectrum_price_stats",
            {
                "token_id": test_tokens["Djed (Unstable)"],
                "time_point": current_time_ms,
                "time_window": 86400  # 24 hours
            },
            "Get Djed Unstable price statistics with explicit time point"
        )
        
        # ===================================
        # Asset & Token Info Tests
        # ===================================
        
        await self.test_endpoint(
            "Get Asset Info (SigUSD)",
            "get_asset_info",
            {
                "token_id": test_tokens["SigUSD"]
            },
            "Get detailed SigUSD asset information"
        )
        
        await self.test_endpoint(
            "Get Token Info (SigUSD)",
            "get_token_info",
            {
                "token_id": test_tokens["SigUSD"]
            },
            "Get comprehensive SigUSD token information"
        )
        
        await self.test_endpoint(
            "Get Token Info (Djed)",
            "get_token_info",
            {
                "token_id": test_tokens["Djed (Unstable)"]
            },
            "Get Djed Unstable token information"
        )
        
        await self.test_endpoint(
            "Get Circulating Supply (SigUSD)",
            "get_circulating_supply",
            {
                "token_id": test_tokens["SigUSD"]
            },
            "Get SigUSD circulating supply data"
        )
        
        # ===================================
        # Search Tests
        # ===================================
        
        await self.test_endpoint(
            "Search Tokens (ERG)",
            "search_tokens",
            {
                "query": "ERG"
            },
            "Search for tokens containing 'ERG' in name or symbol"
        )
        
        await self.test_endpoint(
            "Search Tokens (SigUSD)",
            "search_tokens",
            {
                "query": "SigUSD"
            },
            "Search for SigUSD related tokens"
        )
        
        await self.test_endpoint(
            "Search Tokens (Djed)",
            "search_tokens",
            {
                "query": "Djed"
            },
            "Search for Djed related tokens"
        )
        
        # ===================================
        # TradingView Tests
        # ===================================
        
        await self.test_endpoint(
            "Get TradingView History (ERG)",
            "get_trading_view_history",
            {
                "symbol": "ERG",
                "from_timestamp": current_time_s - (7 * 24 * 3600),
                "to_timestamp": current_time_s,
                "resolution": "1D",
                "countback": 7
            },
            "Get 7 days of ERG TradingView historical data"
        )
        
        # ===================================
        # Additional CRUX Endpoints
        # ===================================
        
        print("\n" + "=" * 80)
        await self.print_summary()
    
    async def print_summary(self):
        """Print test summary and statistics."""
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - successful_tests
        
        # Calculate average response time
        avg_response_time = sum(r["duration_ms"] for r in self.results) / total_tests if total_tests > 0 else 0
        
        print(f"📊 TEST SUMMARY")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Successful: {successful_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   📈 Success Rate: {(successful_tests/total_tests*100):.1f}%")
        print(f"   ⏱️  Average Response Time: {avg_response_time:.1f}ms")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   • {result['test_name']}: {result['error']}")
        
        # Show endpoints with API errors
        api_errors = []
        for result in self.results:
            if result["success"] and isinstance(result.get("data"), dict) and "error" in result["data"]:
                api_errors.append(result)
        
        if api_errors:
            print(f"\n⚠️  ENDPOINTS WITH API ERRORS:")
            for result in api_errors:
                print(f"   • {result['test_name']}: {result['data']['error']}")
        
        print(f"\n🎯 ENDPOINT DOCUMENTATION:")
        print(f"   All test cases above serve as example inputs for each endpoint.")
        print(f"   Copy the 'Params' values to use as templates for your own requests.")
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": successful_tests/total_tests*100 if total_tests > 0 else 0,
            "avg_response_time_ms": avg_response_time,
            "results": self.results
        }
    
    def save_results(self, filename: str = "endpoint_test_results.json"):
        """Save test results to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "base_url": self.base_url,
                "results": self.results
            }, f, indent=2)
        print(f"💾 Test results saved to {filename}")


async def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Test Ergo Price MCP Server endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL of the MCP server (default: http://localhost:8000)")
    parser.add_argument("--api-key", default="secret", 
                       help="API key for authentication (default: secret)")
    parser.add_argument("--save-results", action="store_true",
                       help="Save test results to JSON file")
    parser.add_argument("--output", default="endpoint_test_results.json",
                       help="Output file for test results (default: endpoint_test_results.json)")
    
    args = parser.parse_args()
    
    try:
        async with EndpointTester(args.base_url, args.api_key) as tester:
            await tester.run_all_tests()
            
            if args.save_results:
                tester.save_results(args.output)
                
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 