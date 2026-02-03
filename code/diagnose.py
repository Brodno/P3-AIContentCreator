import sys
import os
import importlib

print(f"Current Working Directory: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")
print(f"Version: {sys.version}")

print("\n--- Checking Imports ---")
try:
    import dotenv
    print(f"✅ dotenv imported (Version: {getattr(dotenv, '__version__', 'unknown')})")
except ImportError as e:
    print(f"❌ Failed to import dotenv: {e}")

try:
    import google.genai
    print(f"✅ google.genai imported")
except ImportError as e:
    print(f"❌ Failed to import google.genai: {e}")

print("\n--- Checking Project Structure ---")
modules_path = os.path.join(os.getcwd(), 'modules')
config_path = os.path.join(os.getcwd(), 'config')

if os.path.exists(modules_path):
    print(f"✅ 'modules' directory found at {modules_path}")
else:
    print(f"❌ 'modules' directory NOT found at {modules_path}")

if os.path.exists(config_path):
    print(f"✅ 'config' directory found at {config_path}")
else:
    print(f"❌ 'config' directory NOT found at {config_path}")

print("\n--- Checking Internal Imports ---")
sys.path.append(os.getcwd())
try:
    import config.gemini_config as gemini_config
    print("✅ Successfully imported config.gemini_config")
    
    if hasattr(gemini_config, 'generate_content_with_retry'):
         print("✅ Found generate_content_with_retry in gemini_config")
    else:
         print("❌ generate_content_with_retry NOT found in gemini_config")
         
except ImportError as e:
    print(f"❌ Failed to import config.gemini_config: {e}")

try:
    import modules.generator as generator
    print("✅ Successfully imported modules.generator")
except ImportError as e:
    print(f"❌ Failed to import modules.generator: {e}")

print("\n--- Checking .env ---")
env_path = os.path.join(os.getcwd(), '.env')
if os.path.exists(env_path):
    print(f"✅ .env found at {env_path}")
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    if key:
        print(f"✅ GEMINI_API_KEY found (starts with: {key[:4]}...)")
    else:
        print("❌ GEMINI_API_KEY is missing or empty in .env")
else:
    print(f"❌ .env NOT found at {env_path}")
    # Search for it
    print("Searching for .env in parent directories...")
    parent = os.path.dirname(os.getcwd())
    if os.path.exists(os.path.join(parent, '.env')):
        print(f"Found .env in parent: {parent}")
    else:
         print("Could not find .env in parent either.")
