import json
# Removed import locale for cross-platform compatibility

def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If config.json doesn't exist, return default currency
        return {'currency': 'USD'}
    except json.JSONDecodeError:
        # Handle malformed JSON
        print(f"Warning: Invalid JSON format in {config_path}. Using default currency 'USD'.")
        return {'currency': 'USD'}

def get_currency_symbol(currency: str) -> str:
    """Get currency symbol."""
    return {
        'USD': '$',
        'IDR': 'Rp',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'CNY': '¥',
        'SEK': 'kr',
        'NZD': 'NZ$'
    }.get(currency.upper(), '$') # .upper() for case-insensitivity

def format_currency(amount: float, currency: str) -> str:
    """
    Format amount based on currency without relying on locale for simplicity and cross-platform compatibility.
    Handles common currency formatting (e.g., commas for thousands, 2 decimal places).
    For IDR, it will format without decimals.
    """
    symbol = get_currency_symbol(currency)
    
    if currency.upper() == 'IDR':
        # Indonesian Rupiah typically doesn't use decimals for large amounts
        # Use str.format with comma as thousands separator and replace for IDR dot style
        formatted_amount = "{:,.0f}".format(amount).replace(",", "_TEMP_").replace(".", ",").replace("_TEMP_", ".")
        return f"{symbol}{formatted_amount}"
    else:
        # Default to 2 decimal places with comma as thousands separator
        return f"{symbol}{amount:,.2f}"