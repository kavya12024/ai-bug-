"""
Test the fixers directly without Docker dependency
Tests the AI fixer with Ollama on all languages
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from ai_fixer import AIFixer
from error_parser import ErrorParser, Error
from utils.logger import setup_logger

logger = setup_logger(__name__)

def test_fixer_python():
    """Test Python fixer"""
    print("\n" + "="*70)
    print("TEST 1: PYTHON FIXER (Rule-based + Ollama)")
    print("="*70 + "\n")
    
    broken_code = """# This file has intentional errors for testing

# Missing import - numpy
import json, os

def calculate_mean(numbers):
    # Missing colon after if
    if len(numbers) > 0
        total = sum(numbers)
        return total / len(numbers)
    return 0

# Typo in True
if True:
    print("This is Ture") ; # Wrong spelling

print("Done")
"""
    
    print("Original code:")
    print(broken_code[:300] + "...\n")
    
    # Create errors
    errors = [
        Error(type='syntax', message="SyntaxError: expected ':'"),
        Error(type='typo', message="'Ture' should be 'True'")
    ]
    
    # Test rule-based fixer
    fixer = AIFixer(use_ollama=False)
    fixed_code = fixer.fix_code(broken_code, errors, language='python')
    
    print("After Rule-Based Fix:")
    print(fixed_code[:300] + "...\n")
    
    # Test Ollama fixer
    print("Testing Ollama CodeLlama fixer...")
    fixer_ollama = AIFixer(use_ollama=True, ollama_model="codellama:7b")
    fixed_code_ollama = fixer_ollama.fix_code(broken_code, errors, language='python')
    
    print("After Ollama Fix:")
    print(fixed_code_ollama[:300] + "...\n")
    
    return fixed_code != broken_code or fixed_code_ollama != broken_code

def test_fixer_javascript():
    """Test JavaScript fixer"""
    print("\n" + "="*70)
    print("TEST 2: JAVASCRIPT FIXER (Rule-based + Ollama)")
    print("="*70 + "\n")
    
    broken_code = """// This file has intentional JavaScript errors

// Missing semicolon and undefined function
const numbers = [1, 2, 3, 4, 5]
callUndefinedFunction()

// Function with syntax error
function calculateMean(nums) {
    if (nums.length > 0) {
        const total = nums.reduce((a, b) => a + b, 0)
        return total / nums.length
    }
    return 0
}

const mean = calculateMean(numbers)
console.log("Mean: " + mean)
"""
    
    print("Original code:")
    print(broken_code[:300] + "...\n")
    
    # Create errors
    errors = [
        Error(type='syntax', message="SyntaxError: Missing semicolon"),
    ]
    
    # Test rule-based fixer
    fixer = AIFixer(use_ollama=False)
    fixed_code = fixer.fix_code(broken_code, errors, language='javascript')
    
    print("After Rule-Based Fix:")
    print(fixed_code[:300] + "...\n")
    
    # Test Ollama fixer
    print("Testing Ollama CodeLlama fixer...")
    fixer_ollama = AIFixer(use_ollama=True, ollama_model="codellama:7b")
    fixed_code_ollama = fixer_ollama.fix_code(broken_code, errors, language='javascript')
    
    print("After Ollama Fix:")
    print(fixed_code_ollama[:300] + "...\n")
    
    return fixed_code != broken_code or fixed_code_ollama != broken_code

def test_fixer_cpp():
    """Test C++ fixer"""
    print("\n" + "="*70)
    print("TEST 3: C++ FIXER (Rule-based + Ollama)")
    print("="*70 + "\n")
    
    broken_code = """// C++ file with errors

// Missing includes
#include <vector>

int main() {
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    
    // Using cout without iostream
    std::cout << "Vector size: " << numbers.size() << std::endl;
    
    // Syntax error - missing semicolon
    int sum = 0
    
    for (int num : numbers) {
        sum += num
    }
    
    std::cout << "Sum: " << sum << std::endl;
    
    return 
}
"""
    
    print("Original code:")
    print(broken_code[:300] + "...\n")
    
    # Create errors
    errors = [
        Error(type='syntax', message="error: expected ';'"),
    ]
    
    # Test rule-based fixer
    fixer = AIFixer(use_ollama=False)
    fixed_code = fixer.fix_code(broken_code, errors, language='cpp')
    
    print("After Rule-Based Fix:")
    print(fixed_code[:300] + "...\n")
    
    # Test Ollama fixer
    print("Testing Ollama CodeLlama fixer...")
    fixer_ollama = AIFixer(use_ollama=True, ollama_model="codellama:7b")
    fixed_code_ollama = fixer_ollama.fix_code(broken_code, errors, language='cpp')
    
    print("After Ollama Fix:")
    print(fixed_code_ollama[:300] + "...\n")
    
    return fixed_code != broken_code or fixed_code_ollama != broken_code

def main():
    print("\n" + "="*70)
    print("AI BUG FIXER - DIRECT FIXER TESTS (All Languages)")
    print("="*70)
    
    results = {}
    
    try:
        results['python'] = test_fixer_python()
    except Exception as e:
        print(f"❌ Python test error: {e}")
        results['python'] = False
    
    try:
        results['javascript'] = test_fixer_javascript()
    except Exception as e:
        print(f"❌ JavaScript test error: {e}")
        results['javascript'] = False
    
    try:
        results['cpp'] = test_fixer_cpp()
    except Exception as e:
        print(f"❌ C++ test error: {e}")
        results['cpp'] = False
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    print(f"Python:     {'✅ FIXED' if results['python'] else '❌ NOT FIXED'}")
    print(f"JavaScript: {'✅ FIXED' if results['javascript'] else '❌ NOT FIXED'}")
    print(f"C++:        {'✅ FIXED' if results['cpp'] else '❌ NOT FIXED'}")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
