"""
Smart Restaurant Recommender - Verification & Test Script
This script verifies that everything is set up correctly.
"""

import sys
import os
from pathlib import Path

def check_project_structure():
    """Verify all required files exist."""
    print("\n" + "="*60)
    print("🔍 VERIFYING PROJECT STRUCTURE")
    print("="*60 + "\n")
    
    required_files = {
        "app.py": "Main Streamlit application",
        "requirements.txt": "Python dependencies",
        "README.md": "Project documentation",
        "SETUP_GUIDE.md": "Setup instructions",
        "PROJECT_SUMMARY.md": "Project summary",
        "QUICK_START.txt": "Quick reference",
        "src/__init__.py": "Package initialization",
        "src/data_loader.py": "Data loading module",
        "src/recommender.py": "Recommendation engine",
        "src/utils.py": "Utility functions",
        "data/restaurants.csv": "Restaurant dataset",
    }
    
    project_root = Path(__file__).parent
    all_exist = True
    
    for file_path, description in required_files.items():
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path:<30} - {description}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Verify all required packages are installed."""
    print("\n" + "="*60)
    print("📦 CHECKING DEPENDENCIES")
    print("="*60 + "\n")
    
    required_packages = {
        "pandas": "Data manipulation",
        "numpy": "Numerical operations",
        "streamlit": "Web framework",
    }
    
    all_installed = True
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {package:<20} - {description}")
        except ImportError:
            print(f"❌ {package:<20} - NOT INSTALLED")
            all_installed = False
    
    return all_installed

def check_data_integrity():
    """Verify the dataset is accessible."""
    print("\n" + "="*60)
    print("📊 CHECKING DATA INTEGRITY")
    print("="*60 + "\n")
    
    try:
        import pandas as pd
        data_path = Path(__file__).parent / "data" / "restaurants.csv"
        
        if not data_path.exists():
            print("❌ Dataset file not found at", data_path)
            return False
        
        # Load and verify data
        df = pd.read_csv(data_path)
        
        required_columns = [
            'Restaurant Name', 'Cuisines', 'Average Cost for two',
            'Aggregate rating', 'City', 'Address'
        ]
        
        missing_cols = [col for col in required_columns if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing columns: {missing_cols}")
            return False
        
        print(f"✅ Dataset loaded successfully")
        print(f"   - Records: {len(df):,}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - Size: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking data: {str(e)}")
        return False

def print_next_steps():
    """Print next steps for running the app."""
    print("\n" + "="*60)
    print("🚀 NEXT STEPS")
    print("="*60 + "\n")
    
    print("To run the Smart Restaurant Recommender:\n")
    
    if sys.platform == "win32":
        print("Option 1 (Easiest):")
        print("  >> run.bat\n")
    else:
        print("Option 1 (Easiest):")
        print("  $ bash run.sh\n")
    
    print("Option 2 (Manual):")
    print("  1. Open terminal in project directory")
    print("  2. Run: streamlit run app.py")
    print("  3. Open: http://localhost:8501\n")

def print_features():
    """Print project features."""
    print("="*60)
    print("✨ PROJECT FEATURES")
    print("="*60 + "\n")
    
    features = [
        ("🍜 Smart Filtering", "Filter by cuisine, budget, and rating"),
        ("📊 Interactive UI", "Beautiful Streamlit web interface"),
        ("⭐ Smart Ranking", "Results ranked by rating and popularity"),
        ("💾 Export Feature", "Download recommendations as CSV"),
        ("📈 Analytics", "Dataset statistics and insights"),
        ("🎨 Responsive Design", "Works on desktop and tablet"),
        ("⚡ Fast Performance", "<100ms filtering and ranking"),
        ("📚 Well Documented", "Comprehensive code comments"),
        ("✅ Error Handling", "Graceful handling of edge cases"),
        ("🔒 Data Validation", "Input validation throughout"),
    ]
    
    for feature, description in features:
        print(f"  {feature:<25} - {description}")
    print()

def main():
    """Run all verification checks."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🍽️  Smart Restaurant Recommender - Setup Verification  ".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run checks
    structure_ok = check_project_structure()
    dependencies_ok = check_dependencies()
    data_ok = check_data_integrity()
    
    # Print features
    print_features()
    
    # Print summary
    print("="*60)
    print("📋 VERIFICATION SUMMARY")
    print("="*60 + "\n")
    
    checks = [
        ("Project Structure", structure_ok),
        ("Dependencies", dependencies_ok),
        ("Data Integrity", data_ok),
    ]
    
    all_ok = all(status for _, status in checks)
    
    for check_name, status in checks:
        symbol = "✅" if status else "❌"
        print(f"{symbol} {check_name:<30} - {'PASS' if status else 'FAIL'}")
    
    print()
    
    if all_ok:
        print("🎉 ALL CHECKS PASSED! Project is ready to use.\n")
        print_next_steps()
        return 0
    else:
        print("⚠️  Some checks failed. Please review the issues above.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
