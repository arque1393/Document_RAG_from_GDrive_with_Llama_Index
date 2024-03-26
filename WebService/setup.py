import sys
import os
from pathlib import Path
base_dir = Path(__file__).resolve().parent.parent
print(base_dir)
sys.path.append(str(base_dir))
os.system('python fast_api_main.py')