# Gemini Workload Logger

A simple GUI application to log your project workload using the Gemini API for console-style logging.

## Setup

1.  **Install Requirements:**
   ```bash
   pip install google-generativeai tkinter python-dotenv
   ```
2. **Get your Gemini API key:** Go to [Google AI Studio](https://makersuite.google.com/app/apikey) and get your Gemini API key.
3.  **Create `.env` file:** In the same directory as the `gemini_logger.py` file, create a `.env` file and add your Gemini API key:

    ```
    GOOGLE_API_KEY="YOUR_ACTUAL_GEMINI_API_KEY_HERE"
    ```
    Remember to replace `YOUR_ACTUAL_GEMINI_API_KEY_HERE` with your actual key.

## Usage

1.  Run the application: `python gemini_logger.py`
2.  Enter your workload update in the text box.
3.  Click on "Save as File" to save a new file or click "Change File" to load an existing log file
4.  Click "Update Log" to append the timestamped, Gemini-formatted log to the current file.

## Features

-   Uses Gemini API to translate input text to console-like status logs.
-   Saves logs to a specified text file.
-   Basic GUI with text input and a display for log entries.
-   Timestamped log entries.
-   Supports saving to new or loading existing log files.

## Important

-   Do not commit the `.env` file containing your API key to version control. The included `.gitignore` takes care of this.

## changelog
*   Adjusted Gemini API interaction for improved stability.
*   Removed structured response constraint to resolve API errors.
*   This change simplifies data retrieval from the model.
*   The system now expects and processes standard text output.
*   This modification enhances application reliability.