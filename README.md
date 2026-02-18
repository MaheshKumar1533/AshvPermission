# AshvPermission - Permission Letter Generator

A Flask web application to generate permission letters with roll numbers automatically mapped to departments. Supports **two types of roll numbers**: First Years and Seniors.

## Features

- ✅ **Dual Roll Number Support**: Separate inputs for First Year and Senior students
- ✅ **Automatic Department Mapping**: Roll numbers organized by department based on prefixes
- ✅ **A4 Letter Format**: Professional letter format with customizable header
- ✅ **Live Preview**: See department mapping before generating
- ✅ **Print/PDF Export**: Print directly or save as PDF from browser
- ✅ **HTML Download**: Download standalone HTML file
- ✅ **Customizable Settings**: Change institution details and defaults

## Installation

1. **Install Python 3.7+**

2. **Install Flask**:

```bash
pip install flask
```

3. **Run the application**:

```bash
python app.py
```

4. **Open in browser**: http://127.0.0.1:5000

## Usage

1. **Enter Roll Numbers**:
   - First Year rolls in the green box (e.g., 25CS101, 26EC201)
   - Senior rolls in the blue box (e.g., 22CS101, 23EC201)

2. **Fill Letter Details** (optional):
   - Subject, Body, Date, Place
   - Leave blank to use defaults

3. **Preview**: Click "Preview Department Mapping" to see organization

4. **Generate**: Click "Generate Letter" to create the letter

5. **Export**:
   - Use browser's Print (Ctrl+P) → Save as PDF
   - Or download as HTML file

## Roll Number Format

### First Year (Batches: 25, 26)

| Roll Number | Department                    |
| ----------- | ----------------------------- |
| 25CS101     | Computer Science - First Year |
| 26EC201     | Electronics - First Year      |
| 25ME301     | Mechanical - First Year       |

### Seniors (Batches: 21, 22, 23, 24)

| Roll Number | Department                    |
| ----------- | ----------------------------- |
| 22CS101     | Computer Science - 2022 Batch |
| 23EC201     | Electronics - 2023 Batch      |
| 24ME301     | Mechanical - 2024 Batch       |

## Department Codes

- **CS** - Computer Science
- **EC** - Electronics and Communication
- **EE** - Electrical Engineering
- **ME** - Mechanical Engineering
- **CE** - Civil Engineering
- **IT** - Information Technology
- **AI** - Artificial Intelligence
- **DS** - Data Science
- **CH** - Chemical Engineering
- **BT** - Biotechnology

## Project Structure

```
AshvPermission/
├── app.py                  # Flask application
├── config.py               # Configuration (mappings, defaults)
├── department_mapper.py    # Roll number mapping logic
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Home page (form)
│   ├── letter.html        # Letter preview
│   ├── letter_download.html # Downloadable letter
│   └── settings.html      # Settings page
└── static/                # Static files (if needed)
```

## Configuration

Edit `config.py` to customize:

- **FIRST_YEAR_BATCHES**: Which batch years are first years (default: 25, 26)
- **FIRST_YEAR_PATTERNS**: Department mapping for first years
- **SENIOR_PATTERNS**: Department mapping for seniors
- **HEADER_CONFIG**: Institution name, address, contact
- **DEFAULT_SUBJECT**: Default letter subject
- **DEFAULT_BODY**: Default letter body

## Screenshots

### Home Page

- Dual input for First Year and Senior roll numbers
- Live department mapping preview
- Customizable subject and body

### Generated Letter

- Professional A4 format
- Institution header
- Students organized by category and department
- Print-ready design

## License

MIT License
