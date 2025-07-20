"""
Example calculator module for demonstrating the testing framework
"""

import math
from typing import Union, List, Optional
from dataclasses import dataclass


@dataclass
class CalculationResult:
    """Result of a calculation with metadata"""
    value: float
    operation: str
    inputs: List[Union[int, float]]
    timestamp: Optional[str] = None


class Calculator:
    """A simple calculator class with various mathematical operations"""
    
    def __init__(self, precision: int = 2):
        """
        Initialize calculator with specified precision
        
        Args:
            precision: Number of decimal places for results
        """
        self.precision = precision
        self.history: List[CalculationResult] = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Add two numbers"""
        result = float(a + b)
        self._record_calculation("add", [a, b], result)
        return round(result, self.precision)
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Subtract b from a"""
        result = float(a - b)
        self._record_calculation("subtract", [a, b], result)
        return round(result, self.precision)
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Multiply two numbers"""
        result = float(a * b)
        self._record_calculation("multiply", [a, b], result)
        return round(result, self.precision)
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = float(a / b)
        self._record_calculation("divide", [a, b], result)
        return round(result, self.precision)
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """Raise base to the power of exponent"""
        result = float(base ** exponent)
        self._record_calculation("power", [base, exponent], result)
        return round(result, self.precision)
    
    def square_root(self, value: Union[int, float]) -> float:
        """Calculate square root of value"""
        if value < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = float(math.sqrt(value))
        self._record_calculation("square_root", [value], result)
        return round(result, self.precision)
    
    def factorial(self, n: int) -> int:
        """Calculate factorial of n"""
        if n < 0:
            raise ValueError("Cannot calculate factorial of negative number")
        if n == 0 or n == 1:
            return 1
        
        result = 1
        for i in range(2, n + 1):
            result *= i
        
        self._record_calculation("factorial", [n], float(result))
        return result
    
    def average(self, numbers: List[Union[int, float]]) -> float:
        """Calculate average of a list of numbers"""
        if not numbers:
            raise ValueError("Cannot calculate average of empty list")
        
        result = float(sum(numbers) / len(numbers))
        self._record_calculation("average", numbers, result)
        return round(result, self.precision)
    
    def _record_calculation(self, operation: str, inputs: List[Union[int, float]], result: float):
        """Record a calculation in history"""
        from datetime import datetime
        calc_result = CalculationResult(
            value=result,
            operation=operation,
            inputs=inputs,
            timestamp=datetime.now().isoformat()
        )
        self.history.append(calc_result)
    
    def get_history(self) -> List[CalculationResult]:
        """Get calculation history"""
        return self.history.copy()
    
    def clear_history(self):
        """Clear calculation history"""
        self.history.clear()
    
    def get_statistics(self) -> dict:
        """Get statistics about calculations performed"""
        if not self.history:
            return {
                "total_calculations": 0,
                "operations_used": {},
                "most_used_operation": None
            }
        
        operations = {}
        for calc in self.history:
            operations[calc.operation] = operations.get(calc.operation, 0) + 1
        
        most_used = max(operations.items(), key=lambda x: x[1])[0] if operations else None
        
        return {
            "total_calculations": len(self.history),
            "operations_used": operations,
            "most_used_operation": most_used
        }


class AdvancedCalculator(Calculator):
    """Advanced calculator with additional mathematical functions"""
    
    def __init__(self, precision: int = 4):
        super().__init__(precision)
        self.constants = {
            "pi": math.pi,
            "e": math.e,
            "phi": (1 + math.sqrt(5)) / 2  # Golden ratio
        }
    
    def sin(self, angle: Union[int, float]) -> float:
        """Calculate sine of angle (in radians)"""
        result = float(math.sin(angle))
        self._record_calculation("sin", [angle], result)
        return round(result, self.precision)
    
    def cos(self, angle: Union[int, float]) -> float:
        """Calculate cosine of angle (in radians)"""
        result = float(math.cos(angle))
        self._record_calculation("cos", [angle], result)
        return round(result, self.precision)
    
    def tan(self, angle: Union[int, float]) -> float:
        """Calculate tangent of angle (in radians)"""
        result = float(math.tan(angle))
        self._record_calculation("tan", [angle], result)
        return round(result, self.precision)
    
    def log(self, value: Union[int, float], base: Union[int, float] = 10) -> float:
        """Calculate logarithm of value with given base"""
        if value <= 0:
            raise ValueError("Cannot calculate logarithm of non-positive number")
        if base <= 0 or base == 1:
            raise ValueError("Invalid base for logarithm")
        
        result = float(math.log(value, base))
        self._record_calculation("log", [value, base], result)
        return round(result, self.precision)
    
    def ln(self, value: Union[int, float]) -> float:
        """Calculate natural logarithm of value"""
        return self.log(value, math.e)
    
    def get_constant(self, name: str) -> float:
        """Get mathematical constant by name"""
        if name not in self.constants:
            raise ValueError(f"Unknown constant: {name}")
        return self.constants[name]


def validate_number(value: Union[int, float]) -> bool:
    """Validate if a value is a valid number"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def format_number(value: Union[int, float], precision: int = 2) -> str:
    """Format a number with specified precision"""
    return f"{value:.{precision}f}"


def calculate_compound_interest(principal: float, rate: float, time: float, 
                               compounds_per_year: int = 1) -> float:
    """Calculate compound interest"""
    if principal <= 0 or rate < 0 or time < 0 or compounds_per_year <= 0:
        raise ValueError("Invalid parameters for compound interest calculation")
    
    rate_decimal = rate / 100
    amount = principal * (1 + rate_decimal / compounds_per_year) ** (compounds_per_year * time)
    return round(amount, 2) 