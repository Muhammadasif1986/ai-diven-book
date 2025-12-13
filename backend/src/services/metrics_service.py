"""
Metrics service for the RAG chatbot system.
Tracks API usage and performance metrics.
"""
from datetime import datetime
from typing import Optional, List
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.models.user_models import APIMetric
from src.core.config import settings


class MetricsService:
    """Service for tracking and managing API usage metrics."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.logger = logging.getLogger(__name__)

    async def log_api_call(
        self,
        session_token: str,
        endpoint: str,
        request_data: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        rate_limited: bool = False
    ) -> APIMetric:
        """
        Log an API call to track usage metrics.

        Args:
            session_token: The session token for the request
            endpoint: The API endpoint that was called
            request_data: The anonymized request data
            response_time_ms: The response time in milliseconds
            status_code: The HTTP status code
            rate_limited: Whether the request was rate limited

        Returns:
            APIMetric object representing the logged metric
        """
        try:
            # Create new API metric record
            api_metric = APIMetric(
                session_token=session_token,
                endpoint=endpoint,
                request_data=request_data,
                response_time_ms=response_time_ms,
                status_code=status_code,
                rate_limited=rate_limited
            )

            # Add to database
            self.db_session.add(api_metric)
            await self.db_session.commit()
            await self.db_session.refresh(api_metric)

            self.logger.info(f"Logged API call: {endpoint} for session {session_token[:10]}...")

            return api_metric

        except Exception as e:
            self.logger.error(f"Error logging API call: {e}")
            # Don't raise the exception as logging shouldn't affect the main API call
            return None

    async def get_session_metrics(
        self,
        session_token: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[APIMetric]:
        """
        Get API metrics for a specific session.

        Args:
            session_token: The session token to get metrics for
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            List of APIMetric objects
        """
        try:
            result = await self.db_session.execute(
                select(APIMetric)
                .where(APIMetric.session_token == session_token)
                .order_by(APIMetric.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            metrics = result.scalars().all()

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting session metrics: {e}")
            return []

    async def get_endpoint_metrics(
        self,
        endpoint: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[APIMetric]:
        """
        Get API metrics for a specific endpoint.

        Args:
            endpoint: The endpoint to get metrics for
            limit: Maximum number of records to return
            offset: Offset for pagination

        Returns:
            List of APIMetric objects
        """
        try:
            result = await self.db_session.execute(
                select(APIMetric)
                .where(APIMetric.endpoint == endpoint)
                .order_by(APIMetric.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            metrics = result.scalars().all()

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting endpoint metrics: {e}")
            return []

    async def get_rate_limited_calls_count(self, session_token: str) -> int:
        """
        Get the count of rate limited calls for a session.

        Args:
            session_token: The session token to check

        Returns:
            Number of rate limited calls
        """
        try:
            result = await self.db_session.execute(
                select(APIMetric)
                .where(
                    APIMetric.session_token == session_token,
                    APIMetric.rate_limited == True
                )
            )
            metrics = result.scalars().all()

            return len(metrics)

        except Exception as e:
            self.logger.error(f"Error getting rate limited calls count: {e}")
            return 0

    async def get_average_response_time(self, endpoint: str) -> Optional[float]:
        """
        Get the average response time for an endpoint.

        Args:
            endpoint: The endpoint to calculate average for

        Returns:
            Average response time in milliseconds, or None if no data
        """
        try:
            from sqlalchemy import func

            result = await self.db_session.execute(
                select(func.avg(APIMetric.response_time_ms))
                .where(
                    APIMetric.endpoint == endpoint,
                    APIMetric.response_time_ms.isnot(None)
                )
            )
            avg_time = result.scalar()

            return avg_time

        except Exception as e:
            self.logger.error(f"Error getting average response time: {e}")
            return None

    async def cleanup_old_metrics(self, days_old: int = 30) -> int:
        """
        Remove metrics older than the specified number of days.

        Args:
            days_old: Number of days to keep metrics for

        Returns:
            Number of metrics deleted
        """
        try:
            from sqlalchemy import and_
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            result = await self.db_session.execute(
                select(APIMetric)
                .where(APIMetric.created_at < cutoff_date)
            )
            old_metrics = result.scalars().all()

            for metric in old_metrics:
                await self.db_session.delete(metric)

            await self.db_session.commit()

            self.logger.info(f"Cleaned up {len(old_metrics)} old metrics")

            return len(old_metrics)

        except Exception as e:
            self.logger.error(f"Error cleaning up old metrics: {e}")
            return 0