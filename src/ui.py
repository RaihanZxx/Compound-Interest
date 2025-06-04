import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.text import Text
from rich import box
from datetime import datetime
from .calculator import CompoundInterestCalculator
from .database import Database
from .utils import format_currency, get_currency_symbol # Corrected import

console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = Text("Compound Interest Calculator\nby HanSoBored", style="bold cyan", justify="center")
    console.print(Panel(banner, border_style="green", box=box.ROUNDED, padding=(1, 2)))

def get_valid_input(prompt: str, prompt_type, min_val: float, error_msg: str, max_val: float = None, default_val=None):
    """
    Helper function to get validated user input.
    :param prompt: The prompt message to display.
    :param prompt_type: The rich.prompt type (FloatPrompt, IntPrompt, Prompt).
    :param min_val: Minimum allowed value.
    :param error_msg: Error message for value less than min_val.
    :param max_val: Maximum allowed value (optional).
    :param default_val: Default value if user enters nothing.
    :return: The validated input value.
    """
    while True:
        try:
            if default_val is not None:
                # rich.prompt.FloatPrompt/IntPrompt expect float/int for default
                value = prompt_type.ask(prompt, default=default_val) 
            else:
                value = prompt_type.ask(prompt)
            
            if value < min_val:
                console.print(error_msg, style="red")
                continue
            if max_val is not None and value > max_val:
                console.print(f"Value must not exceed {max_val:.2f}.", style="red")
                continue
            return value
        except ValueError:
            console.print("Invalid input. Please enter a valid number.", style="red")
        except TypeError: 
            console.print("Invalid default value type. Please check internal logic.", style="red")
            return None 

def get_valid_date(prompt: str, default_date: str = None):
    """Helper function to get a valid date string (YYYY-MM-DD)."""
    while True:
        date_str = Prompt.ask(prompt, default=default_date if default_date else "")
        if not date_str:
            return None # Allow empty string for optional date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            console.print("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-31).", style="red")

def display_results(principal: float, payment: float, payment_frequency: str, rate: float, 
                    time: float, compounds_per_year: int, tax_rate: float, fee_rate: float, 
                    amount: float, interest: float, currency: str):
    console.print("\n[bold green]Results:[/bold green]")
    
    total_invested_str = ""
    if payment > 0:
        total_invested = payment * compounds_per_year * time
        total_invested_str = f"[bold]Total Invested:[/bold] {format_currency(total_invested, currency)}\n"

    panel_content = (
        f"[bold]Principal:[/bold] {format_currency(principal, currency)}\n" if principal > 0 else ""
    ) + (
        f"[bold]Payment:[/bold] {format_currency(payment, currency)} per {payment_frequency}\n" if payment > 0 else ""
    ) + total_invested_str + (
        f"[bold]Interest Rate:[/bold] {rate:.2f}%\n"
        f"[bold]Time:[/bold] {time:.2f} years\n"
        f"[bold]Compounding Frequency:[/bold] {compounds_per_year} times/year\n"
        f"[bold]Tax Rate:[/bold] {tax_rate:.2f}%\n"
        f"[bold]Fee Rate:[/bold] {fee_rate:.2f}%\n\n"
        f"[bold cyan]Final Amount:[/bold cyan] {format_currency(amount, currency)}\n"
        f"[bold cyan]Interest Earned:[/bold cyan] {format_currency(interest, currency)}"
    )
    console.print(Panel(
        panel_content,
        title="Compound Interest Summary",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    ))

