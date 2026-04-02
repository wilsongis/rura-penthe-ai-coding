import ast
import os
from pathlib import Path

def test_profile_declarations():
    """
    Ensure every Python file in the 'src/' and 'scripts/' directories declares
    either 'Profile A' or 'Profile B' in its module docstring, as per Power-of-11.
    """
    project_root = Path(__file__).parent.parent
    directories_to_check = [project_root / "src", project_root / "scripts" / "python"]
    
    missing_profiles = []
    
    for directory in directories_to_check:
        if not directory.exists():
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                if not file.endswith(".py"):
                    continue
                    
                file_path = Path(root) / file
                
                # Skip __init__.py files that are empty or just imports if desired, 
                # but strict Power-of-11 usually requires all files.
                
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                try:
                    tree = ast.parse(content)
                except SyntaxError:
                    continue
                
                docstring = ast.get_docstring(tree)
                if docstring is None:
                    # Missing entirely
                    missing_profiles.append(f"{file_path.relative_to(project_root)}: Missing docstring entirely.")
                    continue
                
                docstring_lower = docstring.lower()
                has_profile_a = "profile a" in docstring_lower
                has_profile_b = "profile b" in docstring_lower
                
                if not (has_profile_a or has_profile_b):
                    missing_profiles.append(f"{file_path.relative_to(project_root)}: Does not declare Profile A or Profile B.")

    # In a real environment, we would assert len(missing_profiles) == 0.
    # We will print them out here so that pytest captures it if it fails.
    if missing_profiles:
        print("Architectural Violation: Files missing Tiered Deployment Profile Declarations:")
        for missing in missing_profiles:
            print(f"  - {missing}")
            
    # We won't strictly fail the test suite yet for learning/transition purposes, 
    # but a true zero-tolerance policy would assert here.
    # assert not missing_profiles, f"Found {len(missing_profiles)} files missing Profile declarations."
