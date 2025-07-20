"""
Basic tests for the calculator module
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from example_calculator import Calculator, validate_number, format_number


class TestCalculator:
    """Test cases for the Calculator class"""
    
    def test_calculator_initialization(self):
        """Test calculator initialization with default precision"""
        calc = Calculator()
        assert calc.precision == 2
        assert len(calc.history) == 0
    
    def test_calculator_custom_precision(self):
        """Test calculator initialization with custom precision"""
        calc = Calculator(precision=4)
        assert calc.precision == 4
    
    def test_add_operation(self):
        """Test addition operation"""
        calc = Calculator()
        result = calc.add(5, 3)
        assert result == 8.0
        assert len(calc.history) == 1
        assert calc.history[0].operation == "add"
    
    def test_subtract_operation(self):
        """Test subtraction operation"""
        calc = Calculator()
        result = calc.subtract(10, 4)
        assert result == 6.0
    
    def test_multiply_operation(self):
        """Test multiplication operation"""
        calc = Calculator()
        result = calc.multiply(6, 7)
        assert result == 42.0
    
    def test_divide_operation(self):
        """Test division operation"""
        calc = Calculator()
        result = calc.divide(15, 3)
        assert result == 5.0
    
    def test_divide_by_zero(self):
        """Test division by zero raises error"""
        calc = Calculator()
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(10, 0)
    
    def test_power_operation(self):
        """Test power operation"""
        calc = Calculator()
        result = calc.power(2, 3)
        assert result == 8.0
    
    def test_square_root_operation(self):
        """Test square root operation"""
        calc = Calculator()
        result = calc.square_root(16)
        assert result == 4.0
    
    def test_square_root_negative(self):
        """Test square root of negative number raises error"""
        calc = Calculator()
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            calc.square_root(-1)
    
    def test_factorial_operation(self):
        """Test factorial operation"""
        calc = Calculator()
        result = calc.factorial(5)
        assert result == 120
    
    def test_factorial_zero(self):
        """Test factorial of zero"""
        calc = Calculator()
        result = calc.factorial(0)
        assert result == 1
    
    def test_factorial_negative(self):
        """Test factorial of negative number raises error"""
        calc = Calculator()
        with pytest.raises(ValueError, match="Cannot calculate factorial of negative number"):
            calc.factorial(-1)
    
    def test_average_operation(self):
        """Test average operation"""
        calc = Calculator()
        result = calc.average([1, 2, 3, 4, 5])
        assert result == 3.0
    
    def test_average_empty_list(self):
        """Test average of empty list raises error"""
        calc = Calculator()
        with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
            calc.average([])
    
    def test_history_recording(self):
        """Test that calculations are recorded in history"""
        calc = Calculator()
        calc.add(1, 2)
        calc.multiply(3, 4)
        
        assert len(calc.history) == 2
        assert calc.history[0].operation == "add"
        assert calc.history[1].operation == "multiply"
    
    def test_clear_history(self):
        """Test clearing calculation history"""
        calc = Calculator()
        calc.add(1, 2)
        calc.clear_history()
        assert len(calc.history) == 0
    
    def test_get_statistics(self):
        """Test getting calculation statistics"""
        calc = Calculator()
        calc.add(1, 2)
        calc.add(3, 4)
        calc.multiply(2, 3)
        
        stats = calc.get_statistics()
        assert stats["total_calculations"] == 3
        assert stats["operations_used"]["add"] == 2
        assert stats["operations_used"]["multiply"] == 1
        assert stats["most_used_operation"] == "add"


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_validate_number_valid(self):
        """Test validate_number with valid numbers"""
        assert validate_number(42) == True
        assert validate_number(3.14) == True
        assert validate_number(0) == True
    
    def test_validate_number_invalid(self):
        """Test validate_number with invalid values"""
        assert validate_number("not a number") == False  # type: ignore
        assert validate_number(None) == False  # type: ignore
    
    def test_format_number(self):
        """Test format_number function"""
        assert format_number(3.14159, 2) == "3.14"
        assert format_number(42, 0) == "42.0"
        assert format_number(0.123456, 4) == "0.1235" 