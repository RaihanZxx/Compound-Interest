# Compound Interest Calculator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/downloads/)
![Made with Rich](https://img.shields.io/badge/Made%20with-Rich-green.svg)

---

## ✨ Overview

A powerful and intuitive command-line interface (CLI) application for calculating and visualizing compound interest. Designed with a clean, minimalist interface using `rich` for an enhanced user experience.

---

## 🚀 Features

-   **Lump Sum Calculation:** Calculate future value and interest for a single initial investment.
-   **Regular Savings (Annuity):** Project growth for periodic contributions.
-   **Scenario Comparison:** Analyze multiple investment scenarios side-by-side.
-   **Monte Carlo Simulation:** Understand potential outcomes with varying interest rates.
-   **Goal Calculator:** Determine required principal or time to reach a financial target.
-   **Templates:** Save and load common calculation parameters for quick access.
-   **Calculation History:** Keep track of all your past calculations.
-   **Batch Processing:** Process multiple calculations from a JSON input file.
-   **Notifications:** Get alerts for upcoming target dates (if set).
-   **Configurable Currency:** Supports various currencies via `config.json` (e.g., USD, IDR, EUR).
-   **Interactive UI:** Built with `rich` for a visually appealing and user-friendly console experience.

---

## 🖼️ Previews

### Below are some previews of Compound Interest in action:
**Main Menu:**

<img src="https://github.com/RaihanZxx/Compound-Interest/blob/main/previews%2Fpreviews1.jpg" width="400">

**Calculate Regular Savings:**

<img src="https://github.com/RaihanZxx/Compound-Interest/blob/main/previews%2Fpreviews2.jpg" width="400">

---

## 🛠️ Getting Started

Follow these steps to get the application up and running on your local machine.

### Prerequisites

-   Python 3.x installed on your system.
-   `pip` (Python package installer).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RaihanZxx/Compound-Interest.git
    cd Compound-Interest
    ```
  
2.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    -   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Usage

To run the application, ensure your virtual environment is active and execute:

```bash
python3 main.py
```

The application will present a menu with various calculation options.

Example: Running Batch Calculations

You can use the batch_input.json file provided to test batch processing:

[
    {
        "principal": 10000,
        "rate": 5.0,
        "time": 10,
        "compounds_per_year": 12,
        "tax_rate": 10.0,
        "fee_rate": 1.0
    },
    {
        "principal": 5000,
        "rate": 3.5,
        "time": 5,
        "compounds_per_year": 4,
        "tax_rate": 5.0,
        "fee_rate": 0.5
    }
]

When prompted in the CLI, enter batch_input.json as the file path.

## ⚙️ Configuration

The config.json file allows you to set the default currency for calculations:

{
    "currency": "IDR"
}

Change "IDR" to your preferred currency code (e.g., "USD", "EUR", "GBP") to update the display currency.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

---

## 📬 Contact

For questions or feedback, reach out via GitHub Issues or contact the maintainer at:
- <img src="https://img.shields.io/badge/Telegram-%40HanSoBored-0088cc?style=flat-square&logo=telegram" alt="Telegram" height="20">
- <img src="https://img.shields.io/badge/Email-raihanzxzy%40gmail.com-d14836?style=flat-square&logo=gmail" alt="Email" height="20">