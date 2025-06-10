import os
import google.generativeai as genai
from pathlib import Path
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your Google API key as environment variable or replace with your key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

def list_available_models():
    """List models that support generateContent"""
    print("Available models:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"- {model.name}")
    print()

# Model Configuration
MODEL_CONFIG = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

# Safety Settings of Model
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    }
]

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=MODEL_CONFIG,
    safety_settings=safety_settings
)

def image_format(image_path):
    """Format image for Gemini API"""
    img = Path(image_path)
    if not img.exists():
        raise FileNotFoundError(f"Could not find image: {img}")
    
    # Determine MIME type based on file extension
    extension = img.suffix.lower()
    mime_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp'
    }
    
    mime_type = mime_type_map.get(extension, 'image/jpeg')
    
    image_parts = [
        {
            "mime_type": mime_type,
            "data": img.read_bytes()
        }
    ]
    return image_parts

def gemini_output(image_path, system_prompt, user_prompt):
    """Generate output using Gemini model"""
    try:
        image_info = image_format(image_path)
        input_prompt = [system_prompt, image_info[0], user_prompt]
        response = model.generate_content(input_prompt)
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"


def process_invoice(image_path, output_file=None):
    """Process invoice image and return parsed JSON."""

    system_prompt = """
    You are a specialist in comprehending import and export Invoices.
    Input images in the form of import and export invoices will be provided to you,
    and your task is to respond with a valid JSON object based on the content of the input image.
    """

    user_prompt = """Convert Invoice data into JSON format with this structure. Always return this exact JSON structure even if some values are missing:

    {
      "invoice_header": {
        "company_name": "",
        "address": "",
        "invoice_number": "",
        "date": "",
        "customer_details": {
          "name": "",
          "address": "",
          "gstin": ""
        }
      },
      "invoice_details": [
        {
          "item_number": "",
          "item_name": "",
          "quantity": "",
          "unit": "",
          "rate": "",
          "amount": ""
        }
      ],
      "totals": {
        "subtotal": "",
        "cgst_percentage": "",
        "cgst_amount": "",
        "sgst_percentage": "",
        "sgst_amount": "",
        "total": ""
      }
    }

    Do not wrap the response in triple backticks or Markdown. Respond with only JSON text.
    """

    print(f"Processing invoice: {image_path}")
    output = gemini_output(image_path, system_prompt, user_prompt)

    print("Raw Gemini response:")
    print(output)

    # Clean triple backtick if accidentally included
    output = output.strip()
    if output.startswith("```json"):
        output = re.sub(r"^```json\n|```$", "", output)

    try:
        parsed = json.loads(output)
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response. Error: {e}\nResponse:\n{output}")


def main():
    """Main function to run the invoice processing"""
    
    # List available models
    list_available_models()
    
    # Example usage - replace with your image path
    image_path = input("Enter the path to your invoice image: ").strip()
    
    # Check if file exists
    if not Path(image_path).exists():
        print(f"Error: Image file not found at {image_path}")
        return
    
    # Ask if user wants to save output
    save_output = input("Do you want to save output to a file? (y/n): ").strip().lower()
    output_file = None
    
    if save_output == 'y':
        output_file = input("Enter output filename (e.g., invoice_data.json): ").strip()
        if not output_file:
            output_file = "invoice_data.txt"
    
    # Process the invoice
    try:
        result = process_invoice(image_path, output_file)
    except Exception as e:
        print(f"Error processing invoice: {str(e)}")

if __name__ == "__main__":
    main()