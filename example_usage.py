#!/usr/bin/env python3
"""
Example usage of the Autonomous Agent-Based Testing Framework

This script demonstrates how to use the framework to analyze and improve
test quality for the example calculator module.
"""

import os
from pathlib import Path
from src import TestingFramework
from src.llm_config import llm_config


def main():
    """Main example function"""
    
    # Check for any LLM provider credentials
    provider_info = llm_config.get_provider_info()
    if not provider_info["credentials_configured"]:
        print("❌ Error: No LLM provider credentials found")
        print("Please set up at least one provider in your .env file:")
        print("")
        print("For Azure OpenAI:")
        print("  AZURE_OPENAI_API_KEY=your-key")
        print("  AZURE_OPENAI_ENDPOINT=your-endpoint")
        print("  AZURE_OPENAI_API_VERSION=2023-07-01-preview")
        print("")
        print("For OpenAI:")
        print("  OPENAI_API_KEY=your-key")
        print("")
        print("For Anthropic:")
        print("  ANTHROPIC_API_KEY=your-key")
        return
    
    # Get the current project directory
    project_path = Path(__file__).parent
    
    print("🚀 Autonomous Agent-Based Testing Framework Demo")
    print("=" * 60)
    print(f"📁 Project: {project_path}")
    print()
    
    try:
        # Initialize the framework
        print("🔧 Initializing framework...")
        
        # Show provider info
        provider_info = llm_config.get_provider_info()
        print(f"🤖 Using provider: {provider_info['default_provider']}")
        print(f"📋 Available providers: {', '.join(provider_info['available_providers'])}")
        
        framework = TestingFramework(
            project_path=project_path,
            model="gpt-4",
            temperature=0.1
        )
        
        # Get initial codebase summary
        print("\n📊 Initial Codebase Analysis:")
        summary = framework.get_codebase_summary()
        print(f"   Total code units: {summary['total_code_units']}")
        print(f"   Classes: {summary['classes']}")
        print(f"   Functions: {summary['functions']}")
        print(f"   Methods: {summary['methods']}")
        print(f"   Existing tests: {summary['total_tests']}")
        
        # Run analysis only (no test generation)
        print("\n🔍 Running Analysis (No Changes)...")
        framework.code_units = framework.code_mapper.map_codebase(framework.source_path)
        framework.test_cases = framework.test_discovery.discover_tests(framework.test_path)
        
        before_metrics = framework.test_assessor.assess_quality(framework.code_units, framework.test_cases)
        
        print(f"   📈 Coverage: {before_metrics.coverage_percentage:.1f}%")
        print(f"   🧪 Total Tests: {before_metrics.total_tests}")
        print(f"   ✅ Total Assertions: {before_metrics.total_assertions}")
        print(f"   📊 Assertion Density: {before_metrics.assertion_density:.2f}")
        print(f"   📝 Test Clarity Score: {before_metrics.test_clarity_score:.1f}/10")
        print(f"   ⚠️  Uncovered Units: {len(before_metrics.uncovered_units)}")
        
        if before_metrics.uncovered_units:
            print("\n   📋 Uncovered Units:")
            for unit in list(before_metrics.uncovered_units)[:5]:
                print(f"      - {unit}")
        
        # Ask user if they want to run full audit
        print("\n" + "=" * 60)
        response = input("🤖 Would you like to run the full autonomous audit with test generation? (y/N): ")
        
        if response.lower() in ['y', 'yes']:
            print("\n🚀 Running Full Autonomous Audit...")
            print("⚠️  This will generate new test files and may take several minutes.")
            print("   Make sure you have sufficient OpenAI API credits.")
            
            confirm = input("   Continue? (y/N): ")
            if confirm.lower() in ['y', 'yes']:
                # Run full audit
                audit_report = framework.run_full_audit(
                    generate_tests=True,
                    run_mutation_testing=False,  # Skip mutation testing for demo
                    max_iterations=2
                )
                
                # Display results
                print("\n" + "=" * 60)
                print("📊 AUDIT RESULTS SUMMARY")
                print("=" * 60)
                
                if audit_report.before_metrics and audit_report.after_metrics:
                    before = audit_report.before_metrics
                    after = audit_report.after_metrics
                    
                    print(f"📈 Coverage: {before.coverage_percentage:.1f}% → {after.coverage_percentage:.1f}% "
                          f"({after.coverage_percentage - before.coverage_percentage:+.1f}%)")
                    print(f"🧪 Tests: {before.total_tests} → {after.total_tests} "
                          f"({after.total_tests - before.total_tests:+d})")
                    print(f"✅ Assertions: {before.total_assertions} → {after.total_assertions} "
                          f"({after.total_assertions - before.total_assertions:+d})")
                    print(f"📊 Assertion Density: {before.assertion_density:.2f} → {after.assertion_density:.2f} "
                          f"({after.assertion_density - before.assertion_density:+.2f})")
                
                if audit_report.improvements:
                    print("\n🎉 Improvements Made:")
                    for improvement in audit_report.improvements:
                        print(f"   ✅ {improvement}")
                
                if audit_report.recommendations:
                    print("\n💡 Recommendations:")
                    for rec in audit_report.recommendations:
                        print(f"   📝 {rec}")
                
                print(f"\n📄 Reports saved to: {framework.reports_path}")
            else:
                print("❌ Audit cancelled.")
        else:
            print("✅ Analysis complete. No changes made.")
        
        print("\n🎯 Demo completed!")
        print("\nTo run the framework on your own projects:")
        print("1. Set up LLM provider credentials in .env file")
        print("2. Use: python -m src audit ./your-project --verbose")
        print("3. Or use the Python API as shown in this example")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure LLM provider credentials are set correctly in .env")
        print("2. Check your internet connection")
        print("3. Verify you have sufficient API credits")
        print("4. Review the error message above")


if __name__ == "__main__":
    main() 