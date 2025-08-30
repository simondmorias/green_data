#!/usr/bin/env python3
"""
Test Runner for RGM Data Generator
Runs all validation tests to ensure generated data meets requirements
"""

import sys
import os
import traceback
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all test modules
from test_products_dimension import test_products_dimension
from test_geography_dimension import test_geography_dimension
from test_time_dimension import test_time_dimension
from test_fact_sales import test_fact_sales
from test_seasonal_patterns import test_seasonal_patterns
from test_data_scenarios import test_data_scenarios
from test_data_quality import test_data_quality


def run_test(test_func, test_name):
    """Run a single test and report results"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"{'='*60}")
    
    try:
        result = test_func()
        if result:
            print(f"✅ {test_name} PASSED")
            return True
        else:
            print(f"❌ {test_name} FAILED")
            return False
    except AssertionError as e:
        print(f"❌ {test_name} FAILED: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ {test_name} ERROR: {str(e)}")
        traceback.print_exc()
        return False


def main():
    """Run all tests and report overall results"""
    
    print("\n" + "="*60)
    print("RGM Data Generator - Test Suite")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check if data exists
    data_dir = 'generated_data'
    if not os.path.exists(data_dir):
        print(f"\n❌ ERROR: Data directory '{data_dir}' not found!")
        print("Please run 'python3 generate_rgm_data.py' first to generate the data.")
        return 1
    
    # Define all tests
    tests = [
        (test_products_dimension, "Products Dimension Validation"),
        (test_geography_dimension, "Geography Dimension Validation"),
        (test_time_dimension, "Time Dimension Validation"),
        (test_fact_sales, "Fact Sales Table Validation"),
        (test_seasonal_patterns, "Seasonal Patterns Validation"),
        (test_data_scenarios, "Complex Data Scenarios Validation"),
        (test_data_quality, "Data Quality Issues Validation"),
    ]
    
    # Run all tests
    results = []
    for test_func, test_name in tests:
        success = run_test(test_func, test_name)
        results.append((test_name, success))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-"*60)
    print(f"Total Tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(results)*100):.1f}%")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Return 0 if all tests passed, 1 otherwise
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)