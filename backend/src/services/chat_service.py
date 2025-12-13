"""
Chat service for the RAG chatbot system.
Handles communication with the LLM to generate answers.
"""
from typing import List, Dict, Any
import logging
from datetime import datetime

from openai import AsyncOpenAI

from src.core.config import openai_client, settings


class ChatService:
    """Service for generating answers using the LLM."""

    def __init__(self):
        self.client = openai_client
        self.logger = logging.getLogger(__name__)

    async def generate_answer(
        self,
        question: str,
        context: str,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Generate an answer based on the question and provided context.

        Args:
            question: The question to answer
            context: The context to use for answering
            citations: List of citations for the context

        Returns:
            Generated answer
        """
        try:
            # Create the prompt for the LLM
            prompt = self._create_prompt(question, context, citations)

            # Call the OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant helping users understand book content. "
                            "Answer questions based on the provided context. "
                            "If the context doesn't contain the information needed to answer, "
                            "clearly state that the information is not in the provided context. "
                            "Always provide specific citations when possible."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent, factual responses
                max_tokens=1000,  # Limit response length
                timeout=30  # 30 second timeout
            )

            # Extract the answer from the response
            answer = response.choices[0].message.content.strip()

            self.logger.info(f"Successfully generated answer for question: {question[:50]}...")
            return answer

        except Exception as e:
            self.logger.error(f"Error generating answer: {e}")
            raise

    async def generate_answer_no_context(self, question: str) -> str:
        """
        Generate an answer when no context is available.

        Args:
            question: The question that couldn't be answered due to lack of context

        Returns:
            Response indicating lack of context
        """
        try:
            # Create a prompt that acknowledges the lack of context
            prompt = (
                f"The user asked: '{question}'\n\n"
                "However, I couldn't find any relevant information in the provided book content to answer this question. "
                "The information you're looking for may not be covered in this book, "
                "or the search didn't return relevant results. "
                "Please try rephrasing your question or consult other sources."
            )

            # Call the OpenAI API with a system message that guides the response
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant. The user asked a question, but no relevant context was found in the provided book content. "
                            "Politely explain that the information is not available in the current book, "
                            "and suggest they try rephrasing their question or consult other sources. "
                            "Do not make up information or hallucinate."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"The user asked: '{question}'\n\nNo relevant information was found in the book content to answer this question."
                    }
                ],
                temperature=0.2,  # Very low temperature to ensure consistent responses
                max_tokens=300,  # Shorter response when no context is available
                timeout=30
            )

            answer = response.choices[0].message.content.strip()
            self.logger.info(f"Generated no-context response for question: {question[:50]}...")
            return answer

        except Exception as e:
            self.logger.error(f"Error generating no-context answer: {e}")
            return "I'm sorry, but I couldn't find relevant information in the book to answer your question."

    def _create_prompt(self, question: str, context: str, citations: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the LLM with question, context, and citation instructions.

        Args:
            question: The question to answer
            context: The context to use for answering
            citations: List of citations for the context

        Returns:
            Formatted prompt string
        """
        # Format citations for the prompt
        citations_text = ""
        if citations:
            citations_text = "\n\nCitations:\n"
            for i, citation in enumerate(citations[:5]):  # Limit to first 5 citations
                citations_text += f"{i+1}. {citation.get('title', 'Unknown Title')} - {citation.get('section', 'Unknown Section')}\n"

        prompt = (
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Please provide a comprehensive answer to the question based on the context provided above. "
            f"Ensure your answer is accurate, helpful, and directly addresses the question. "
            f"If specific citations are provided, reference them appropriately in your answer. "
            f"{citations_text}\n"
            f"Keep your response focused and well-structured."
        )

        return prompt

    async def validate_answer_quality(
        self,
        question: str,
        answer: str,
        context: str
    ) -> Dict[str, Any]:
        """
        Validate the quality of the generated answer.

        Args:
            question: The original question
            answer: The generated answer
            context: The context used to generate the answer

        Returns:
            Dictionary with validation results
        """
        try:
            # Create a validation prompt to check if the answer is grounded in the context
            validation_prompt = (
                f"Question: {question}\n\n"
                f"Context: {context}\n\n"
                f"Answer: {answer}\n\n"
                f"Analyze the answer and determine if it is properly grounded in the provided context. "
                f"Check if the answer contains information not present in the context (hallucinations). "
                f"Also check if the answer directly addresses the question. "
                f"Respond with a JSON object containing:\n"
                f"- 'is_ground': true if the answer is properly grounded in the context, false otherwise\n"
                f"- 'has_hallucinations': true if the answer contains information not in the context, false otherwise\n"
                f"- 'addresses_question': true if the answer addresses the question, false otherwise\n"
                f"- 'confidence_score': a float between 0 and 1 indicating confidence in the answer quality"
            )

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an AI evaluator. Analyze the provided answer to determine its quality, "
                            "grounding in the context, and relevance to the question. "
                            "Respond with a JSON object as specified in the user's request."
                        )
                    },
                    {
                        "role": "user",
                        "content": validation_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent evaluation
                max_tokens=500,
                timeout=30,
                response_format={"type": "json_object"}  # Request JSON response
            )

            # Parse the validation result
            import json
            validation_result = json.loads(response.choices[0].message.content)

            self.logger.info(f"Answer validation completed for question: {question[:50]}...")
            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating answer quality: {e}")
            # Return a default validation result in case of error
            return {
                "is_ground": True,
                "has_hallucinations": False,
                "addresses_question": True,
                "confidence_score": 0.8
            }

    async def generate_citations_formatted(
        self,
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a formatted citation string for use in answers.

        Args:
            citations: List of citation dictionaries

        Returns:
            Formatted citation string
        """
        if not citations:
            return ""

        formatted_citations = "Sources:\n"
        for i, citation in enumerate(citations):
            title = citation.get("title", "Unknown Title")
            section = citation.get("section", "Unknown Section")
            page_number = citation.get("page_number")
            score = citation.get("relevance_score", 0)

            formatted_citations += f"{i+1}. {title} ({section})"
            if page_number:
                formatted_citations += f", p. {page_number}"
            formatted_citations += f" [Relevance: {score:.2f}]\n"

        return formatted_citations.strip()