# PromptManager Unit Tests

Unit tests for the PromptManager class following AAA (Arrange, Act, Assert) principles.

## Quick Start


### Run Tests
```bash
# Run all tests with verbose output
python -m pytest AntiPattern_Remediator\test\unit_test\prompt\test_prompt_manager.py -v

# Run specific test class
python -m pytest AntiPattern_Remediator\test\unit_test\prompt\test_prompt_manager.py::TestPromptManagerInitialization -v

# Run specific test method
python -m pytest AntiPattern_Remediator\test\unit_test\prompt\test_prompt_manager.py::TestPromptManagerInitialization::test_initialization_creates_correct_attributes -v
```

## Test Coverage

### ✅ **18 Tests Covering:**

1. **Initialization Tests (4)** - Verify object creation and attribute setup
2. **Prompt Retrieval Tests (2)** - Test cache retrieval functionality  
3. **YAML Loading Tests (5)** - File loading, error handling, edge cases
4. **Template Structure Tests (2)** - MessagesPlaceholder and variable substitution
5. **Error Handling Tests (3)** - Edge cases and exception handling
6. **Integration Tests (2)** - Complete workflow validation

### Key Features Tested:
- ✅ AAA principle compliance
- ✅ MessagesPlaceholder inclusion in templates
- ✅ YAML parsing with error handling
- ✅ Variable substitution in prompts
- ✅ Malformed file handling
- ✅ Missing file/section handling
- ✅ Cache management

## Test Results
```
18 passed in 0.19s
```

All tests pass successfully.

```python

================================================ test session starts =================================================
platform win32 -- Python 3.10.18, pytest-8.4.1, pluggy-1.6.0 -- D:\anacnoda3\envs\Legacy-Code-Migration\python.exe     
cachedir: .pytest_cache
rootdir: D:\FILES\Legacy-Code-Migration
plugins: anyio-4.9.0, langsmith-0.4.4
collected 18 items

AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptManagerInitialization::test_initialization_creates_correct_attributes PASSED [  5%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptManagerInitialization::test_prompt_constants_have_correct_values PASSED [ 11%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptManagerInitialization::test_prompt_directory_is_set_correctly PASSED [ 16%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptManagerInitialization::test_cache_initialization PASSED [ 22%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptRetrieval::test_get_prompt_returns_cached_template PASSED [ 27%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptRetrieval::test_get_prompt_returns_none_for_missing_key PASSED [ 33%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestYAMLLoading::test_load_prompt_from_yaml_with_valid_file PASSED [ 38%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestYAMLLoading::test_load_prompt_from_yaml_with_malformed_yaml PASSED [ 44%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestYAMLLoading::test_load_prompt_from_yaml_with_missing_system_prompt PASSED [ 50%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestYAMLLoading::test_load_prompt_from_yaml_with_missing_file PASSED [ 55%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestYAMLLoading::test_load_prompt_from_yaml_with_missing_section PASSED [ 61%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptTemplateStructure::test_template_contains_messages_placeholder PASSED [ 66%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptTemplateStructure::test_template_variable_substitution PASSED [ 72%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestErrorHandlingAndEdgeCases::test_get_prompt_with_empty_cache PASSED [ 77%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestErrorHandlingAndEdgeCases::test_initialization_with_missing_directory PASSED [ 83%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestErrorHandlingAndEdgeCases::test_yaml_with_empty_content PASSED [ 88%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptLoadingIntegration::test_load_all_prompts_loads_all_available_files PASSED [ 94%]
AntiPattern_Remediator/test/unit_test/prompt/test_prompt_manager.py::TestPromptLoadingIntegration::test_load_all_prompts_handles_partial_failures PASSED [100%]

================================================= 18 passed in 0.19s =================================================
```