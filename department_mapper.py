"""
Department Mapper Module
Maps roll numbers to departments based on MITS roll number formats:

UG First Years: 25MRAXXDDD (all departments grouped together as "First Year")
UG 2nd-4th Years: YY691AXXDD or YY695AXXDD (department wise based on XX code)
PG MBA: 25MRC*, 2X691E*
PG MCA: 25MRD*, 2X691F*
"""
from config import (
    UG_DEPARTMENT_CODES, DEPARTMENT_FULL_NAMES,
    FIRST_YEAR_PREFIX, PG_MBA_PREFIXES, PG_MCA_PREFIXES
)
from collections import defaultdict
import re


class DepartmentMapper:
    """Maps roll numbers to departments based on MITS roll number patterns"""
    
    def __init__(self):
        self.ug_dept_codes = UG_DEPARTMENT_CODES
        self.dept_full_names = DEPARTMENT_FULL_NAMES
        self.first_year_prefix = FIRST_YEAR_PREFIX
        self.pg_mba_prefixes = PG_MBA_PREFIXES
        self.pg_mca_prefixes = PG_MCA_PREFIXES
    
    def get_student_type(self, roll_number: str) -> str:
        """
        Determine student type from roll number
        Returns: 'UG_FIRST_YEAR', 'UG_SENIOR', 'PG_MBA', 'PG_MCA', or 'UNKNOWN'
        """
        roll = roll_number.strip().upper()
        
        # Check UG First Year: 25MRAXXDDD pattern
        if self.first_year_prefix in roll:
            return 'UG_FIRST_YEAR'
        
        # Check PG MBA: 25MRC* or XX691E*
        for prefix in self.pg_mba_prefixes:
            if prefix in roll:
                return 'PG_MBA'
        
        # Check PG MCA: 25MRD* or XX691F*
        for prefix in self.pg_mca_prefixes:
            if prefix in roll:
                return 'PG_MCA'
        
        # Check UG Senior: YY691AXXDD or YY695AXXDD pattern
        if '691A' in roll or '695A' in roll:
            return 'UG_SENIOR'
        
        return 'UNKNOWN'
    
    def get_department(self, roll_number: str) -> tuple:
        """
        Get department for a single roll number
        
        Args:
            roll_number: The student's roll number
            
        Returns:
            Tuple of (department_name, student_type)
        """
        roll = roll_number.strip().upper()
        student_type = self.get_student_type(roll)
        
        if student_type == 'UG_FIRST_YEAR':
            # All first years grouped together
            return ("First Year", student_type)
        
        elif student_type == 'PG_MBA':
            return ("MBA", student_type)
        
        elif student_type == 'PG_MCA':
            return ("MCA", student_type)
        
        elif student_type == 'UG_SENIOR':
            # Extract department code from YY691AXXDD or YY695AXXDD
            # Position of XX is after 691A/695A (index 6-7 in pattern like 22691A0501)
            match = re.search(r'69[15]A(\d{2})', roll)
            if match:
                dept_code = match.group(1)
                if dept_code in self.ug_dept_codes:
                    dept_name = self.ug_dept_codes[dept_code]
                    return (dept_name, student_type)
            return ("Unknown Dept", student_type)
        
        return ("Unknown", student_type)
    
    def is_first_year(self, roll_number: str) -> bool:
        """Check if roll number belongs to first year"""
        return self.get_student_type(roll_number) == 'UG_FIRST_YEAR'
    
    def organize_unified(self, roll_numbers: list) -> dict:
        """
        Organize all roll numbers by department
        First years are grouped together, seniors by department
        All lists are sorted
        
        Args:
            roll_numbers: List of all roll numbers
            
        Returns:
            Dictionary with departments as keys and sorted roll lists as values
        """
        organized = defaultdict(list)
        
        for roll in roll_numbers:
            if roll.strip():
                dept, _ = self.get_department(roll)
                organized[dept].append(roll.strip().upper())
        
        # Sort roll numbers within each department
        for dept in organized:
            organized[dept].sort()
        
        return dict(organized)
    
    def get_unified_summary(self, roll_numbers: list) -> dict:
        """
        Get summary for unified roll numbers input
        Organizes by department with sorted rolls
        
        Args:
            roll_numbers: List of all roll numbers
            
        Returns:
            Summary dictionary with departments and counts
        """
        organized = self.organize_unified(roll_numbers)
        
        # Count by type
        ug_first_year_count = 0
        ug_senior_count = 0
        pg_count = 0
        
        for dept, rolls in organized.items():
            for roll in rolls:
                student_type = self.get_student_type(roll)
                if student_type == 'UG_FIRST_YEAR':
                    ug_first_year_count += 1
                elif student_type == 'UG_SENIOR':
                    ug_senior_count += 1
                elif student_type in ('PG_MBA', 'PG_MCA'):
                    pg_count += 1
        
        # Build departments info with custom sort order
        # Order: UG First Year, UG Departments (sorted), PG
        departments = {}
        
        # Custom sort: First Year first, then depts alphabetically, then MBA/MCA at end
        def sort_key(dept_name):
            if dept_name == 'First Year':
                return (0, dept_name)
            elif dept_name in ('MBA', 'MCA'):
                return (2, dept_name)
            else:
                return (1, dept_name)
        
        sorted_depts = sorted(organized.keys(), key=sort_key)
        
        for dept in sorted_depts:
            rolls = organized[dept]
            departments[dept] = {
                "count": len(rolls),
                "roll_numbers": rolls  # Already sorted
            }
        
        return {
            "total_students": len([r for r in roll_numbers if r.strip()]),
            "first_year_count": ug_first_year_count,
            "senior_count": ug_senior_count + pg_count,
            "ug_first_year_count": ug_first_year_count,
            "ug_senior_count": ug_senior_count,
            "pg_count": pg_count,
            "departments": departments,
            "organized": organized
        }


