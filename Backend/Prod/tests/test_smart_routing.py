"""Tests for smart routing components."""
import asyncio
from unittest.mock import Mock, AsyncMock

from Backend.Prod.models.plan_reader import Step
from Backend.Prod.models.smart_context_router import (
    SmartContextRouter,
    RoutingDecision,
    ProviderTier,
    PROVIDER_PROFILES
)
from Backend.Prod.models.provider_fallback_cascade import (
    ProviderFallbackCascade,
    CascadeConfig,
    FailureType,
    CircuitBreaker
)
from Backend.Prod.models.step_chunker import (
    StepChunker,
    ChunkType
)
from Backend.Prod.models.section_generator import (
    SectionGenerator,
    SectionType,
    should_use_section_generation
)


class TestSmartContextRouter:
    """Test smart context router."""
    
    def test_initialization(self):
        router = SmartContextRouter()
        assert router is not None
        assert len(router.profiles) > 0
    
    def test_initialization_with_providers(self):
        router = SmartContextRouter(available_providers=["groq", "gemini"])
        assert "groq" in router.profiles
        assert "gemini" in router.profiles
        assert "deepseek" not in router.profiles
    
    def test_estimate_tokens_simple(self):
        router = SmartContextRouter()
        step = Step({
            "id": "test_1",
            "description": "Create a simple function",
            "type": "code_generation",
            "complexity": 0.3,
            "estimated_tokens": 1000,
            "dependencies": [],
            "validation_criteria": []
        })
        
        tokens = router.estimate_tokens(step)
        assert tokens > 0
        assert tokens >= step.estimated_tokens
    
    def test_estimate_tokens_with_context(self):
        router = SmartContextRouter()
        step = Step({
            "id": "test_2",
            "description": "Create a complex class",
            "type": "code_generation",
            "complexity": 0.8,
            "estimated_tokens": 5000,
            "dependencies": [],
            "validation_criteria": []
        })
        
        context = "Additional context " * 100  # ~400 tokens
        tokens = router.estimate_tokens(step, context=context)
        
        # Should include context tokens
        assert tokens > 5000
    
    def test_estimate_tokens_with_files(self):
        router = SmartContextRouter()
        step = Step({
            "id": "test_3",
            "description": "Modify existing code",
            "type": "refactoring",
            "complexity": 0.5,
            "estimated_tokens": 2000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {"files": ["test.py"]}
        })
        
        loaded_files = {"test.py": "def foo():\n    pass\n" * 50}  # ~200 tokens
        tokens = router.estimate_tokens(step, loaded_files=loaded_files)
        
        assert tokens > 2000
    
    def test_select_provider_small_tokens(self):
        router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini"])
        
        decision = router.select_provider_for_tokens(
            estimated_tokens=5000,
            execution_mode="FAST"
        )
        
        assert decision.primary_provider == "groq"
        assert not decision.should_chunk
    
    def test_select_provider_medium_tokens(self):
        router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini"])
        
        decision = router.select_provider_for_tokens(
            estimated_tokens=20000,
            execution_mode="BUILD"
        )
        
        assert decision.primary_provider == "deepseek"
    
    def test_select_provider_large_tokens(self):
        router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini"])
        
        decision = router.select_provider_for_tokens(
            estimated_tokens=60000,
            execution_mode="BUILD"
        )
        
        assert decision.primary_provider == "gemini"
        assert decision.should_chunk
    
    def test_select_provider_vision(self):
        router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini"])
        
        decision = router.select_provider_for_tokens(
            estimated_tokens=5000,
            requires_vision=True,
            execution_mode="BUILD"
        )
        
        assert decision.primary_provider == "gemini"
    
    def test_should_chunk_step(self):
        router = SmartContextRouter()
        
        # Large step that should be chunked
        step = Step({
            "id": "large_step",
            "description": "Create " + "x" * 1000,  # Long description
            "type": "code_generation",
            "complexity": 0.8,
            "estimated_tokens": 40000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {
                "input_files": ["file1.py", "file2.py", "file3.py", "file4.py"]
            }
        })
        
        should_chunk, reason = router.should_chunk_step(step, 40000)
        assert should_chunk
        assert "estimated_tokens" in reason or "input_files" in reason
    
    def test_get_fallback_chain(self):
        router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini", "codestral"])
        
        chain = router._get_fallback_chain("groq", "FAST")
        
        assert "groq" not in chain
        assert len(chain) > 0
        assert all(p in router.available_providers for p in chain)


