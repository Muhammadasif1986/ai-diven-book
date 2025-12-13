"""
Session management service for the RAG chatbot system.
Handles anonymous user sessions and session-related operations.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.user_models import UserSession
from src.core.config import settings


class SessionService:
    """Service for managing user sessions."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_session(self, is_authenticated: bool = False, user_id: Optional[str] = None) -> str:
        """
        Create a new user session.

        Args:
            is_authenticated: Whether the user is authenticated
            user_id: User ID for authenticated users (optional)

        Returns:
            Session token
        """
        session_token = f"sess_{uuid.uuid4().hex}"

        # Calculate expiration time (e.g., 24 hours from now)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Create new session record
        user_session = UserSession(
            session_token=session_token,
            is_authenticated=is_authenticated,
            user_id=user_id,
            expires_at=expires_at
        )

        # Add to database
        self.db_session.add(user_session)
        await self.db_session.commit()
        await self.db_session.refresh(user_session)

        return session_token

    async def get_session(self, session_token: str) -> Optional[UserSession]:
        """
        Get a user session by token.

        Args:
            session_token: The session token to retrieve

        Returns:
            UserSession object if found, None otherwise
        """
        result = await self.db_session.execute(
            select(UserSession).where(UserSession.session_token == session_token)
        )
        session = result.scalar_one_or_none()

        # Check if session has expired
        if session and session.expires_at and session.expires_at < datetime.utcnow():
            await self.delete_session(session_token)
            return None

        return session

    async def extend_session(self, session_token: str) -> bool:
        """
        Extend a user session's expiration time.

        Args:
            session_token: The session token to extend

        Returns:
            True if session was extended, False otherwise
        """
        session = await self.get_session(session_token)
        if not session:
            return False

        # Extend expiration time
        session.expires_at = datetime.utcnow() + timedelta(hours=24)
        await self.db_session.commit()

        return True

    async def delete_session(self, session_token: str) -> bool:
        """
        Delete a user session.

        Args:
            session_token: The session token to delete

        Returns:
            True if session was deleted, False otherwise
        """
        session = await self.get_session(session_token)
        if not session:
            return False

        await self.db_session.delete(session)
        await self.db_session.commit()

        return True

    async def validate_session(self, session_token: str) -> bool:
        """
        Validate if a session is still active.

        Args:
            session_token: The session token to validate

        Returns:
            True if session is valid, False otherwise
        """
        session = await self.get_session(session_token)
        return session is not None

    async def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions from the database.

        Returns:
            Number of sessions cleaned up
        """
        from sqlalchemy import and_

        result = await self.db_session.execute(
            select(UserSession).where(UserSession.expires_at < datetime.utcnow())
        )
        expired_sessions = result.scalars().all()

        for session in expired_sessions:
            await self.db_session.delete(session)

        await self.db_session.commit()
        return len(expired_sessions)