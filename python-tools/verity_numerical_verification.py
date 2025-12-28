"""
Verity Numerical Claim Verification Engine
==========================================
Specialized engine for verifying numerical claims and statistics.

Features:
- Number extraction and parsing
- Statistical claim validation
- Unit conversion
- Order of magnitude checking
- Percentage and ratio verification
- Trend and comparison validation
"""

import re
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union
from enum import Enum


class NumberType(Enum):
    """Types of numerical values"""
    INTEGER = "integer"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    FRACTION = "fraction"
    RATIO = "ratio"
    CURRENCY = "currency"
    RANGE = "range"
    APPROXIMATE = "approximate"


class MagnitudeWord(Enum):
    """Words representing magnitudes"""
    THOUSAND = 1_000
    MILLION = 1_000_000
    BILLION = 1_000_000_000
    TRILLION = 1_000_000_000_000
    QUADRILLION = 1_000_000_000_000_000


@dataclass
class ExtractedNumber:
    """A number extracted from text"""
    value: float
    original_text: str
    number_type: NumberType
    unit: Optional[str] = None
    confidence: float = 0.9
    is_approximate: bool = False
    range_min: Optional[float] = None
    range_max: Optional[float] = None


@dataclass
class NumericalClaim:
    """A parsed numerical claim"""
    subject: str
    value: ExtractedNumber
    comparison_type: Optional[str] = None  # "equals", "greater", "less", "between"
    comparison_value: Optional[ExtractedNumber] = None
    context: str = ""


class NumberExtractor:
    """
    Extract and parse numbers from text.
    """
    
    # Currency symbols and codes
    CURRENCIES = {
        '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
        'usd': 'USD', 'eur': 'EUR', 'gbp': 'GBP', 'jpy': 'JPY',
        'cad': 'CAD', 'aud': 'AUD', 'chf': 'CHF', 'cny': 'CNY'
    }
    
    # Magnitude words
    MAGNITUDE_PATTERNS = {
        r'\bthousand\b': 1_000,
        r'\bmillion\b': 1_000_000,
        r'\bbillion\b': 1_000_000_000,
        r'\btrillion\b': 1_000_000_000_000,
        r'\bk\b': 1_000,
        r'\bm\b': 1_000_000,
        r'\bb\b': 1_000_000_000,
    }
    
    # Common units
    UNITS = {
        'length': ['km', 'kilometers', 'miles', 'mi', 'meters', 'm', 'feet', 'ft', 'inches', 'in'],
        'weight': ['kg', 'kilograms', 'pounds', 'lbs', 'tons', 'tonnes', 'grams', 'g', 'ounces', 'oz'],
        'temperature': ['celsius', '°c', 'fahrenheit', '°f', 'kelvin', 'k'],
        'time': ['seconds', 'sec', 'minutes', 'min', 'hours', 'hr', 'days', 'weeks', 'months', 'years'],
        'volume': ['liters', 'l', 'gallons', 'gal', 'ml', 'milliliters'],
        'area': ['sq km', 'square kilometers', 'sq mi', 'square miles', 'acres', 'hectares'],
    }
    
    @classmethod
    def extract_all(cls, text: str) -> List[ExtractedNumber]:
        """Extract all numbers from text"""
        numbers = []
        
        # Extract percentages
        numbers.extend(cls._extract_percentages(text))
        
        # Extract currency values
        numbers.extend(cls._extract_currency(text))
        
        # Extract ranges
        numbers.extend(cls._extract_ranges(text))
        
        # Extract regular numbers with magnitudes
        numbers.extend(cls._extract_standard_numbers(text))
        
        return numbers
    
    @classmethod
    def _extract_percentages(cls, text: str) -> List[ExtractedNumber]:
        """Extract percentage values"""
        numbers = []
        
        # Pattern: "50%" or "50 percent"
        pattern = r'(\d+(?:\.\d+)?)\s*(?:%|percent)'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value = float(match.group(1))
            numbers.append(ExtractedNumber(
                value=value / 100,  # Normalize to decimal
                original_text=match.group(0),
                number_type=NumberType.PERCENTAGE,
                unit='percent'
            ))
        
        return numbers
    
    @classmethod
    def _extract_currency(cls, text: str) -> List[ExtractedNumber]:
        """Extract currency values"""
        numbers = []
        
        # Pattern: "$1,234.56" or "1,234.56 USD"
        pattern = r'([\$€£¥])?\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(thousand|million|billion|trillion)?\s*([A-Z]{3})?'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            symbol = match.group(1)
            value_str = match.group(2).replace(',', '')
            magnitude = match.group(3)
            currency_code = match.group(4)
            
            if not value_str:
                continue
            
            value = float(value_str)
            
            # Apply magnitude
            if magnitude:
                for mag_pattern, multiplier in cls.MAGNITUDE_PATTERNS.items():
                    if re.search(mag_pattern, magnitude, re.IGNORECASE):
                        value *= multiplier
                        break
            
            # Determine currency
            currency = None
            if symbol:
                currency = cls.CURRENCIES.get(symbol, 'USD')
            elif currency_code:
                currency = currency_code.upper()
            
            if currency or symbol:
                numbers.append(ExtractedNumber(
                    value=value,
                    original_text=match.group(0),
                    number_type=NumberType.CURRENCY,
                    unit=currency
                ))
        
        return numbers
    
    @classmethod
    def _extract_ranges(cls, text: str) -> List[ExtractedNumber]:
        """Extract number ranges"""
        numbers = []
        
        # Pattern: "5 to 10" or "5-10" or "between 5 and 10"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)',
            r'between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                mid_val = (min_val + max_val) / 2
                
                numbers.append(ExtractedNumber(
                    value=mid_val,
                    original_text=match.group(0),
                    number_type=NumberType.RANGE,
                    range_min=min_val,
                    range_max=max_val
                ))
        
        return numbers
    
    @classmethod
    def _extract_standard_numbers(cls, text: str) -> List[ExtractedNumber]:
        """Extract standard numbers with optional magnitudes and units"""
        numbers = []
        
        # Pattern: number + optional magnitude + optional unit
        pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(thousand|million|billion|trillion|k|m|b)?\s*([a-zA-Z]+)?'
        
        for match in re.finditer(pattern, text, re.IGNORECASE):
            value_str = match.group(1).replace(',', '')
            magnitude = match.group(2)
            unit = match.group(3)
            
            if not value_str:
                continue
            
            value = float(value_str)
            is_approx = False
            
            # Apply magnitude
            if magnitude:
                for mag_pattern, multiplier in cls.MAGNITUDE_PATTERNS.items():
                    if re.search(mag_pattern, magnitude, re.IGNORECASE):
                        value *= multiplier
                        break
            
            # Check for "approximately" or "about" nearby
            context_start = max(0, match.start() - 20)
            context = text[context_start:match.start()].lower()
            if any(word in context for word in ['about', 'approximately', 'around', 'roughly', 'nearly', 'almost']):
                is_approx = True
            
            # Identify unit type
            unit_type = None
            if unit:
                unit_lower = unit.lower()
                for category, units in cls.UNITS.items():
                    if unit_lower in [u.lower() for u in units]:
                        unit_type = unit_lower
                        break
            
            numbers.append(ExtractedNumber(
                value=value,
                original_text=match.group(0),
                number_type=NumberType.APPROXIMATE if is_approx else NumberType.DECIMAL if '.' in value_str else NumberType.INTEGER,
                unit=unit_type,
                is_approximate=is_approx
            ))
        
        return numbers


