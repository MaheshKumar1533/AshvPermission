# Configuration for Department Mapping and Letter Generation

# =============================================================================
# ROLL NUMBER FORMATS:
# =============================================================================
# UG First Years: 25MRAXXDDD (e.g., 25MRA05001) - All departments together
# UG 2nd-4th Years: YY691AXXDD (e.g., 22691A0501) - Department wise
# UG 2nd-4th Years (Diploma joined): YY695AXXDD (e.g., 22695A0501) - Department wise
# PG MBA: 25MRC*, 2X691E* (e.g., 25MRC001, 24691E01)
# PG MCA: 25MRD*, 2X691F* (e.g., 25MRD001, 24691F01)
# =============================================================================

# Department codes for UG 2nd-4th years (XX in YY691AXXDD or YY695AXXDD)
UG_DEPARTMENT_CODES = {
    "01": "CE",      # Civil Engineering
    "02": "EEE",     # Electrical & Electronics Engineering
    "03": "ME",      # Mechanical Engineering
    "04": "ECE",     # Electronics & Communication Engineering
    "05": "CSE",     # Computer Science & Engineering
    "31": "CAI",     # CSE (AI)
    "32": "CSD",     # CSE (Data Science)
    "37": "CSC",     # CSE (Cyber Security)
    "40": "CSN",     # CSE (Networks)
    "33": "CSM",     # CSE (AI & ML)
    "28": "CST",     # CSE (IoT)
}

# Full department names
DEPARTMENT_FULL_NAMES = {
    "CE": "Civil Engineering",
    "EEE": "Electrical & Electronics Engineering",
    "ME": "Mechanical Engineering",
    "ECE": "Electronics & Communication Engineering",
    "CSE": "Computer Science & Engineering",
    "CAI": "CSE (Artificial Intelligence)",
    "CSD": "CSE (Data Science)",
    "CSC": "CSE (Cyber Security)",
    "CSN": "CSE (Networks)",
    "CSM": "CSE (AI & ML)",
    "CST": "CSE (IoT)",
    "MBA": "Master of Business Administration",
    "MCA": "Master of Computer Applications",
}

# Default letter content
DEFAULT_SUBJECT = "Request for Permission to Perform Ashv-2k26 Activities"

DEFAULT_BODY = """Greetings from the ASHV Organizing Committee.
We kindly request your permission to grant attendance for today to the students who are part of the ASHV 2K26 Organizing Team, as they are engaged in official ASHV-related activities for ASHV. Their presence and contribution today are essential for the smooth coordination of ASHV activities.
We assure you that the students are involved only in official ASHV activities and will maintain discipline and decorum.
We request you to kindly consider and grant attendance for the same.
Thanking you."""

# Header configuration
HEADER_CONFIG = {
    "institution_name": "Your Institution Name",
    "institution_address": "Institution Address Line 1",
    "institution_city": "City, State - PIN Code",
    "institution_contact": "Phone: +91-XXXXXXXXXX | Email: info@institution.edu",
}

# Default place
DEFAULT_PLACE = "Madanapalle"

# Database configuration
SQLALCHEMY_DATABASE_URI = "sqlite:///permissions.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# First year pattern identifier
FIRST_YEAR_PREFIX = "MRA"  # 25MRAXXDDD pattern

# PG patterns
PG_MBA_PREFIXES = ["MRC", "691E"]  # 25MRC* or 2X691E*
PG_MCA_PREFIXES = ["MRD", "691F"]  # 25MRD* or 2X691F*