def parse_roll_numbers(input_text: str) -> list:
    """
    Parse roll numbers from various input formats
    Supports comma-separated, newline-separated, or space-separated
    """
    if not input_text:
        return []
    
    # Replace common separators with comma
    normalized = input_text.replace('\n', ',').replace(';', ',').replace('\t', ',')
    
    # Split and clean
    roll_numbers = []
    for item in normalized.split(','):
        parts = item.strip().split()
        for part in parts:
            cleaned = part.strip()
            if cleaned:
                roll_numbers.append(cleaned.upper())
    
    return roll_numbers


if __name__ == "__main__":
    # Test the mapper with MITS roll number formats
    mapper = DepartmentMapper()
    
    test_rolls = [
        # UG First Years
        "25MRA05001", "25MRA05002", "25MRA04001",
        # UG Seniors - CSE
        "22691A0501", "22691A0502", "23691A0503",
        # UG Seniors - ECE
        "22691A0401", "23691A0402",
        # UG Seniors - ME
        "24691A0301",
        # UG Seniors - CSE AI
        "23691A3101",
        # UG Seniors (Diploma) - CSE
        "24695A0501", "24695A0502",
        # PG MBA
        "25MRC001", "24691E01",
        # PG MCA
        "25MRD001", "24691F01",
    ]
    
    print("Testing MITS Department Mapper")
    print("=" * 60)
    
    for roll in test_rolls:
        dept, stype = mapper.get_department(roll)
        print(f"  {roll:15} -> {dept:25} ({stype})")
    
    print("\n" + "=" * 60)
    print("Organized Summary:")
    print("=" * 60)
    
    summary = mapper.get_unified_summary(test_rolls)
    print(f"\nTotal Students: {summary['total_students']}")
    print(f"UG First Year: {summary['ug_first_year_count']}")
    print(f"UG Seniors: {summary['ug_senior_count']}")
    print(f"PG Students: {summary['pg_count']}")
    
    print("\nBy Department:")
    for dept, info in summary['departments'].items():
        print(f"\n{dept} ({info['count']}):")
        print(f"  {', '.join(info['roll_numbers'])}")