def display_yearly_growth(growth: list, currency: str, show_graph: bool = True):
    if not growth:
        console.print("[yellow]No yearly growth data to display.[/yellow]")
        return
        
    table = Table(title="Yearly Growth", box=box.MINIMAL)
    table.add_column("Year", style="cyan", justify="center", width=10)
    table.add_column("Amount", style="green", justify="right", width=20)
    if show_graph:
        table.add_column("Growth Graph", style="green", justify="left", width=30) 

    max_amount = max(amount for _, amount in growth) if growth else 1.0 # Avoid division by zero
    
    for year, amount in growth:
        formatted_amount = format_currency(amount, currency)
        if show_graph:
            bar_length = int((amount / max_amount) * 20) if max_amount > 0 else 0
            bar = "█" * min(bar_length, 20) # Cap bar length
            table.add_row(str(year), formatted_amount, bar)
        else:
            table.add_row(str(year), formatted_amount)
    console.print(table)

def display_comparison(scenarios: list, currency: str):
    if not scenarios:
        console.print("[yellow]No scenarios to compare.[/yellow]")
        return

    table = Table(title="Scenario Comparison", box=box.MINIMAL)
    table.add_column("Scenario", style="cyan", width=10)
    table.add_column("Principal/Payment", style="green", width=25)
    table.add_column("Rate", style="green", width=10)
    table.add_column("Time", style="green", width=10)
    table.add_column("Compounds/Year", style="green", width=15)
    table.add_column("Tax Rate", style="green", width=10)
    table.add_column("Fee Rate", style="green", width=10)
    table.add_column("Amount", style="green", width=20)
    table.add_column("Interest", style="green", width=20)
    for i, s in enumerate(scenarios, 1):
        principal_payment_str = ""
        if s['payment'] > 0:
            principal_payment_str = f"{format_currency(s['payment'], currency)}/{s['payment_frequency']}"
        elif s['principal'] > 0:
            principal_payment_str = format_currency(s['principal'], currency)
        
        table.add_row(
            f"Scenario {i}",
            principal_payment_str,
            f"{s['rate']:.2f}%",
            f"{s['time']:.2f} yrs",
            str(s['compounds_per_year']),
            f"{s['tax_rate']:.2f}%",
            f"{s['fee_rate']:.2f}%",
            format_currency(s['amount'], currency),
            format_currency(s['interest'], currency)
        )
    console.print(table)

def display_monte_carlo(results: dict, currency: str):
    console.print("\n[bold green]Monte Carlo Simulation Results:[/bold green]")
    console.print(Panel(
        f"[bold]Mean Amount:[/bold] {format_currency(results['mean'], currency)}\n"
        f"[bold]Min Amount:[/bold] {format_currency(results['min'], currency)}\n"
        f"[bold]Max Amount:[/bold] {format_currency(results['max'], currency)}\n"
        f"[bold]Standard Deviation:[/bold] {format_currency(results['std'], currency)}",
        title="Simulation Summary",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2)
    ))

def display_templates(templates: list, currency: str):
    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        return

    table = Table(title="Saved Templates", box=box.MINIMAL)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Name", style="green", width=15)
    table.add_column("Principal/Payment", style="green", width=25)
    table.add_column("Rate", style="green", width=10)
    table.add_column("Time", style="green", width=10)
    table.add_column("Compounds/Year", style="green", width=15)
    table.add_column("Tax Rate", style="green", width=10)
    table.add_column("Fee Rate", style="green", width=10)
    for t in templates:
        principal_payment_str = ""
        if t['payment'] > 0:
            principal_payment_str = f"{format_currency(t['payment'], currency)}/{t['payment_frequency']}" 
        elif t['principal'] > 0:
            principal_payment_str = format_currency(t['principal'], currency)
        
        table.add_row(
            str(t['id']),
            t['name'],
            principal_payment_str,
            f"{t['rate']:.2f}%",
            f"{t['time']:.2f} yrs",
            str(t['compounds_per_year']),
            f"{t['tax_rate']:.2f}%",
            f"{t['fee_rate']:.2f}%"
        )
    console.print(table)

