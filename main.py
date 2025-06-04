from src.ui import main_menu
from src.utils import load_config
import sys # Import sys to access standard streams
import os # Import os to check for file existence

# Ensure the database file is in the root directory, not src/
# This is a good practice to keep data outside source code
db_path = "calculations.db"
# If running for the first time or if the database is missing/corrupted
# it will be initialized by the Database class.

if __name__ == "__main__":
    # Add project root to sys.path if not already there,
    # to ensure src modules are found correctly when running from root.
    # This might not be strictly necessary if always run from root, but good for robustness.
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        config = load_config()
        # Pass the currency setting from config to the UI
        main_menu(config.get('currency', 'USD'))
    except KeyboardInterrupt:
        print("\nCalculation cancelled by user. Exiting.")
    except Exception as e:
        print(f"\nAn unhandled error occurred: {str(e)}")
        import traceback
        traceback.print_exc() # Print full traceback for unhandled exceptions