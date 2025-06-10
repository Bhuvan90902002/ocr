# Invoice OCR Processing Script

This script uses Google's Gemini AI to process invoice images and extract structured data in JSON format.

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

## Usage

1. Run the script:
```bash
python local.py
```

2. When prompted:
   - Enter the path to your invoice image
   - Choose whether to save the output to a file
   - If yes, specify the output filename

## Input Image Requirements

Supported image formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)

## Output Format

The script outputs a JSON structure containing:
- Invoice header information
- Customer details
- Line items
- Tax and total calculations 