class TestProviderFallbackCascade:
    """Test provider fallback cascade."""
    
    def test_circuit_breaker(self):
        cb = CircuitBreaker(threshold=3, timeout=60.0)
        
        # Should start closed
        assert not cb.is_open("groq")
        
        # Record failures
        cb.record_failure("groq")
        cb.record_failure("groq")
        assert not cb.is_open("groq")  # Still under threshold
        
        cb.record_failure("groq")
        assert cb.is_open("groq")  # Now open
        
        # Record success should close it
        cb.record_success("groq")
        assert not cb.is_open("groq")
    
    def test_classify_error_rate_limit(self):
        cascade = ProviderFallbackCascade(clients={})
        
        error = Exception("429 rate limit exceeded")
        failure_type = cascade.classify_error(error)
        
        assert failure_type == FailureType.RATE_LIMIT
    
    def test_classify_error_token_limit(self):
        cascade = ProviderFallbackCascade(clients={})
        
        error = Exception("413 request too large for model")
        failure_type = cascade.classify_error(error)
        
        assert failure_type == FailureType.TOKEN_LIMIT
    
    def test_classify_error_timeout(self):
        cascade = ProviderFallbackCascade(clients={})
        
        error = Exception("timeout after 30s")
        failure_type = cascade.classify_error(error)
        
        assert failure_type == FailureType.TIMEOUT
    
    def test_should_retry_rate_limit(self):
        cascade = ProviderFallbackCascade(clients={})
        
        should_retry, delay = cascade.should_retry(FailureType.RATE_LIMIT, 0, "groq")
        
        assert should_retry
        assert delay > 0
    
    def test_should_not_retry_token_limit(self):
        cascade = ProviderFallbackCascade(clients={})
        
        should_retry, delay = cascade.should_retry(FailureType.TOKEN_LIMIT, 0, "groq")
        
        assert not should_retry
    
    def test_should_not_retry_after_max_attempts(self):
        cascade = ProviderFallbackCascade(clients={})
        
        should_retry, delay = cascade.should_retry(
            FailureType.RATE_LIMIT,
            cascade.config.max_attempts_per_provider - 1,
            "groq"
        )
        
        assert not should_retry


class TestStepChunker:
    """Test step chunker."""
    
    def test_analyze_step_should_chunk(self):
        chunker = StepChunker()
        
        step = Step({
            "id": "large_step",
            "description": "Create a complex system with multiple components and classes",
            "type": "code_generation",
            "complexity": 0.9,
            "estimated_tokens": 35000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {
                "files": ["file1.py", "file2.py", "file3.py", "file4.py"]
            }
        })
        
        should_chunk, reason = chunker.analyze_step(step, 35000)
        assert should_chunk
        assert reason is not None
    
    def test_analyze_step_should_not_chunk(self):
        chunker = StepChunker()
        
        step = Step({
            "id": "small_step",
            "description": "Create a simple function",
            "type": "code_generation",
            "complexity": 0.3,
            "estimated_tokens": 3000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {"files": ["file.py"]}
        })
        
        should_chunk, reason = chunker.analyze_step(step, 3000)
        assert not should_chunk
        assert reason is None
    
    def test_chunk_by_files(self):
        chunker = StepChunker()
        
        step = Step({
            "id": "multi_file",
            "description": "Create modules",
            "type": "code_generation",
            "complexity": 0.5,
            "estimated_tokens": 10000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {
                "files": ["module1.py", "module2.py", "module3.py"]
            }
        })
        
        strategy = chunker._chunk_by_files(step, 10000)
        
        assert strategy.strategy_type == ChunkType.FILE_BASED
        assert len(strategy.chunks) == 3
        assert all(len(c.generated_files) > 0 for c in strategy.chunks)
    
    def test_chunk_iterative(self):
        chunker = StepChunker()
        
        step = Step({
            "id": "large_task",
            "description": "Create a very large system with many components",
            "type": "code_generation",
            "complexity": 0.9,
            "estimated_tokens": 50000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {}
        })
        
        strategy = chunker._chunk_iterative(step, 50000)
        
        assert strategy.strategy_type == ChunkType.ITERATIVE
        assert len(strategy.chunks) >= 2
        assert not strategy.parallelizable  # Iterative chunks are dependent


