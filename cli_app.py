from imap_client import fetch_all_emails, search_emails
from semantic_search import semantic_search_emails, semantic_search_with_scores
from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env
load_dotenv()

def get_credentials():
    imap_host = os.getenv("IMAP_HOST")
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")

    # Safety check
    if not all([imap_host, email_user, email_pass]):
        print("ERROR: One or more environment variables are missing.")
        print("Make sure your .env file includes:")
        print("IMAP_HOST=...")
        print("EMAIL_USER=...")
        print("EMAIL_PASS=...")
        sys.exit(1)

    return imap_host, email_user, email_pass

def generate_email_summary(email_):
    """Generate a one-line summary of what the email is about."""
    subject = email_['subject']
    body = email_['body']
    
    # If subject is meaningful, use it as the summary
    if subject and subject != "(No Subject)" and len(subject.strip()) > 3:
        return subject.strip()
    
    # Otherwise, use the first meaningful sentence from the body
    if body:
        # Clean up the body text
        lines = body.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Skip very short lines
                # Truncate if too long
                if len(line) > 100:
                    line = line[:97] + "..."
                return line
    
    return "(No content preview available)"

def display_one_line_summary(emails):
    """Display emails with just a one-line summary of what each is about."""
    if not emails:
        print("No emails to display.")
        return

    print(f"\nFound {len(emails)} emails:")
    print("=" * 80)
    for i, email_ in enumerate(emails, 1):
        summary = generate_email_summary(email_)
        print(f"{i:3d}. {summary}")
    print("=" * 80)

def display_summary(emails):
    if not emails:
        print("No emails to display.")
        return

    for i, email_ in enumerate(emails, 1):
        print(f"\n--- Email {i} ---")
        print(f"From: {email_['from']}")
        print(f"Subject: {email_['subject']}")
        print(f"Date: {email_['date']}")

def display_summary_with_scores(results):
    """Display email summary with similarity scores for semantic search."""
    if not results:
        print("No emails to display.")
        return

    for i, (email_, score) in enumerate(results, 1):
        # Color-code scores: green for high (>0.5), yellow for medium (>0.3), red for low
        if score >= 0.5:
            score_indicator = f"🟢 {score:.3f} (High)"
        elif score >= 0.3:
            score_indicator = f"🟡 {score:.3f} (Medium)"
        elif score >= 0.1:
            score_indicator = f"🟠 {score:.3f} (Low)"
        else:
            score_indicator = f"🔴 {score:.3f} (Very Low)"
        
        print(f"\n--- Email {i} | Similarity: {score_indicator} ---")
        print(f"From: {email_['from']}")
        print(f"Subject: {email_['subject']}")
        print(f"Date: {email_['date']}")

def display_full_email(email_):
    print("\n" + "=" * 80)
    print("📧 FULL EMAIL CONTENT")
    print("=" * 80)
    print(f"From: {email_['from']}")
    print(f"Subject: {email_['subject']}")
    print(f"Date: {email_['date']}")
    print("\n" + "-" * 80)
    print("📄 EMAIL BODY:")
    print("-" * 80)
    
    # Display full body content
    full_body = email_.get('full_body', email_.get('body', ''))
    if full_body:
        # Clean up the body for better display
        lines = full_body.split('\n')
        for line in lines:
            print(line.rstrip())
    else:
        print("(No content available)")
    
    print("\n" + "=" * 80)

def run_cli():
    print("Welcome to IMAP Email CLI Tool")

    imap_host, email_user, email_pass = get_credentials()

    while True:
        print("\nChoose an option:")
        print("1. Fetch all emails")
        print("2. Search emails by keyword")
        print("3. Semantic search emails")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()

        try:
            if choice == "1":
                print("Fetching all emails...")
                emails = fetch_all_emails(imap_host, email_user, email_pass)
                display_one_line_summary(emails)

                index = input("\nEnter email number to view full content (or press Enter to skip): ")
                if index.isdigit():
                    index = int(index)
                    if 1 <= index <= len(emails):
                        display_full_email(emails[index - 1])
                    else:
                        print("Invalid index.")
                else:
                    print("Skipping full view.")

            elif choice == "2":
                keyword = input("Enter keyword to search: ").strip()
                emails = search_emails(imap_host, email_user, email_pass, keyword)

                print(f"\nFound {len(emails)} matching email(s) for keyword: '{keyword}'")

                if emails:
                    display_one_line_summary(emails)
                    index = input("\nEnter email number to view full content (or press Enter to skip): ")
                    if index.isdigit():
                        index = int(index)
                        if 1 <= index <= len(emails):
                            display_full_email(emails[index - 1])
                        else:
                            print("Invalid index.")
                    else:
                        print("Skipping full view.")
                else:
                    print("No matching emails found.")

            elif choice == "3":
                query = input("Enter semantic search query: ").strip()
                if not query:
                    print("Please enter a valid search query.")
                    continue
                
                # Ask for threshold (optional)
                threshold_input = input("Enter similarity threshold (0.0-1.0, default 0.1, press Enter to skip): ").strip()
                min_threshold = 0.1  # Default threshold
                
                if threshold_input:
                    try:
                        min_threshold = float(threshold_input)
                        if min_threshold < 0.0 or min_threshold > 1.0:
                            print("Invalid threshold, using default 0.1")
                            min_threshold = 0.1
                    except ValueError:
                        print("Invalid threshold format, using default 0.1")
                        min_threshold = 0.1
                
                print(f"\n🔍 Performing semantic search for: '{query}'")
                print(f"📊 Using similarity threshold: {min_threshold:.3f}")
                print("⏳ This may take a moment while we process the emails...")
                
                try:
                    # Get results with similarity scores and threshold
                    results = semantic_search_with_scores(imap_host, email_user, email_pass, query, top_k=8, min_threshold=min_threshold)
                    
                    if results:
                        # Show model info on first result
                        from semantic_search import get_semantic_engine
                        engine = get_semantic_engine()
                        print(f"\n✅ Found {len(results)} semantically similar email(s) above threshold {min_threshold:.3f}:")
                        print(f"🤖 Model: {engine.model_name}")
                        print("📈 Scores: 🟢 High (≥0.5) | 🟡 Medium (≥0.3) | 🟠 Low (≥0.1) | 🔴 Very Low (<0.1)")
                        display_summary_with_scores(results)
                        
                        index = input("\nEnter email number to view full content (or press Enter to skip): ")
                        if index.isdigit():
                            index = int(index)
                            if 1 <= index <= len(results):
                                email_, score = results[index - 1]
                                print(f"\n📊 [Detailed Similarity Score: {score:.6f}]")
                                display_full_email(email_)
                            else:
                                print("Invalid index.")
                        else:
                            print("Skipping full view.")
                    else:
                        print(f"❌ No semantically similar emails found above threshold {min_threshold:.3f}.")
                        print("💡 Try lowering the threshold or using different search terms.")
                except Exception as e:
                    print(f"❌ Error during semantic search: {e}")
                    print("💡 Note: First-time semantic search may take longer to download the model.")
            
            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Try again.")

        except Exception as e:
            print(f"ERROR: {e}")
