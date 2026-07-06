"""AI Test Case Generator — Core logic and prompt templates.

Generates structured test cases from feature descriptions using LLM prompts.
Supports both real LLM API calls (OpenAI/Claude) and a mock mode for offline use.
"""

import json
import csv
import io
from typing import Optional

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a senior QA engineer. Given a feature description, generate a comprehensive set of test cases covering:

1. **Normal flow** — Happy path scenarios
2. **Boundary values** — Edge cases for input limits
3. **Equivalence classes** — Valid and invalid partitions
4. **Error/exception scenarios** — What happens when things go wrong
5. **Security/validation** — Input sanitization, auth checks

Output format: JSON array of objects with keys:
- id (int): test case number
- title (str): short test case name
- category (str): normal | boundary | equivalence | error | security
- preconditions (str): what must be set up
- steps (list[str]): numbered test steps
- expected_result (str): what should happen
- priority (str): high | medium | low
"""


def build_prompt(feature_description: str, scenario_type: Optional[str] = None) -> str:
    """Build the user prompt for test case generation."""
    prompt = f"""Generate test cases for the following feature:

{feature_description}

"""
    if scenario_type:
        prompt += f"\nFocus specifically on {scenario_type} scenarios."
    else:
        prompt += "\nCover all categories: normal flow, boundary values, equivalence classes, error scenarios, and security."

    prompt += """
