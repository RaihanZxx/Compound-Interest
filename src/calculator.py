import math
import json
import numpy as np
from typing import List, Tuple, Dict
from datetime import datetime

class CompoundInterestCalculator:
    @staticmethod
    def calculate(principal: float, rate: float, time: float, compounds_per_year: int, 
                  tax_rate: float = 0, fee_rate: float = 0) -> Tuple[float, float]:
        """Calculate compound interest with tax and fees."""
        # Ensure rates are handled as decimals
        rate_decimal = rate / 100
        tax_rate_decimal = tax_rate / 100
        fee_rate_decimal = fee_rate / 100

        # Calculate future value before tax and fees
        amount = principal * math.pow((1 + rate_decimal / compounds_per_year), compounds_per_year * time)
        interest = amount - principal

        # Apply tax on interest and fee on the total amount
        tax = interest * tax_rate_decimal
        fee = amount * fee_rate_decimal
        
        final_amount = amount - tax - fee
        final_interest = interest - tax - fee
        return final_amount, final_interest

    @staticmethod
    def calculate_regular_savings(payment: float, rate: float, time: float, 
                                compounds_per_year: int, tax_rate: float = 0, 
                                fee_rate: float = 0) -> Tuple[float, float]:
        """
        Calculate future value of regular savings (annuity).
        Assumes payments are made at the end of each compounding period.
        """
        rate_decimal = rate / 100
        tax_rate_decimal = tax_rate / 100
        fee_rate_decimal = fee_rate / 100

        # Handle zero rate scenario to prevent division by zero or log errors
        if rate_decimal == 0:
            fv = payment * compounds_per_year * time
            total_invested = fv
            interest = 0.0
        else:
            # Future Value of an Ordinary Annuity
            fv = payment * (((1 + rate_decimal / compounds_per_year) ** (compounds_per_year * time) - 1) / (rate_decimal / compounds_per_year))
            total_invested = payment * compounds_per_year * time
            interest = fv - total_invested

        # Apply tax on interest and fee on the future value
        tax = interest * tax_rate_decimal
        fee = fv * fee_rate_decimal # Fee applied on the accumulated amount

        final_amount = fv - tax - fee
        final_interest = interest - tax - fee
        return final_amount, final_interest

    @staticmethod
    def calculate_principal(target_amount: float, rate: float, time: float, 
                          compounds_per_year: int) -> float:
        """
        Calculate required principal for target amount.
        Note: This function does not account for tax or fees directly as their
        application (on interest/amount) makes direct reversal non-trivial.
        The user should adjust the target_amount to be a gross amount if they
        want to account for tax/fees after the investment period.
        """
        rate_decimal = rate / 100
        if rate_decimal == 0:
            return target_amount # If rate is zero, principal equals target amount
        
        denominator = math.pow((1 + rate_decimal / compounds_per_year), compounds_per_year * time)
        principal = target_amount / denominator
        return principal

    @staticmethod
    def calculate_time(target_amount: float, principal: float, rate: float, 
                      compounds_per_year: int) -> float:
        """
        Calculate required time for target amount.
        Note: This function does not account for tax or fees directly as their
        application (on interest/amount) makes direct reversal non-trivial.
        The user should adjust the target_amount to be a gross amount if they
        want to account for tax/fees after the investment period.
        """
        rate_decimal = rate / 100
        if principal <= 0: 
            return float('inf') if target_amount > 0 else 0.0 # Cannot grow from zero or negative principal
        if target_amount <= principal: # Target must be greater than principal for growth
            return 0.0

        if rate_decimal == 0: # If rate is zero, target cannot be reached if target > principal
            return float('inf')

        log_factor = 1 + rate_decimal / compounds_per_year
        if log_factor <= 1: # Rate must be positive for growth
            return float('inf')

        # log(target_amount / principal) / (compounds_per_year * log(1 + rate_decimal / compounds_per_year))
        time = math.log(target_amount / principal) / (compounds_per_year * math.log(log_factor))
        return time

    @staticmethod
    def yearly_growth(principal: float, rate: float, time: float, compounds_per_year: int, 
                     tax_rate: float = 0, fee_rate: float = 0) -> List[Tuple[int, float]]:
        """Calculate yearly growth for visualization."""
        growth = []
        for year in range(int(time) + 1):
            amount, _ = CompoundInterestCalculator.calculate(principal, rate, float(year), compounds_per_year, tax_rate, fee_rate)
            growth.append((year, amount))
        return growth

    @staticmethod
    def yearly_growth_regular_savings(payment: float, rate: float, time: float, 
                                    compounds_per_year: int, tax_rate: float = 0, 
                                    fee_rate: float = 0) -> List[Tuple[int, float]]:
        """Calculate yearly growth for regular savings visualization."""
        growth = []
        for year in range(int(time) + 1):
            amount, _ = CompoundInterestCalculator.calculate_regular_savings(payment, rate, float(year), compounds_per_year, tax_rate, fee_rate)
            growth.append((year, amount))
        return growth

    @staticmethod
    def monte_carlo_simulation(principal: float, rate: float, time: float, compounds_per_year: int, 
                             tax_rate: float, fee_rate: float, simulations: int = 1000) -> Dict:
        """Run Monte Carlo simulation with random rate variations."""
        np.random.seed(42)  # For reproducibility
        # Assume rate variation follows a normal distribution around the given rate
        # with a standard deviation of 20% of the rate.
        # Ensure rates are non-negative.
        rates = np.maximum(0, np.random.normal(rate, rate * 0.2, simulations)) 
        results = []
        for r in rates:
            amount, _ = CompoundInterestCalculator.calculate(principal, r, time, compounds_per_year, tax_rate, fee_rate)
            results.append(amount)
        return {
            'mean': float(np.mean(results)),
            'min': float(np.min(results)),
            'max': float(np.max(results)),
            'std': float(np.std(results))
        }

    @staticmethod
    def process_batch(file_path: str, default_tax_rate: float = 0, default_fee_rate: float = 0) -> List[dict]:
        """Process batch calculations from JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            results = []
            for calc in data:
                principal = float(calc.get('principal', 0))
                payment = float(calc.get('payment', 0))
                rate = float(calc.get('rate', 0))
                time = float(calc.get('time', 0))
                compounds = int(calc.get('compounds_per_year', 1))
                
                # Use rates from batch file if specified, otherwise use defaults
                tax = float(calc.get('tax_rate', default_tax_rate))
                fee = float(calc.get('fee_rate', default_fee_rate))
                
                amount = 0.0
                interest = 0.0
                payment_frequency = calc.get('payment_frequency', None) # Store frequency if available in batch
                
                if payment > 0:
                    # If payment_frequency is not explicitly provided in JSON, infer from compounds_per_year
                    if payment_frequency not in ['weekly', 'monthly', 'quarterly', 'yearly']:
                        if compounds == 1: payment_frequency = "yearly"
                        elif compounds == 4: payment_frequency = "quarterly"
                        elif compounds == 12: payment_frequency = "monthly"
                        elif compounds == 52: payment_frequency = "weekly"
                        else: payment_frequency = "per_compound" # Custom frequency if no standard match

                    amount, interest = CompoundInterestCalculator.calculate_regular_savings(payment, rate, time, compounds, tax, fee)
                else:
                    amount, interest = CompoundInterestCalculator.calculate(principal, rate, time, compounds, tax, fee)
                
                results.append({
                    'principal': principal,
                    'payment': payment,
                    'rate': rate,
                    'time': time,
                    'compounds_per_year': compounds,
                    'tax_rate': tax,
                    'fee_rate': fee,
                    'amount': amount,
                    'interest': interest,
                    'payment_frequency': payment_frequency, # Add payment_frequency for regular savings
                    'timestamp': datetime.now().isoformat()
                })
            return results
        except FileNotFoundError:
            raise ValueError(f"Batch file not found: {file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {file_path}")
        except Exception as e:
            raise ValueError(f"Error processing batch file: {str(e)}")