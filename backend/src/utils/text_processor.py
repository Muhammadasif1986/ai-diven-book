"""
Text processing utilities for the RAG chatbot system.
"""
import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    start_idx: int
    end_idx: int
    chunk_id: str


class TextProcessor:
    """Utility class for processing and chunking text content."""

    def __init__(self, chunk_size: int = 512, overlap: int = 100):
        """
        Initialize the text processor.

        Args:
            chunk_size: Target size of each chunk in tokens (approximate)
            overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Approximate token to character ratio (varies by language and text)
        # Using 4 characters per token as a rough approximation
        self.chars_per_token = 4
        self.max_chunk_chars = chunk_size * self.chars_per_token
        self.overlap_chars = overlap * self.chars_per_token

    def chunk_text(self, text: str, source_file: str = "", title: str = "", section: str = "") -> List[TextChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: The text to chunk
            source_file: Source file identifier
            title: Title of the content
            section: Section identifier

        Returns:
            List of TextChunk objects
        """
        if not text or len(text.strip()) == 0:
            return []

        chunks = []
        start_idx = 0
        chunk_id_counter = 0

        while start_idx < len(text):
            # Determine the end position for this chunk
            end_idx = start_idx + self.max_chunk_chars

            # If we're near the end of the text, adjust end_idx
            if end_idx >= len(text):
                end_idx = len(text)
            else:
                # Try to break at sentence boundary
                # Look for sentence endings near the end of our chunk
                sentence_end = self._find_sentence_end(text, start_idx, end_idx)
                if sentence_end != -1:
                    end_idx = sentence_end

                # If no good sentence boundary found, look for paragraph boundary
                if end_idx == start_idx + self.max_chunk_chars:
                    paragraph_end = self._find_paragraph_end(text, start_idx, end_idx)
                    if paragraph_end != -1:
                        end_idx = paragraph_end

                # If still no good boundary, just break at max_chunk_chars
                # but make sure we don't split in the middle of a word
                if end_idx == start_idx + self.max_chunk_chars:
                    word_end = self._find_word_end(text, start_idx, end_idx)
                    if word_end != -1:
                        end_idx = word_end

            # Extract the chunk
            chunk_text = text[start_idx:end_idx].strip()
            if len(chunk_text) > 0:  # Only add non-empty chunks
                chunk_id = f"{source_file}:{title}:{section}:{chunk_id_counter}"
                chunks.append(TextChunk(
                    text=chunk_text,
                    start_idx=start_idx,
                    end_idx=end_idx,
                    chunk_id=chunk_id
                ))
                chunk_id_counter += 1

            # Determine the next start position with overlap
            if end_idx >= len(text):
                # At the end of the text
                break

            # Move start position forward, accounting for overlap
            next_start = end_idx - self.overlap_chars
            if next_start <= start_idx:
                # If overlap would cause us to not advance, move by a full chunk
                next_start = start_idx + self.max_chunk_chars

            # Ensure we don't get stuck in an infinite loop
            if next_start <= start_idx:
                next_start = start_idx + 1

            start_idx = next_start

        return chunks

    def _find_sentence_end(self, text: str, start: int, end: int) -> int:
        """
        Find the best sentence ending within the range [start, end].

        Args:
            text: The text to search
            start: Start position to search from
            end: End position to search to

        Returns:
            Position of sentence end, or -1 if not found
        """
        # Look for sentence endings: . ! ? followed by space or end of text
        # Also consider abbreviations and decimal numbers to avoid false positives
        sentence_endings = [r'[.!?]\s+', r'[.!?](?=\n)', r'[.!?](?=\Z)']

        for ending_pattern in sentence_endings:
            # Search in reverse from the end position
            search_start = max(start, end - 200)  # Don't search too far back
            search_text = text[search_start:end]

            matches = list(re.finditer(ending_pattern, search_text))
            if matches:
                # Get the last match in our search range
                last_match = matches[-1]
                actual_pos = search_start + last_match.end()
                # Ensure it's within our original range
                if start < actual_pos <= end:
                    return actual_pos

        return -1

    def _find_paragraph_end(self, text: str, start: int, end: int) -> int:
        """
        Find the best paragraph ending within the range [start, end].

        Args:
            text: The text to search
            start: Start position to search from
            end: End position to search to

        Returns:
            Position of paragraph end, or -1 if not found
        """
        # Look for double newlines (paragraph breaks)
        search_start = max(start, end - 200)  # Don't search too far back
        search_text = text[search_start:end]

        # Find the last double newline in the search range
        para_end_pos = search_text.rfind('\n\n')
        if para_end_pos != -1:
            actual_pos = search_start + para_end_pos + 2  # +2 for the '\n\n'
            if start < actual_pos <= end:
                return actual_pos

        # If no double newline, look for single newlines
        single_para_end = search_text.rfind('\n')
        if single_para_end != -1:
            actual_pos = search_start + single_para_end + 1  # +1 for the '\n'
            if start < actual_pos <= end:
                return actual_pos

        return -1

    def _find_word_end(self, text: str, start: int, end: int) -> int:
        """
        Find the best word boundary within the range [start, end].

        Args:
            text: The text to search
            start: Start position to search from
            end: End position to search to

        Returns:
            Position of word end, or -1 if not found
        """
        # Look for the last space or punctuation before the end
        search_start = max(start, end - 100)  # Don't search too far back
        search_text = text[search_start:end]

        # Find the last word boundary
        for i in range(len(search_text) - 1, -1, -1):
            if search_text[i] in ' \t\n\r.,;:!?()[]{}"\'':
                actual_pos = search_start + i
                if start < actual_pos < end:
                    return actual_pos

        return -1

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: The text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove extra newlines but preserve paragraph structure
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def validate_selection_text(self, text: str, max_length: int = 5000) -> Tuple[bool, str]:
        """
        Validate selected text based on length constraints.

        Args:
            text: The selected text to validate
            max_length: Maximum allowed length (default from settings)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return False, "Selected text cannot be empty"

        if len(text) > max_length:
            return False, f"Selected text too long. Maximum {max_length} characters allowed."

        return True, "Text is valid"


# Create a default text processor instance
default_text_processor = TextProcessor()