#!/usr/bin/env python3
"""Test script to validate workflow structure without executing LLM calls."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all workflow modules can be imported."""
    print("Testing imports...")
    try:
        from Backend.Prod.workflows.proto import ProtoWorkflow
        from Backend.Prod.workflows.prod import ProdWorkflow
        from Backend.Prod.workflows import ProtoWorkflow as ProtoWF, ProdWorkflow as ProdWF
        print("✓ All workflow imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_workflow_initialization():
    """Test that workflows can be initialized."""
    print("\nTesting workflow initialization...")
    try:
        from Backend.Prod.workflows.proto import ProtoWorkflow
        from Backend.Prod.workflows.prod import ProdWorkflow
        
        proto = ProtoWorkflow()
        prod = ProdWorkflow()
        
        print("✓ ProtoWorkflow initialized")
        print("✓ ProdWorkflow initialized")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_validation_plan_generation():
    """Test that validation plan generation logic exists."""
    print("\nTesting validation plan generation...")
    try:
        from Backend.Prod.workflows.proto import ProtoWorkflow
        
        proto = ProtoWorkflow()
        
        # Check that _validate_results method exists
        assert hasattr(proto, '_validate_results'), "_validate_results method missing"
        assert callable(proto._validate_results), "_validate_results is not callable"
        
        print("✓ Validation method exists in ProtoWorkflow")
        
        from Backend.Prod.workflows.prod import ProdWorkflow
        prod = ProdWorkflow()
        assert hasattr(prod, '_validate_results'), "_validate_results method missing"
        assert callable(prod._validate_results), "_validate_results is not callable"
        
        print("✓ Validation method exists in ProdWorkflow")
        return True
    except Exception as e:
        print(f"✗ Validation plan generation test failed: {e}")
        return False

def test_cache_namespace():
    """Test that cache namespace support exists."""
    print("\nTesting cache namespace support...")
    try:
        from Backend.Prod.cache.semantic_cache import SemanticCache
        
        cache = SemanticCache()
        
        # Check that get and put methods accept namespace parameter
        import inspect
        get_sig = inspect.signature(cache.get)
        put_sig = inspect.signature(cache.put)
        
        assert 'namespace' in get_sig.parameters, "get() missing namespace parameter"
        assert 'namespace' in put_sig.parameters, "put() missing namespace parameter"
        
        print("✓ Cache namespace support present")
        return True
    except Exception as e:
        print(f"✗ Cache namespace test failed: {e}")
        return False

def test_guidelines_injection():
    """Test that guidelines injection exists."""
    print("\nTesting guidelines injection...")
    try:
        from Backend.Prod.models.agent_router import AgentRouter
        
        router = AgentRouter(execution_mode="BUILD")
        
        # Check that _load_guidelines method exists
        assert hasattr(router, '_load_guidelines'), "_load_guidelines method missing"
        assert callable(router._load_guidelines), "_load_guidelines is not callable"
        
        # Check that _build_step_prompt_stripped exists and handles guidelines
        assert hasattr(router, '_build_step_prompt_stripped'), "_build_step_prompt_stripped method missing"
        
        print("✓ Guidelines injection methods present")
        return True
    except Exception as e:
        print(f"✗ Guidelines injection test failed: {e}")
        return False

def test_cli_commands():
    """Test that CLI commands are defined."""
    print("\nTesting CLI commands...")
    try:
        import argparse
        from Backend.Prod.cli import main
        
        # Create a parser to check arguments
        parser = argparse.ArgumentParser()
        
        # We can't easily test argparse without running, but we can check the module
        import inspect
        main_source = inspect.getsource(main)
        
        assert '--fast' in main_source or 'args.fast' in main_source, "--fast flag missing"
        assert '--build' in main_source or 'args.build' in main_source, "--build flag missing"
        assert '--stats' in main_source or 'args.stats' in main_source, "--stats flag missing"
        
        print("✓ CLI commands present")
        return True
    except Exception as e:
        print(f"✗ CLI commands test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing AETHERFLOW 2.0 Workflows Structure")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_workflow_initialization,
        test_validation_plan_generation,
        test_cache_namespace,
        test_guidelines_injection,
        test_cli_commands
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All structure tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