class UnitConverter:
    """
    Convert between common units.
    """
    
    # Conversion factors to base units
    LENGTH_TO_METERS = {
        'km': 1000, 'kilometers': 1000,
        'm': 1, 'meters': 1,
        'cm': 0.01, 'centimeters': 0.01,
        'mm': 0.001, 'millimeters': 0.001,
        'mi': 1609.34, 'miles': 1609.34,
        'ft': 0.3048, 'feet': 0.3048,
        'in': 0.0254, 'inches': 0.0254,
        'yd': 0.9144, 'yards': 0.9144,
    }
    
    WEIGHT_TO_KG = {
        'kg': 1, 'kilograms': 1,
        'g': 0.001, 'grams': 0.001,
        'mg': 0.000001, 'milligrams': 0.000001,
        'lb': 0.453592, 'lbs': 0.453592, 'pounds': 0.453592,
        'oz': 0.0283495, 'ounces': 0.0283495,
        'ton': 907.185, 'tons': 907.185,  # US ton
        'tonne': 1000, 'tonnes': 1000,  # Metric ton
    }
    
    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert between units"""
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Check length
        if from_unit in cls.LENGTH_TO_METERS and to_unit in cls.LENGTH_TO_METERS:
            meters = value * cls.LENGTH_TO_METERS[from_unit]
            return meters / cls.LENGTH_TO_METERS[to_unit]
        
        # Check weight
        if from_unit in cls.WEIGHT_TO_KG and to_unit in cls.WEIGHT_TO_KG:
            kg = value * cls.WEIGHT_TO_KG[from_unit]
            return kg / cls.WEIGHT_TO_KG[to_unit]
        
        # Temperature
        if from_unit in ['c', 'celsius', '°c'] and to_unit in ['f', 'fahrenheit', '°f']:
            return value * 9/5 + 32
        if from_unit in ['f', 'fahrenheit', '°f'] and to_unit in ['c', 'celsius', '°c']:
            return (value - 32) * 5/9
        
        return None


class OrderOfMagnitudeChecker:
    """
    Check if numbers are within reasonable order of magnitude.
    """
    
    # Expected ranges for common statistics
    EXPECTED_RANGES = {
        'world_population': (7_000_000_000, 9_000_000_000),
        'us_population': (300_000_000, 400_000_000),
        'china_population': (1_300_000_000, 1_500_000_000),
        'human_life_expectancy_years': (50, 100),
        'earth_circumference_km': (39_000, 41_000),
        'speed_of_light_mps': (299_000_000, 300_000_000),
        'earth_sun_distance_km': (147_000_000, 153_000_000),
        'human_height_cm': (100, 250),
        'human_weight_kg': (20, 200),
    }
    
    @classmethod
    def check_magnitude(cls, value: float, context: str) -> Dict:
        """Check if value is within expected magnitude for context"""
        result = {
            "value": value,
            "context": context,
            "is_plausible": True,
            "expected_range": None,
            "order_of_magnitude": int(math.log10(abs(value))) if value != 0 else 0,
            "explanation": ""
        }
        
        # Check against known ranges
        for key, (min_val, max_val) in cls.EXPECTED_RANGES.items():
            if key.replace('_', ' ') in context.lower():
                result["expected_range"] = (min_val, max_val)
                
                if min_val <= value <= max_val:
                    result["is_plausible"] = True
                    result["explanation"] = f"Value is within expected range ({min_val:,} - {max_val:,})"
                elif value < min_val / 10 or value > max_val * 10:
                    result["is_plausible"] = False
                    result["explanation"] = f"Value is far outside expected range ({min_val:,} - {max_val:,})"
                else:
                    result["is_plausible"] = True
                    result["explanation"] = f"Value is slightly outside expected range ({min_val:,} - {max_val:,})"
                
                break
        
        return result


class NumericalClaimVerifier:
    """
    Main engine for verifying numerical claims.
    """
    
    def __init__(self):
        self.extractor = NumberExtractor()
        self.converter = UnitConverter()
        self.magnitude_checker = OrderOfMagnitudeChecker()
    
    def parse_claim(self, claim: str) -> Optional[NumericalClaim]:
        """Parse a numerical claim into structured form"""
        numbers = self.extractor.extract_all(claim)
        
        if not numbers:
            return None
        
        # Find comparison type
        comparison = self._detect_comparison(claim)
        
        # Use first number as primary value
        primary = numbers[0]
        secondary = numbers[1] if len(numbers) > 1 else None
        
        # Extract subject (what the number refers to)
        subject = self._extract_subject(claim, primary.original_text)
        
        return NumericalClaim(
            subject=subject,
            value=primary,
            comparison_type=comparison,
            comparison_value=secondary,
            context=claim
        )
    
    def _detect_comparison(self, claim: str) -> Optional[str]:
        """Detect type of comparison in claim"""
        claim_lower = claim.lower()
        
        if any(word in claim_lower for word in ['more than', 'greater than', 'over', 'exceeds', 'above']):
            return 'greater'
        if any(word in claim_lower for word in ['less than', 'fewer than', 'under', 'below']):
            return 'less'
        if any(word in claim_lower for word in ['between', 'from', 'range']):
            return 'between'
        if any(word in claim_lower for word in ['exactly', 'precisely', 'is', 'equals', 'was']):
            return 'equals'
        
        return 'equals'  # Default
    
    def _extract_subject(self, claim: str, number_text: str) -> str:
        """Extract what the number refers to"""
        # Remove the number from the claim
        remaining = claim.replace(number_text, '[NUMBER]')
        
        # Try to extract noun phrase before or after [NUMBER]
        # This is simplified - real implementation would use NLP
        parts = remaining.split('[NUMBER]')
        
        if len(parts) >= 2:
            before = parts[0].strip().split()[-5:] if parts[0] else []
            after = parts[1].strip().split()[:5] if len(parts) > 1 else []
            
            subject_words = before + after
            return ' '.join(subject_words).strip()
        
        return remaining.strip()
    
    def verify_numerical_claim(
        self,
        claim: str,
        reference_value: Optional[float] = None,
        reference_unit: Optional[str] = None,
        tolerance: float = 0.1
    ) -> Dict:
        """
        Verify a numerical claim against a reference value.
        
        tolerance: Acceptable error margin (0.1 = 10%)
        """
        parsed = self.parse_claim(claim)
        
        if not parsed:
            return {
                "claim": claim,
                "has_numerical_content": False,
                "explanation": "No numerical claims detected"
            }
        
        result = {
            "claim": claim,
            "has_numerical_content": True,
            "extracted_value": parsed.value.value,
            "extracted_unit": parsed.value.unit,
            "subject": parsed.subject,
            "comparison_type": parsed.comparison_type,
            "is_valid": None,
            "explanation": ""
        }
        
        # If reference value provided, compare
        if reference_value is not None:
            claimed = parsed.value.value
            
            # Convert units if needed
            if parsed.value.unit and reference_unit:
                converted = self.converter.convert(claimed, parsed.value.unit, reference_unit)
                if converted is not None:
                    claimed = converted
                    result["converted_value"] = claimed
                    result["converted_unit"] = reference_unit
            
            # Check based on comparison type
            error = abs(claimed - reference_value) / reference_value if reference_value != 0 else 0
            result["error_margin"] = round(error * 100, 2)
            
            if parsed.comparison_type == 'equals':
                result["is_valid"] = error <= tolerance
            elif parsed.comparison_type == 'greater':
                result["is_valid"] = claimed > reference_value
            elif parsed.comparison_type == 'less':
                result["is_valid"] = claimed < reference_value
            elif parsed.comparison_type == 'between':
                if parsed.value.range_min is not None and parsed.value.range_max is not None:
                    result["is_valid"] = parsed.value.range_min <= reference_value <= parsed.value.range_max
                else:
                    result["is_valid"] = error <= tolerance
            
            if result["is_valid"]:
                result["explanation"] = f"Numerical claim is accurate (within {tolerance * 100}% tolerance)"
            else:
                result["explanation"] = f"Numerical claim is off by {result['error_margin']}%. Reference value: {reference_value}"
        
        # Check order of magnitude regardless
        magnitude_check = self.magnitude_checker.check_magnitude(
            parsed.value.value,
            parsed.subject
        )
        result["magnitude_check"] = magnitude_check
        
        if not magnitude_check["is_plausible"]:
            result["is_valid"] = False
            result["explanation"] = f"Value seems implausible. {magnitude_check['explanation']}"
        
        return result
    
    def compare_numerical_claims(
        self,
        claim1: str,
        claim2: str
    ) -> Dict:
        """Compare two numerical claims for consistency"""
        parsed1 = self.parse_claim(claim1)
        parsed2 = self.parse_claim(claim2)
        
        if not parsed1 or not parsed2:
            return {
                "claim1": claim1,
                "claim2": claim2,
                "can_compare": False,
                "explanation": "Could not extract numbers from both claims"
            }
        
        value1 = parsed1.value.value
        value2 = parsed2.value.value
        
        # Convert units if possible
        if parsed1.value.unit and parsed2.value.unit:
            converted = self.converter.convert(value2, parsed2.value.unit, parsed1.value.unit)
            if converted is not None:
                value2 = converted
        
        # Calculate difference
        if value1 != 0:
            percent_diff = abs(value1 - value2) / abs(value1) * 100
        else:
            percent_diff = 100 if value2 != 0 else 0
        
        return {
            "claim1": claim1,
            "claim2": claim2,
            "can_compare": True,
            "value1": value1,
            "value2": value2,
            "percent_difference": round(percent_diff, 2),
            "are_consistent": percent_diff < 10,
            "explanation": f"Values differ by {percent_diff:.1f}%"
        }
    
    def generate_numerical_search_queries(self, claim: str) -> List[str]:
        """Generate search queries for numerical verification"""
        parsed = self.parse_claim(claim)
        queries = [claim]
        
        if parsed:
            # Add subject-focused query
            queries.append(f"{parsed.subject} statistics")
            queries.append(f"{parsed.subject} data")
            queries.append(f"official {parsed.subject} numbers")
            
            # Add verification-style queries
            queries.append(f"fact check {parsed.subject}")
            
            # Add unit-specific queries if applicable
            if parsed.value.unit:
                queries.append(f"{parsed.subject} in {parsed.value.unit}")
        
        return list(set(queries))


__all__ = [
    'NumericalClaimVerifier', 'NumberExtractor', 'UnitConverter',
    'OrderOfMagnitudeChecker', 'ExtractedNumber', 'NumericalClaim', 'NumberType'
]