def display_notifications(notifications: list, currency: str):
    if notifications:
        console.print("\n[bold yellow]Upcoming Investment Targets:[/bold yellow]")
        table = Table(box=box.MINIMAL)
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Initial/Payment", style="green", width=20)
        table.add_column("Current Value", style="green", width=20) 
        table.add_column("Target Date", style="magenta", width=15)
        for n in notifications:
            calc_type = "Lump Sum" if n['principal'] > 0 else "Regular Savings"
            initial_val_str = ""
            if n['payment'] > 0:
                initial_val_str = f"{format_currency(n['payment'], currency)}/{n['payment_frequency']}" 
            elif n['principal'] > 0:
                initial_val_str = format_currency(n['principal'], currency)

            table.add_row(
                str(n['id']),
                calc_type,
                initial_val_str,
                format_currency(n['amount'], currency), 
                n['target_date']
            )
        console.print(table)

def display_history(history: list, currency: str):
    if not history:
        console.print("[yellow]No calculations found in history.[/yellow]\n")
        return

    table = Table(title="Calculation History", box=box.MINIMAL)
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Type", style="cyan", width=10)
    table.add_column("Principal/Payment", style="green", width=25)
    table.add_column("Rate", style="green", width=10)
    table.add_column("Time", style="green", width=10)
    table.add_column("Compounds/Year", style="green", width=15)
    table.add_column("Tax Rate", style="green", width=10)
    table.add_column("Fee Rate", style="green", width=10)
    table.add_column("Amount", style="green", width=20)
    table.add_column("Interest", style="green", width=20)
    table.add_column("Timestamp", style="magenta", width=20)
    for row in history:
        calc_type = "Lump Sum" if row['principal'] > 0 else "Regular Savings"
        principal_payment_str = ""
        if row['payment'] > 0:
            principal_payment_str = f"{format_currency(row['payment'], currency)}/{row['payment_frequency']}" 
        elif row['principal'] > 0:
            principal_payment_str = format_currency(row['principal'], currency)
        
        table.add_row(
            str(row['id']),
            calc_type,
            principal_payment_str,
            f"{row['rate']:.2f}%",
            f"{row['time']:.2f} yrs",
            str(row['compounds_per_year']),
            f"{row['tax_rate']:.2f}%",
            f"{row['fee_rate']:.2f}%",
            format_currency(row['amount'], currency),
            format_currency(row['interest'], currency),
            row['timestamp']
        )
    console.print(table)

