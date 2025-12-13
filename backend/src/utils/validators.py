"""
Validation utilities for the RAG chatbot system.
"""
import re
from typing import Optional, Tuple


def validate_query_input(
    question: str,
    context_type: str,
    selected_text: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Validate query input parameters.

    Args:
        question: The question to validate
        context_type: The context type ("full_book" or "selection")
        selected_text: Selected text for validation (if applicable)

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate question
    if not question or not question.strip():
        return False, "Question cannot be empty"

    if len(question.strip()) < 5:
        return False, "Question must be at least 5 characters long"

    if len(question.strip()) > 2000:
        return False, "Question must be no more than 2000 characters long"

    # Validate context type
    if context_type not in ["full_book", "selection"]:
        return False, "Context type must be either 'full_book' or 'selection'"

    # Validate selected text if context type is selection
    if context_type == "selection":
        if not selected_text or not selected_text.strip():
            return False, "Selected text cannot be empty when context type is 'selection'"

        if len(selected_text) > 5000:  # Max length from requirements
            return False, f"Selected text too long. Maximum 5000 characters allowed, got {len(selected_text)}"

    return True, "Input is valid"


def validate_book_id(book_id: str) -> Tuple[bool, str]:
    """
    Validate book ID.

    Args:
        book_id: The book ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not book_id or not book_id.strip():
        return False, "Book ID cannot be empty"

    if len(book_id.strip()) < 3:
        return False, "Book ID must be at least 3 characters long"

    if len(book_id.strip()) > 100:
        return False, "Book ID must be no more than 100 characters long"

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', book_id.strip()):
        return False, "Book ID can only contain letters, numbers, hyphens, and underscores"

    return True, "Book ID is valid"


def validate_session_token(session_token: str) -> Tuple[bool, str]:
    """
    Validate session token.

    Args:
        session_token: The session token to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not session_token or not session_token.strip():
        return False, "Session token cannot be empty"

    if len(session_token.strip()) < 10:
        return False, "Session token must be at least 10 characters long"

    if len(session_token.strip()) > 255:
        return False, "Session token must be no more than 255 characters long"

    # Basic check for valid token format (alphanumeric and common separators)
    if not re.match(r'^[a-zA-Z0-9._-]+$', session_token.strip()):
        return False, "Session token contains invalid characters"

    return True, "Session token is valid"


def validate_content_ingestion_data(data: dict) -> Tuple[bool, str]:
    """
    Validate data for content ingestion.

    Args:
        data: The ingestion data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["book_id", "title", "content"]

    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing required field: {field}"

    # Validate book_id
    is_valid, error_msg = validate_book_id(data["book_id"])
    if not is_valid:
        return False, error_msg

    # Validate title
    title = data["title"].strip()
    if len(title) < 1:
        return False, "Title cannot be empty"

    if len(title) > 500:
        return False, "Title must be no more than 500 characters long"

    # Validate content
    content = data["content"]
    if len(content) < 10:  # Minimum content length
        return False, "Content is too short to be meaningful"

    if len(content) > 1000000:  # 1MB limit
        return False, "Content is too large (maximum 1MB)"

    # Validate optional author
    if "author" in data and data["author"]:
        author = data["author"].strip()
        if len(author) > 250:
            return False, "Author name must be no more than 250 characters long"

    return True, "Content ingestion data is valid"


def validate_selection_text(text: str, max_length: int = 5000) -> Tuple[bool, str]:
    """
    Validate selected text based on length constraints.

    Args:
        text: The selected text to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text:
        return False, "Selected text cannot be empty"

    if len(text) > max_length:
        return False, f"Selected text too long. Maximum {max_length} characters allowed."

    # Check for excessive whitespace or special characters that might indicate invalid selection
    if len(text.strip()) == 0:
        return False, "Selected text cannot contain only whitespace"

    return True, "Selected text is valid"


def validate_api_request(request_data: dict, required_fields: list = None) -> Tuple[bool, str]:
    """
    Validate general API request data.

    Args:
        request_data: The request data to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    if required_fields is None:
        required_fields = []

    # Check if request data is a dictionary
    if not isinstance(request_data, dict):
        return False, "Request data must be a JSON object"

    # Check for required fields
    for field in required_fields:
        if field not in request_data or request_data[field] is None:
            return False, f"Missing required field: {field}"

    # Validate field types and values
    for field, value in request_data.items():
        if value is not None:
            # Check for potentially dangerous content
            if isinstance(value, str):
                # Basic check for potential code injection
                dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
                for pattern in dangerous_patterns:
                    if pattern.lower() in value.lower():
                        return False, f"Field '{field}' contains potentially dangerous content"

                # Check for excessively long strings that might indicate abuse
                if len(value) > 10000:  # 10KB limit for most text fields
                    return False, f"Field '{field}' is too long (maximum 10000 characters)"

    return True, "Request data is valid"


def validate_user_session(session_token: str) -> Tuple[bool, str]:
    """
    Validate user session token format.

    Args:
        session_token: The session token to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not session_token or not session_token.strip():
        return False, "Session token cannot be empty"

    if len(session_token.strip()) < 10:
        return False, "Session token must be at least 10 characters long"

    if len(session_token.strip()) > 255:
        return False, "Session token must be no more than 255 characters long"

    # Basic check for valid token format (alphanumeric and common separators)
    if not re.match(r'^[a-zA-Z0-9._-]+$', session_token.strip()):
        return False, "Session token contains invalid characters"

    return True, "Session token is valid"


def validate_book_content(content: str) -> Tuple[bool, str]:
    """
    Validate book content for ingestion.

    Args:
        content: The book content to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not content:
        return False, "Book content cannot be empty"

    if len(content) < 50:  # Minimum content length
        return False, "Book content is too short to be meaningful (minimum 50 characters)"

    if len(content) > 10 * 1024 * 1024:  # 10MB limit
        return False, "Book content is too large (maximum 10MB)"

    # Check for potentially harmful content
    dangerous_patterns = ['<script', 'javascript:', 'eval(', 'exec(']
    for pattern in dangerous_patterns:
        if pattern.lower() in content.lower():
            return False, f"Content contains potentially dangerous code: {pattern}"

    return True, "Book content is valid"