class TestSectionGenerator:
    """Test section generator."""
    
    def test_create_plan_python(self):
        gen = SectionGenerator()
        
        plan = gen.create_plan(
            description="Create a class with methods and utilities",
            language="python"
        )
        
        assert plan.language == "python"
        assert len(plan.sections) > 0
        assert any(s.section_type == SectionType.IMPORTS for s in plan.sections)
    
    def test_create_plan_javascript(self):
        gen = SectionGenerator()
        
        plan = gen.create_plan(
            description="Create a React component with helper functions",
            language="javascript"
        )
        
        assert plan.language == "javascript"
        assert len(plan.sections) > 0
    
    def test_analyze_description_imports(self):
        gen = SectionGenerator()
        
        sections = gen._analyze_description(
            "Import modules and create a class",
            list(SectionType)
        )
        
        assert SectionType.IMPORTS in sections
    
    def test_analyze_description_classes(self):
        gen = SectionGenerator()
        
        sections = gen._analyze_description(
            "Create a User class with methods",
            list(SectionType)
        )
        
        assert SectionType.CLASSES in sections
    
    def test_should_use_section_generation_true(self):
        step = Step({
            "id": "large_gen",
            "description": "Create multiple classes and functions",
            "type": "code_generation",
            "complexity": 0.8,
            "estimated_tokens": 30000,
            "dependencies": [],
            "validation_criteria": []
        })
        
        result = should_use_section_generation(step, 30000)
        assert result
    
    def test_should_use_section_generation_false(self):
        step = Step({
            "id": "small_gen",
            "description": "Create a simple function",
            "type": "code_generation",
            "complexity": 0.3,
            "estimated_tokens": 3000,
            "dependencies": [],
            "validation_criteria": []
        })
        
        result = should_use_section_generation(step, 3000)
        assert not result


class TestIntegration:
    """Integration tests."""
    
    def test_full_routing_flow(self):
        """Test complete routing flow from step to decision."""
        router = SmartContextRouter(available_providers=["groq", "deepseek", "gemini"])
        
        step = Step({
            "id": "integration_test",
            "description": "Create a complex API endpoint with validation",
            "type": "code_generation",
            "complexity": 0.7,
            "estimated_tokens": 15000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {
                "language": "python",
                "framework": "fastapi",
                "files": ["api.py"]
            }
        })
        
        # Get routing decision
        decision = router.route_step(step, execution_mode="BUILD")
        
        assert decision.primary_provider in ["groq", "deepseek", "gemini"]
        assert decision.estimated_tokens > 0
        assert len(decision.fallback_chain) > 0
    
    def test_chunking_integration(self):
        """Test chunker with router integration."""
        router = SmartContextRouter()
        chunker = StepChunker()
        
        step = Step({
            "id": "massive_step",
            "description": "Create a full application with models, views, controllers, and utilities",
            "type": "code_generation",
            "complexity": 0.95,
            "estimated_tokens": 80000,
            "dependencies": [],
            "validation_criteria": [],
            "context": {
                "files": ["models.py", "views.py", "controllers.py", "utils.py"]
            }
        })
        
        # Router should recommend chunking
        decision = router.route_step(step)
        assert decision.should_chunk
        
        # Chunker should create multiple chunks
        strategy = chunker.chunk_step(step, decision.estimated_tokens)
        assert len(strategy.chunks) > 1


if __name__ == "__main__":
    # Run all tests
    import sys
    
    test_classes = [
        TestSmartContextRouter,
        TestProviderFallbackCascade,
        TestStepChunker,
        TestSectionGenerator,
        TestIntegration
    ]
    
    all_results = []
    for test_class in test_classes:
        instance = test_class()
        for method in [m for m in dir(instance) if m.startswith('test_')]:
            try:
                getattr(instance, method)()
                all_results.append(f'✓ {test_class.__name__}.{method}')
            except Exception as e:
                all_results.append(f'✗ {test_class.__name__}.{method}: {e}')
    
    for r in all_results:
        print(r, file=sys.stderr)
    
    print(file=sys.stderr)
    passed = len([r for r in all_results if r.startswith('✓')])
    failed = len([r for r in all_results if r.startswith('✗')])
    print(f'Results: {passed} passed, {failed} failed', file=sys.stderr)
    sys.exit(0 if failed == 0 else 1)
