# Gemini Workload Logger

A professional GUI application for logging project workloads with AI-enhanced formatting using Google's Gemini API. The application automatically transforms your plain text entries into well-formatted console-style logs.

## Features

- **AI-Powered Logging**: Uses Google's Gemini API to transform plain text into structured console-style logs
- **Dark Mode Support**: Customizable UI with light and dark themes that respect your system preferences
- **Persistent Settings**: Automatically saves your preferences and recent files
- **Modern Interface**: Clean, intuitive UI with responsive design and smooth animations
- **Accessibility Focused**: Color contrast ratios comply with WCAG AA standards

## Installation

### Prerequisites

- Python 3.7 or higher
- An API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Setup with Virtual Environment (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/gemini-workload-logger.git
   cd gemini-workload-logger
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Gemini API key:
   ```
   GOOGLE_API_KEY="your_api_key_here"
   ```

## Usage

1. Start the application:
   ```bash
   python workload-logger.py
   ```

2. Enter text in the input field and click "Update Log" to add a new log entry
3. Use "Save as File" to create a new log file or "Change File" to open an existing one
4. Toggle between light and dark mode using the checkbox in the top-right corner

## Key Functions

- **Text Transformation**: Converts short input (<30 characters) into structured code-like logs
- **Smart Formatting**: Breaks down longer text into multiple logical console entries
- **Error Handling**: Special formatting for entries containing "bad news" as JavaScript errors
- **Theme Switching**: Smooth animated transitions between light and dark themes

## Project Structure

```
gemini-workload-logger/
├── workload-logger.py     # Main application code
├── requirements.txt       # Project dependencies
├── .env                   # Environment variables (API keys)
├── geminiicon.png         # Application icon
├── README.md              # This documentation
└── cache/                 # Folder for persistent user preferences
```

## Development

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a Pull Request

### Future Enhancements

- Tagging system for organizing logs
- Export options with custom formatting
- Advanced search and filtering capabilities
- Integration with project management tools
- Collaborative log editing for teams

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Google Gemini API](https://ai.google.dev/) for AI-powered text transformation
- [Tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI framework
- All contributors who have helped improve this application

---

*Note: This project is not affiliated with or endorsed by Google. Gemini is a trademark of Google LLC.* 