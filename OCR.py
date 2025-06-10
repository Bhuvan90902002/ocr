import os
import google.generativeai as genai
from pathlib import Path
import json
import re
import base64
from dotenv import load_dotenv

# Load environment variables from .env file (for local testing)
load_dotenv()

# Set your Google API key from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=GOOGLE_API_KEY)

# ... existing MODEL_CONFIG and safety_settings ...

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=MODEL_CONFIG,
    safety_settings=safety_settings
)

def image_format(image_data, mime_type):
    """Format image for Gemini API from base64 data"""
    image_parts = [
        {
            "mime_type": mime_type,
            "data": base64.b64decode(image_data)
        }
    ]
    return image_parts

def gemini_output(image_data, mime_type, system_prompt, user_prompt):
    """Generate output using Gemini model"""
    try:
        image_info = image_format(image_data, mime_type)
        input_prompt = [system_prompt, image_info[0], user_prompt]
        response = model.generate_content(input_prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Error processing image with Gemini: {str(e)}")

def process_invoice(image_data, mime_type):
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

    output = gemini_output(image_data, mime_type, system_prompt, user_prompt)

    # Clean triple backtick if accidentally included
    output = output.strip()
    if output.startswith("```json"):
        output = re.sub(r"^```json\n|```$", "", output)

    try:
        parsed = json.loads(output)
        return parsed
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Gemini response. Error: {e}\nResponse:\n{output}")

def lambda_handler(event, context):
    """AWS Lambda function handler"""
    try:
        # Expecting image data in the event body as base64 encoded string
        # and mime_type in headers or query parameters
        body = json.loads(event['body'])
        image_data = body.get('image_data')
        mime_type = body.get('mime_type', 'image/jpeg') # Default to jpeg if not provided

        if not image_data:
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps({ 'error': 'No image_data provided in the request body.' })
            }

        result = process_invoice(image_data, mime_type)

        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps(result)
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({ 'error': 'Invalid JSON in request body.' })
        }
    except KeyError:
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({ 'error': 'Request body must contain an \'image_data\' field.' })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({ 'error': f'Internal server error: {str(e)}' })
        }

# Remove the main() function as it's not needed for Lambda
# if __name__ == "__main__":
#     main()