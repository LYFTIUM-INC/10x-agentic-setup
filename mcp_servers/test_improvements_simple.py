#!/usr/bin/env python3
"""
Simple test to verify MCP improvements are in place
"""

import os
import json
from pathlib import Path

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file_contains(file_path, search_strings, description):
    """Check if file contains specific strings"""
    if not os.path.exists(file_path):
        print(f"{RED}✗ {description} - File not found: {file_path}{RESET}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    all_found = True
    for search_str in search_strings:
        if search_str in content:
            print(f"{GREEN}✓ {description} - Found: {search_str}{RESET}")
        else:
            print(f"{RED}✗ {description} - Missing: {search_str}{RESET}")
            all_found = False
    
    return all_found

def main():
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}MCP Improvements Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    base_path = Path(__file__).parent
    
    # Test 1: Check base server improvements
    print(f"{YELLOW}1. Base Server Improvements:{RESET}")
    base_server_checks = check_file_contains(
        base_path / "shared/src/base_server.py",
        [
            "register_prompt",
            "ResponseFormatter",
            "ProgressManager", 
            "HealthChecker",
            "_register_health_resources"
        ],
        "Base server enhancements"
    )
    
    # Test 2: Check utility files exist
    print(f"\n{YELLOW}2. New Utility Files:{RESET}")
    utils_path = base_path / "shared/src/utils"
    utils_files = [
        ("response_formatter.py", "Response Formatter"),
        ("progress_manager.py", "Progress Manager"),
        ("health_checker.py", "Health Checker")
    ]
    
    utils_exist = True
    for file_name, desc in utils_files:
        file_path = utils_path / file_name
        if file_path.exists():
            print(f"{GREEN}✓ {desc} exists{RESET}")
        else:
            print(f"{RED}✗ {desc} missing{RESET}")
            utils_exist = False
    
    # Test 3: Check ML Code Intelligence prompts
    print(f"\n{YELLOW}3. ML Code Intelligence Prompts:{RESET}")
    ml_prompts = check_file_contains(
        base_path / "ml_code_intelligence/src/server.py",
        [
            "_register_prompts",
            "analyze_codebase_prompt",
            "refactor_for_pattern_prompt",
            "security_audit_prompt",
            "performance_optimization_prompt",
            "code_review_prompt"
        ],
        "ML Code Intelligence prompts"
    )
    
    # Test 4: Check Context-Aware Memory prompts
    print(f"\n{YELLOW}4. Context-Aware Memory Prompts:{RESET}")
    memory_prompts = check_file_contains(
        base_path / "context_aware_memory/src/server.py",
        [
            "_register_prompts",
            "memory_recap_prompt",
            "predict_workflow_prompt",
            "context_analysis_prompt",
            "memory_optimization_prompt",
            "knowledge_extraction_prompt"
        ],
        "Context-Aware Memory prompts"
    )
    
    # Test 5: Check progress token implementation
    print(f"\n{YELLOW}5. Progress Token Implementation:{RESET}")
    progress_impl = check_file_contains(
        base_path / "ml_code_intelligence/src/server.py",
        [
            "progress_token: Optional[str]",
            "progress_manager.start_operation",
            "progress_manager.update_progress",
            "progress_manager.complete_operation"
        ],
        "Progress token in ML Code Intelligence"
    )
    
    # Test 6: Check response formatter usage
    print(f"\n{YELLOW}6. Response Formatter Usage:{RESET}")
    response_usage = check_file_contains(
        base_path / "ml_code_intelligence/src/server.py",
        [
            "response_formatter.success",
            "response_formatter.error"
        ],
        "Response formatter in ML Code Intelligence"
    )
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Summary:{RESET}")
    
    all_passed = all([
        base_server_checks,
        utils_exist,
        ml_prompts,
        memory_prompts,
        progress_impl,
        response_usage
    ])
    
    if all_passed:
        print(f"{GREEN}✅ All improvements are in place!{RESET}")
        
        # List key improvements
        print(f"\n{BLUE}Key Improvements Implemented:{RESET}")
        print(f"• {GREEN}Prompts:{RESET} 5 prompts per server for common workflows")
        print(f"• {GREEN}Response Format:{RESET} Standardized success/error/partial responses")
        print(f"• {GREEN}Progress Tokens:{RESET} Real-time progress for long operations")
        print(f"• {GREEN}Health Checks:{RESET} Built-in health monitoring resources")
        print(f"• {GREEN}Base Integration:{RESET} All features integrated in BaseMCPServer")
        
    else:
        print(f"{RED}❌ Some improvements are missing or incomplete{RESET}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)