# Mail CLI Tool

A Python-based email client that provides both command-line interface (CLI) and web API functionality for accessing and searching emails via IMAP.

## Features

- **CLI Interface**: Interactive command-line tool for email management
- **Web API**: RESTful API endpoints for programmatic email access
- **Email Fetching**: Retrieve recent emails from your inbox
- **Keyword Search**: Search emails by keywords across subject, body, sender, and date
- **Semantic Search**: AI-powered semantic search using local embeddings (no cloud APIs required)
- **Multiple Email Providers**: Support for any IMAP-enabled email provider (Gmail, Outlook, etc.)
- **Environment Configuration**: Secure credential management using environment variables

## Prerequisites

- Python 3.6 or higher
- An email account with IMAP access enabled
- For Gmail: App-specific password required (not your regular password)

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your email credentials:
   ```env
   IMAP_HOST=imap.gmail.com
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   ```

## Usage

### Command Line Interface

Run the CLI tool:
```bash
python main.py
```

The CLI provides the following options:
1. **Fetch all emails**: Displays recent emails (default: 5 most recent)
2. **Search emails by keyword**: Traditional keyword search across all emails
3. **Semantic search emails**: AI-powered semantic search that understands context and meaning
4. **View full email content**: Select any email to view its complete content

### Web API

Start the web API server:
```bash
python main.py api
```

The API will be available at `http://localhost:5000`

#### API Endpoints

**GET /** - Homepage with API documentation

**POST /fetch** - Fetch recent emails
```json
{
  "imap_host": "imap.gmail.com",
  "email": "your_email@gmail.com",
  "password": "your_app_password",
  "folder": "INBOX"
}
```

**POST /search** - Search emails by keyword
```json
{
  "imap_host": "imap.gmail.com",
  "email": "your_email@gmail.com",
  "password": "your_app_password",
  "keyword": "invoice",
  "folder": "INBOX"
}
```

**POST /semantic-search** - Perform semantic search on emails
```json
{
  "imap_host": "imap.gmail.com",
  "email": "your_email@gmail.com",
  "password": "your_app_password",
  "query": "meeting tomorrow",
  "top_k": 5,
  "folder": "INBOX",
  "min_threshold": 0.1,
  "include_scores": true
}
```

**Enhanced API Response:**
```json
{
  "results": [
    {
      "email": {
        "subject": "Team standup tomorrow",
        "from": "manager@company.com",
        "date": "Wed, 09 Jul 2025 14:30:00 GMT",
        "body": "Hi team, we have our weekly standup..."
      },
      "similarity_score": 0.756,
      "score_category": "high",
      "threshold_used": 0.1
    }
  ],
  "total_found": 1,
  "threshold_used": 0.1,
  "query": "meeting tomorrow"
}
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `IMAP_HOST` | IMAP server hostname | `imap.gmail.com` |
| `EMAIL_USER` | Your email address | `user@gmail.com` |
| `EMAIL_PASS` | Your email password/app password | `your_app_password` |

### Common IMAP Hosts

| Provider | IMAP Host | Port |
|----------|-----------|------|
| Gmail | `imap.gmail.com` | 993 |
| Outlook/Hotmail | `imap-mail.outlook.com` | 993 |
| Yahoo | `imap.mail.yahoo.com` | 993 |
| Apple iCloud | `imap.mail.me.com` | 993 |

## File Structure

```
mail-cli/
├── main.py          # Entry point - CLI or API mode
├── cli_app.py       # CLI interface implementation
├── web_app.py       # Flask web API implementation
├── imap_client.py   # IMAP client and email parsing logic
├── semantic_search.py # Semantic search functionality
├── requirements.txt # Python dependencies
├── .env            # Environment variables (create this)
└── README.md       # This file
```

## Security Notes

- Never commit your `.env` file to version control
- Use app-specific passwords for Gmail (not your regular password)
- The API accepts credentials in requests - use HTTPS in production
- Consider implementing authentication for the web API in production environments

## Error Handling

The application includes comprehensive error handling for:
- Missing environment variables
- Invalid IMAP credentials
- Network connectivity issues
- Email parsing errors
- Invalid API requests

## Semantic Search

### How It Works

The semantic search feature uses local AI models to understand the meaning behind your search queries:

1. **Local Processing**: Uses the `all-mpnet-base-v2` model from sentence-transformers (runs locally, no cloud APIs)
2. **Email Cleaning**: Automatically removes HTML tags, URLs, email addresses, signatures, and quoted text
3. **Vector Embeddings**: Converts cleaned email content and search queries into high-dimensional vectors
4. **Similarity Matching**: Computes cosine similarity between query and email vectors
5. **Threshold Filtering**: Filters results based on configurable similarity thresholds (default: 0.1)
6. **Score Categorization**: Returns emails with color-coded similarity scores and confidence levels

### Enhanced Email Display

**Show Complete Emails**: Full email content is displayed without truncation when viewing.

**Semantic Search** finds emails by meaning, not just keywords:
- "conference call scheduled"
- "team sync tomorrow"
- "project discussion"
- "client presentation"

### Similarity Score Categories

- 🟢 **High (≥0.5)**: Very relevant matches
- 🟡 **Medium (≥0.3)**: Moderately relevant matches  
- 🟠 **Low (≥0.1)**: Somewhat relevant matches
- 🔴 **Very Low (0.1)**: Potentially relevant matches

### Email Body Cleaning

The system automatically cleans email content before processing:
- ✅ Removes HTML tags and entities
- ✅ Strips URLs and email addresses
- ✅ Eliminates email signatures and footers
- ✅ Removes quoted text ( lines)
- ✅ Filters out unsubscribe links and privacy notices
- ✅ Limits content length for optimal processing

### First-Time Setup

On first use, the semantic search will download the AI model (~420MB). This only happens once:
```
Loading semantic search model 'all-mpnet-base-v2' (this may take a moment on first run)...
✅ Semantic search model 'all-mpnet-base-v2' loaded successfully!
```

## Dependencies

- **Flask**: Web framework for API endpoints
- **python-dotenv**: Environment variable management
- **sentence-transformers**: Local AI models for semantic search
- **numpy**: Numerical operations for embeddings
- **scikit-learn**: Cosine similarity calculations
- **imaplib**: Built-in Python IMAP client
- **email**: Built-in Python email parsing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for more details.

## Troubleshooting

### Common Issues

1. **"Authentication failed"**
   - Verify your email credentials
   - For Gmail, ensure you're using an app-specific password
   - Check that IMAP is enabled in your email settings

2. **"Connection timeout"**
   - Verify the IMAP host is correct
   - Check your internet connection
   - Some networks may block IMAP ports

3. **"No emails found"**
   - Check if you have emails in the specified folder
   - Try searching with different keywords
   - Verify folder names (case-sensitive)

4. **"Semantic search model loading issues"**
   - Ensure you have a stable internet connection for first-time model download
   - Check available disk space (~420MB required for model)
   - If download fails, the system will automatically fallback to a smaller model
   - Try running with administrator privileges if permission issues occur

5. **"Semantic search taking too long"**
   - First-time usage downloads the AI model and may take a few minutes
   - Subsequent searches should be much faster
   - Consider reducing the number of emails being processed

### Getting Help

If you encounter issues:
1. Check the error messages in the console
2. Verify your `.env` file configuration
3. Test your email credentials with a standard email client
4. Check firewall and network settings