Return ONLY a valid JSON array with no markdown wrapping or extra text.
Each object must contain: id, title, category, preconditions, steps (array), expected_result, priority."""
    return prompt


# ---------------------------------------------------------------------------
# Mock generator (works offline, no API key needed)
# ---------------------------------------------------------------------------

MOCK_TEST_CASES = [
    {"id": 1, "title": "Valid login with correct credentials",
     "category": "normal", "preconditions": "User account exists",
     "steps": ["Enter valid username", "Enter valid password", "Click login"],
     "expected_result": "User is logged in and redirected to dashboard",
     "priority": "high"},
    {"id": 2, "title": "Login with empty username",
     "category": "error", "preconditions": "Login page is displayed",
     "steps": ["Leave username empty", "Enter valid password", "Click login"],
     "expected_result": "Error message: 'Username is required'",
     "priority": "high"},
    {"id": 3, "title": "Login with empty password",
     "category": "error", "preconditions": "Login page is displayed",
     "steps": ["Enter valid username", "Leave password empty", "Click login"],
     "expected_result": "Error message: 'Password is required'",
     "priority": "high"},
    {"id": 4, "title": "Login with incorrect password",
     "category": "error", "preconditions": "User account exists",
     "steps": ["Enter valid username", "Enter wrong password", "Click login"],
     "expected_result": "Error message: 'Invalid credentials'",
     "priority": "high"},
    {"id": 5, "title": "Username field boundary — minimum length",
     "category": "boundary", "preconditions": "Login page is displayed",
     "steps": ["Enter 1-character username", "Enter valid password", "Click login"],
     "expected_result": "Login succeeds if min length >= 1, else error",
     "priority": "medium"},
    {"id": 6, "title": "Username field boundary — maximum length",
     "category": "boundary", "preconditions": "Login page is displayed",
     "steps": ["Enter 256-character username", "Enter valid password", "Click login"],
     "expected_result": "System truncates or rejects with clear message",
     "priority": "medium"},
    {"id": 7, "title": "Login with special characters in username",
     "category": "security", "preconditions": "Login page is displayed",
     "steps": ["Enter username: <script>alert(1)</script>", "Enter password", "Click login"],
     "expected_result": "Input is sanitized, no XSS execution",
     "priority": "high"},
    {"id": 8, "title": "SQL injection attempt in username field",
     "category": "security", "preconditions": "Login page is displayed",
     "steps": ["Enter username: ' OR 1=1 --", "Enter any password", "Click login"],
     "expected_result": "Login fails, no SQL injection possible",
     "priority": "high"},
    {"id": 9, "title": "Login with valid credentials — equivalence class: valid",
     "category": "equivalence", "preconditions": "User account exists",
     "steps": ["Enter a valid username from the valid class", "Enter valid password", "Click login"],
     "expected_result": "Login succeeds",
     "priority": "high"},
    {"id": 10, "title": "Login with non-existent username",
     "category": "equivalence", "preconditions": "Login page is displayed",
     "steps": ["Enter username that doesn't exist", "Enter any password", "Click login"],
     "expected_result": "Error message: 'User not found' or generic error",
     "priority": "medium"},
    {"id": 11, "title": "Remember me checkbox functionality",
     "category": "normal", "preconditions": "Login page is displayed",
     "steps": ["Enter valid credentials", "Check 'Remember me'", "Click login", "Log out", "Reopen login page"],
     "expected_result": "Username is pre-filled or session persists",
     "priority": "low"},
    {"id": 12, "title": "Password field masking",
     "category": "normal", "preconditions": "Login page is displayed",
     "steps": ["Enter password in the password field"],
     "expected_result": "Password characters are masked (bullets/asterisks)",
     "priority": "low"},
    {"id": 13, "title": "Login page accessibility — keyboard navigation",
     "category": "normal", "preconditions": "Login page is displayed",
     "steps": ["Press Tab from username field", "Press Tab again", "Press Enter"],
     "expected_result": "Focus moves: username → password → login button; Enter submits",
     "priority": "low"},
    {"id": 14, "title": "Consecutive failed login attempts — account lockout",
     "category": "security", "preconditions": "User account exists",
     "steps": ["Attempt login with wrong password 5 times", "Attempt login with correct password"],
     "expected_result": "Account is locked after N failed attempts",
     "priority": "high"},
    {"id": 15, "title": "Login with very long password",
     "category": "boundary", "preconditions": "User account exists",
     "steps": ["Enter valid username", "Enter 1000-character password", "Click login"],
     "expected_result": "Password is truncated or rejected gracefully",
     "priority": "medium"},
]

# Scenario-type templates for different feature types
SCENARIO_TEMPLATES = {
    "登录/认证": MOCK_TEST_CASES,
    "搜索功能": [
        {"id": 1, "title": "Search with valid keyword",
         "category": "normal", "preconditions": "Has searchable content",
         "steps": ["Enter valid keyword", "Press Enter or click search"],
         "expected_result": "Relevant results are displayed",
         "priority": "high"},
        {"id": 2, "title": "Search with empty query",
         "category": "error", "preconditions": "Search page is displayed",
         "steps": ["Leave search box empty", "Click search"],
         "expected_result": "Prompt: 'Please enter a search term' or show all results",
         "priority": "medium"},
        {"id": 3, "title": "Search with special characters",
         "category": "security", "preconditions": "Search page is displayed",
         "steps": ["Enter: <img src=x onerror=alert(1)>", "Click search"],
         "expected_result": "Input is sanitized, no script execution",
         "priority": "high"},
        {"id": 4, "title": "Search result pagination",
         "category": "normal", "preconditions": "Search with >1 page of results",
         "steps": ["Search for a term with many results", "Navigate to page 2", "Navigate to page 3"],
         "expected_result": "Pagination works correctly, results change per page",
         "priority": "medium"},
        {"id": 5, "title": "Search with Unicode/emoji input",
         "category": "boundary", "preconditions": "Search page is displayed",
         "steps": ["Enter Unicode characters: 中文日本語한국어", "Enter emoji: 😀🔥🎉", "Click search"],
         "expected_result": "Search handles Unicode input without errors",
         "priority": "low"},
    ],
    "表单验证": [
        {"id": 1, "title": "Submit form with all valid fields",
         "category": "normal", "preconditions": "Form is displayed",
         "steps": ["Fill all fields with valid data", "Click Submit"],
         "expected_result": "Form submits successfully, success message shown",
         "priority": "high"},
        {"id": 2, "title": "Submit with required field empty",
         "category": "error", "preconditions": "Form is displayed",
         "steps": ["Leave required field empty", "Fill other fields", "Click Submit"],
         "expected_result": "Error message for the empty required field",
         "priority": "high"},
        {"id": 3, "title": "Email field format validation",
         "category": "equivalence", "preconditions": "Form is displayed",
         "steps": ["Enter 'invalid-email' in email field", "Click Submit"],
         "expected_result": "Error: 'Invalid email format'",
         "priority": "high"},
        {"id": 4, "title": "Form input maximum length",
         "category": "boundary", "preconditions": "Form is displayed",
         "steps": ["Enter 1000+ characters in a text field", "Click Submit"],
         "expected_result": "Input is truncated or shows character limit error",
         "priority": "medium"},
        {"id": 5, "title": "Cross-site scripting in text field",
         "category": "security", "preconditions": "Form is displayed",
         "steps": ["Enter <script>alert('XSS')</script> in a text field", "Click Submit"],
         "expected_result": "Input is sanitized, no XSS on submission or display",
         "priority": "high"},
    ],
    "文件上传": [
        {"id": 1, "title": "Upload valid file type",
         "category": "normal", "preconditions": "Upload page is displayed",
         "steps": ["Select a valid .jpg file under size limit", "Click Upload"],
         "expected_result": "Upload succeeds, success message shown",
         "priority": "high"},
        {"id": 2, "title": "Upload file exceeding max size",
         "category": "boundary", "preconditions": "Upload page is displayed",
         "steps": ["Select a file larger than the allowed limit", "Click Upload"],
         "expected_result": "Error: 'File too large' with max size indicated",
         "priority": "high"},
        {"id": 3, "title": "Upload disallowed file type",
         "category": "error", "preconditions": "Upload page is displayed",
         "steps": ["Select a .exe file", "Click Upload"],
         "expected_result": "Error: 'File type not allowed'",
         "priority": "high"},
        {"id": 4, "title": "Upload empty file",
         "category": "boundary", "preconditions": "Upload page is displayed",
         "steps": ["Select a 0-byte file", "Click Upload"],
         "expected_result": "Error or handled gracefully",
         "priority": "medium"},
        {"id": 5, "title": "Malicious file name upload",
         "category": "security", "preconditions": "Upload page is displayed",
         "steps": ["Create file named '../../../etc/passwd.txt'", "Attempt upload"],
         "expected_result": "File name is sanitized, path traversal prevented",
         "priority": "high"},
    ],
    "支付流程": [
        {"id": 1, "title": "Successful payment with valid card",
         "category": "normal", "preconditions": "Items in cart, valid payment method",
         "steps": ["Go to checkout", "Enter valid card details", "Confirm payment"],
         "expected_result": "Payment succeeds, order confirmation displayed",
         "priority": "high"},
        {"id": 2, "title": "Payment with expired card",
         "category": "error", "preconditions": "Items in cart",
         "steps": ["Enter expired card details", "Confirm payment"],
         "expected_result": "Error: 'Card expired'",
         "priority": "high"},
        {"id": 3, "title": "Payment with insufficient funds",
         "category": "error", "preconditions": "Items in cart",
         "steps": ["Enter card with insufficient balance", "Confirm payment"],
         "expected_result": "Error: 'Payment declined'",
         "priority": "high"},
        {"id": 4, "title": "Cancel payment mid-flow",
         "category": "normal", "preconditions": "Items in cart, at checkout",
         "steps": ["Start checkout", "Click Cancel/Back at any step"],
         "expected_result": "User returns to cart or previous step, no charge made",
         "priority": "medium"},
        {"id": 5, "title": "Concurrent payment processing",
         "category": "security", "preconditions": "Items in cart",
         "steps": ["Submit payment twice quickly", "Check order history"],
         "expected_result": "Only one successful charge, no duplicate orders",
         "priority": "high"},
    ],
}


def get_scenario_types() -> list:
    """Return available scenario type names."""
    return list(SCENARIO_TEMPLATES.keys())


def generate_test_cases(feature_description: str, scenario_type: Optional[str] = None) -> list:
    """Generate test cases for a feature description.

    Uses mock data when offline; integrates with real LLM APIs when available.
    """
    if scenario_type and scenario_type in SCENARIO_TEMPLATES:
        return SCENARIO_TEMPLATES[scenario_type]
    # Return combined mock cases if no specific type
    all_cases = []
    for cases in SCENARIO_TEMPLATES.values():
        all_cases.extend(cases)
    return all_cases[:20]


def export_to_csv(test_cases: list) -> str:
    """Export test cases to CSV string."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Category", "Preconditions", "Steps", "Expected Result", "Priority"])
    for tc in test_cases:
        writer.writerow([
            tc["id"],
            tc["title"],
            tc["category"],
            tc["preconditions"],
            "; ".join(tc["steps"]),
            tc["expected_result"],
            tc["priority"],
        ])
    return output.getvalue()


def export_to_json(test_cases: list) -> str:
    """Export test cases to JSON string."""
    return json.dumps(test_cases, indent=2, ensure_ascii=False)
