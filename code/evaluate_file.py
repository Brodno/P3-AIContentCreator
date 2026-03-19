
import os
import sys

# Add current directory to path so imports work
sys.path.append(os.getcwd())

from modules.context_loader import load_context
from modules.evaluator import evaluate_post

def main():
    # File path relative to this script
    file_path = os.path.join("..", "..", "..", "MARKETING", "02_PLAN_2026", "posty_luty_2026", "4__Wydajność_nominalna_vs_rzeczywista___ukryty_pod.md")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Reading file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Load context
    context = load_context()
    
    print("\nEvaluating post...")
    # Evaluate
    result = evaluate_post(content, platform="LinkedIn", context=context)
    
    print("\n" + "="*50)
    print("EVALUATION RESULT")
    print("="*50)
    print(f"TOTAL SCORE: {result.get('total_score', 0)}/100")
    print("-" * 20)
    print(f"Breakdown:")
    for k, v in result.get('breakdown', {}).items():
        print(f"  {k}: {v}")
    
    print("-" * 20)
    print(f"Feedback: {result.get('feedback', '')}")
    print("-" * 20)
    if result.get('logic_check', {}).get('passed') is False:
        print("LOGIC ISSUES:")
        for err in result['logic_check'].get('errors', []):
            print(f"  - {err}")
    else:
        print("Logic Check: PASSED")

if __name__ == "__main__":
    main()