def main_menu(currency: str = "USD"):
    calculator = CompoundInterestCalculator()
    db = Database()
    show_graph = True  # Default: show growth graph
    
    # Clear screen at startup
    clear_screen()
    
    while True:
        notifications = db.get_notifications()
        print_banner()
        if notifications:
            display_notifications(notifications, currency)
        
        console.print("\n[bold]Menu:[/bold]")
        console.print("1. Calculate Compound Interest (Lump Sum)")
        console.print("2. Calculate Regular Savings")
        console.print("3. Compare Scenarios")
        console.print("4. Monte Carlo Simulation")
        console.print("5. Goal Calculator")
        console.print("6. Save Template")
        console.print("7. Load Template")
        console.print("8. View History")
        console.print("9. Export History to CSV")
        console.print("10. Process Batch from JSON")
        console.print(f"11. Toggle Growth Graph (Currently: {'On' if show_graph else 'Off'})")
        console.print("12. Exit")
        
        choice = Prompt.ask("Select an option", choices=[str(i) for i in range(1, 13)], default="1")
        
        clear_screen()
        
        if choice == "1": # Calculate Compound Interest (Lump Sum)
            principal = get_valid_input(f"Principal amount ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Principal must be non-negative.")
            rate = get_valid_input("Annual interest rate (%)", FloatPrompt, 0.0, "Rate must be non-negative.", max_val=200.0)
            time = get_valid_input("Time (years)", FloatPrompt, 0.0, "Time must be non-negative.")
            compounds_per_year = get_valid_input(
                "Compounding frequency per year", IntPrompt, 1, "Compounding frequency must be 1 or more.", default_val=12
            )
            tax_rate = get_valid_input("Tax rate (%)", FloatPrompt, 0.0, "Tax rate must be non-negative.", max_val=100.0)
            fee_rate = get_valid_input("Fee rate (%)", FloatPrompt, 0.0, "Fee rate must be non-negative.", max_val=100.0)
            target_date = get_valid_date("Target date (YYYY-MM-DD, optional)")
            
            amount, interest = calculator.calculate(principal, rate, time, compounds_per_year, tax_rate, fee_rate)
            db.save_calculation(principal, 0.0, None, rate, time, compounds_per_year, tax_rate, fee_rate, amount, interest, target_date)
            display_results(principal, 0.0, None, rate, time, compounds_per_year, tax_rate, fee_rate, amount, interest, currency)
            display_yearly_growth(calculator.yearly_growth(principal, rate, time, compounds_per_year, tax_rate, fee_rate), currency, show_graph)
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "2": # Calculate Regular Savings
            payment = get_valid_input(f"Payment amount per period ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Payment must be non-negative.")
            payment_frequency_choices = ["weekly", "monthly", "quarterly", "yearly"]
            payment_frequency = Prompt.ask("Payment frequency", choices=payment_frequency_choices, default="monthly")
            
            compounds_map = {'weekly': 52, 'monthly': 12, 'quarterly': 4, 'yearly': 1}
            compounds_per_year = compounds_map.get(payment_frequency, 12) 

            rate = get_valid_input("Annual interest rate (%)", FloatPrompt, 0.0, "Rate must be non-negative.", max_val=200.0)
            time = get_valid_input("Time (years)", FloatPrompt, 0.0, "Time must be non-negative.")
            tax_rate = get_valid_input("Tax rate (%)", FloatPrompt, 0.0, "Tax rate must be non-negative.", max_val=100.0)
            fee_rate = get_valid_input("Fee rate (%)", FloatPrompt, 0.0, "Fee rate must be non-negative.", max_val=100.0)
            target_date = get_valid_date("Target date (YYYY-MM-DD, optional)")
            
            amount, interest = calculator.calculate_regular_savings(payment, rate, time, compounds_per_year, tax_rate, fee_rate)
            db.save_calculation(0.0, payment, payment_frequency, rate, time, compounds_per_year, tax_rate, fee_rate, amount, interest, target_date)
            display_results(0.0, payment, payment_frequency, rate, time, compounds_per_year, tax_rate, fee_rate, amount, interest, currency)
            display_yearly_growth(calculator.yearly_growth_regular_savings(payment, rate, time, compounds_per_year, tax_rate, fee_rate), currency, show_graph)
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "3": # Compare Scenarios
            scenarios = []
            num_scenarios = get_valid_input("How many scenarios to compare?", IntPrompt, 2, "Number of scenarios must be at least 2.", default_val=2)
            
            for i in range(num_scenarios):
                console.print(f"\n[bold]Scenario {i+1}[/bold]")
                calc_type = Prompt.ask("Calculate type", choices=["lump sum", "regular savings"], default="lump sum")
                
                principal = 0.0
                payment = 0.0
                payment_frequency = None
                compounds_per_year = 0
                
                if calc_type == "lump sum":
                    principal = get_valid_input(f"Principal amount ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Principal must be non-negative.")
                    compounds_per_year = get_valid_input(
                        "Compounding frequency per year", IntPrompt, 1, "Compounding frequency must be 1 or more.", default_val=12
                    )
                else: # regular savings
                    payment = get_valid_input(f"Payment amount per period ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Payment must be non-negative.")
                    payment_frequency_choices = ["weekly", "monthly", "quarterly", "yearly"]
                    payment_frequency = Prompt.ask("Payment frequency", choices=payment_frequency_choices, default="monthly")
                    compounds_map = {'weekly': 52, 'monthly': 12, 'quarterly': 4, 'yearly': 1}
                    compounds_per_year = compounds_map.get(payment_frequency, 12)

                rate = get_valid_input("Annual interest rate (%)", FloatPrompt, 0.0, "Rate must be non-negative.", max_val=200.0)
                time = get_valid_input("Time (years)", FloatPrompt, 0.0, "Time must be non-negative.")
                tax_rate = get_valid_input("Tax rate (%)", FloatPrompt, 0.0, "Tax rate must be non-negative.", max_val=100.0)
                fee_rate = get_valid_input("Fee rate (%)", FloatPrompt, 0.0, "Fee rate must be non-negative.", max_val=100.0)
                
                amount = 0.0
                interest = 0.0
                if calc_type == "lump sum":
                    amount, interest = calculator.calculate(principal, rate, time, compounds_per_year, tax_rate, fee_rate)
                else:
                    amount, interest = calculator.calculate_regular_savings(payment, rate, time, compounds_per_year, tax_rate, fee_rate)
                
                scenarios.append({
                    'principal': principal,
                    'payment': payment,
                    'payment_frequency': payment_frequency,
                    'rate': rate,
                    'time': time,
                    'compounds_per_year': compounds_per_year,
                    'tax_rate': tax_rate,
                    'fee_rate': fee_rate,
                    'amount': amount,
                    'interest': interest
                })
            display_comparison(scenarios, currency)
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "4": # Monte Carlo Simulation
            principal = get_valid_input(f"Principal amount ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Principal must be non-negative.")
            rate = get_valid_input("Annual interest rate (%)", FloatPrompt, 0.0, "Rate must be non-negative.", max_val=200.0)
            time = get_valid_input("Time (years)", FloatPrompt, 0.0, "Time must be non-negative.")
            compounds_per_year = get_valid_input(
                "Compounding frequency per year", IntPrompt, 1, "Compounding frequency must be 1 or more.", default_val=12
            )
            tax_rate = get_valid_input("Tax rate (%)", FloatPrompt, 0.0, "Tax rate must be non-negative.", max_val=100.0)
            fee_rate = get_valid_input("Fee rate (%)", FloatPrompt, 0.0, "Fee rate must be non-negative.", max_val=100.0)
            simulations = get_valid_input("Number of simulations", IntPrompt, 100, "Number of simulations must be at least 100.", default_val=1000)
            
            results = calculator.monte_carlo_simulation(principal, rate, time, compounds_per_year, tax_rate, fee_rate, simulations)
            display_monte_carlo(results, currency)
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "5": # Goal Calculator
            console.print("\n[bold]Goal Calculator[/bold]")
            goal_choice = Prompt.ask("Select goal type (1. Calculate Principal / 2. Calculate Time)", choices=["1", "2"], default="1")
            
            target_amount = get_valid_input(f"Target amount ({get_currency_symbol(currency)})", FloatPrompt, 0.01, "Target amount must be positive.")
            rate = get_valid_input("Annual interest rate (%)", FloatPrompt, 0.0, "Rate must be non-negative.", max_val=200.0)
            compounds_per_year = get_valid_input(
                "Compounding frequency per year", IntPrompt, 1, "Compounding frequency must be 1 or more.", default_val=12
            )
            
            # For simplicity, goal calculation does not account for tax/fees directly
            # as it complicates the inverse formula significantly.
            # User should calculate gross target amount for tax/fees.
            
            if goal_choice == "1": # Calculate Principal
                time = get_valid_input("Time (years)", FloatPrompt, 0.01, "Time must be positive.")
                principal = calculator.calculate_principal(target_amount, rate, time, compounds_per_year)
                console.print(Panel(
                    f"[bold]Required Principal:[/bold] {format_currency(principal, currency)}",
                    title="Goal Result - Required Principal",
                    border_style="blue",
                    box=box.ROUNDED,
                    padding=(1, 2)
                ))
            else: # Calculate Time
                principal = get_valid_input(f"Principal amount ({get_currency_symbol(currency)})", FloatPrompt, 0.01, "Principal must be positive.")
                time = calculator.calculate_time(target_amount, principal, rate, compounds_per_year)
                
                time_display = f"{time:.2f} years"
                if time == float('inf'):
                    time_display = "Infinite (target not reachable with given rate or principal)"
                elif time == 0.0 and target_amount > principal:
                     time_display = "Target amount cannot be reached with given principal and zero rate."
                
                console.print(Panel(
                    f"[bold]Required Time:[/bold] {time_display}",
                    title="Goal Result - Required Time",
                    border_style="blue",
                    box=box.ROUNDED,
                    padding=(1, 2)
                ))
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "6": # Save Template
            name = Prompt.ask("Input template name: ")
            calc_type = Prompt.ask("Calculate type", choices=["lump sum", "regular savings"], default="lump sum")
            
            principal = 0.0
            payment = 0.0
            payment_frequency = None
            compounds_per_year = 0
            
            if calc_type == "lump sum":
                principal = get_valid_input(f"Principal amount ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Principal must be non-negative.")
                compounds_per_year = get_valid_input(
                    "Compounding frequency per year", IntPrompt, 1, "Compounding frequency must be 1 or more.", default_val=12
                )
            else:
                payment = get_valid_input(f"Payment amount per period ({get_currency_symbol(currency)})", FloatPrompt, 0.0, "Payment must be non-negative.")
                payment_frequency_choices = ["weekly", "monthly", "quarterly", "yearly"]
                payment_frequency = Prompt.ask("Payment frequency", choices=payment_frequency_choices, default="monthly")
                compounds_map = {'weekly': 52, 'monthly': 12, 'quarterly': 4, 'yearly': 1}
                compounds_per_year = compounds_map.get(payment_frequency, 12)

            rate = get_valid_input("Annual interest rate (%)", FloatPrompt, 0.0, "Rate must be non-negative.", max_val=200.0)
            time = get_valid_input("Time (years)", FloatPrompt, 0.0, "Time must be non-negative.")
            tax_rate = get_valid_input("Tax rate (%)", FloatPrompt, 0.0, "Tax rate must be non-negative.", max_val=100.0)
            fee_rate = get_valid_input("Fee rate (%)", FloatPrompt, 0.0, "Fee rate must be non-negative.", max_val=100.0)
            
            db.save_template(name, principal, payment, payment_frequency, rate, time, compounds_per_year, tax_rate, fee_rate)
            console.print(f"[green]Successfully saved template '{name}'![/green]\n")
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "7": # Load Template
            templates = db.get_templates()
            if templates:
                display_templates(templates, currency)
                template_id = get_valid_input("Select template ID", IntPrompt, 1, "Template ID must be a positive integer.")
                
                selected_template = next((t for t in templates if t['id'] == template_id), None)
                
                if selected_template:
                    console.print(f"[green]Loading template '{selected_template['name']}'...[/green]")
                    
                    principal = selected_template['principal']
                    payment = selected_template['payment']
                    payment_frequency = selected_template['payment_frequency']
                    rate = selected_template['rate']
                    time = selected_template['time']
                    compounds_per_year = selected_template['compounds_per_year']
                    tax_rate = selected_template['tax_rate']
                    fee_rate = selected_template['fee_rate']

                    amount = 0.0
                    interest = 0.0

                    if payment > 0: # Regular Savings Template
                        amount, interest = calculator.calculate_regular_savings(
                            payment, rate, time, compounds_per_year, tax_rate, fee_rate
                        )
                        db.save_calculation(
                            0.0, payment, payment_frequency, rate, time, compounds_per_year, tax_rate, 
                            fee_rate, amount, interest, None # Target date not saved in template
                        )
                        display_results(
                            0.0, payment, payment_frequency, rate, time, compounds_per_year, tax_rate, 
                            fee_rate, amount, interest, currency
                        )
                        display_yearly_growth(
                            calculator.yearly_growth_regular_savings(
                                payment, rate, time, compounds_per_year, tax_rate, fee_rate
                            ), currency, show_graph # Pass currency
                        )
                    else: # Lump Sum Template
                        amount, interest = calculator.calculate(
                            principal, rate, time, compounds_per_year, tax_rate, fee_rate
                        )
                        db.save_calculation(
                            principal, 0.0, None, rate, time, compounds_per_year, tax_rate, 
                            fee_rate, amount, interest, None # Target date not saved in template
                        )
                        display_results(
                            principal, 0.0, None, rate, time, compounds_per_year, tax_rate, 
                            fee_rate, amount, interest, currency
                        )
                        display_yearly_growth(
                            calculator.yearly_growth(
                                principal, rate, time, compounds_per_year, tax_rate, fee_rate
                            ), currency, show_graph
                        )
                    input("Press Enter to continue...")
                    clear_screen()
                else:
                    console.print("[red]Invalid template ID.[/red]\n")
                    input("Press Enter to continue...")
                    clear_screen()
            else:
                console.print("[yellow]No templates found to load.[/yellow]\n")
                input("Press Enter to continue...")
                clear_screen()
        
        elif choice == "8": # View History
            history = db.get_history()
            display_history(history, currency) 
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "9": # Export History to CSV
            file_path = Prompt.ask("Enter CSV file path", default="calculations_history.csv")
            try:
                db.export_to_csv(file_path)
                console.print(f"[green]History exported to {file_path}[/green]\n")
            except IOError as e:
                console.print(f"[red]Error exporting history: {e}[/red]\n")
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "10": # Process Batch from JSON
            file_path = Prompt.ask("Enter JSON file path (e.g., batch_input.json)")
            default_tax_rate = get_valid_input("Default tax rate for batch (%) (used if not in JSON)", FloatPrompt, 0.0, "Tax rate must be non-negative.", max_val=100.0, default_val=0.0)
            default_fee_rate = get_valid_input("Default fee rate for batch (%) (used if not in JSON)", FloatPrompt, 0.0, "Fee rate must be non-negative.", max_val=100.0, default_val=0.0)
            
            try:
                results = calculator.process_batch(file_path, default_tax_rate, default_fee_rate)
                console.print(f"[bold green]Processing Batch Results from {file_path}:[/bold green]\n")
                if not results:
                    console.print("[yellow]No calculations processed from the batch file.[/yellow]\n")
                
                for i, result in enumerate(results):
                    console.print(f"\n[bold blue]Batch Calculation {i+1}:[/bold blue]")
                    db.save_calculation(
                        result['principal'], result['payment'], result.get('payment_frequency', None), 
                        result['rate'], result['time'], result['compounds_per_year'], 
                        result['tax_rate'], result['fee_rate'], result['amount'], result['interest']
                    )
                    display_results(
                        result['principal'], result['payment'], result.get('payment_frequency', None), 
                        result['rate'], result['time'], result['compounds_per_year'], 
                        result['tax_rate'], result['fee_rate'], result['amount'], result['interest'], currency
                    )
                console.print("\n[green]Batch processing complete.[/green]\n")
            except ValueError as e:
                console.print(f"[red]Error processing batch file: {str(e)}[/red]\n")
            except Exception as e:
                console.print(f"[red]An unexpected error occurred during batch processing: {str(e)}[/red]\n")
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "11": # Toggle Growth Graph
            show_graph = not show_graph
            console.print(f"[green]Growth graph turned {'on' if show_graph else 'off'}.[/green]\n")
            input("Press Enter to continue...")
            clear_screen()
        
        elif choice == "12": # Exit
            console.print("[green]Thank you for using Compound Interest Calculator by HanSoBored![/green]")
            input("Press Enter to exit...")
            clear_screen()
            break