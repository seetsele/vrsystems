"""
Verity Analytics Backend Module
Collects, processes, and stores analytics events from web and mobile clients
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import logging
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalyticsEvent:
    """Single analytics event"""
    event: str
    properties: Dict[str, Any]
    session_id: str
    user_id: str
    timestamp: str
    received_at: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SessionData:
    """Aggregated session data"""
    session_id: str
    user_id: str
    start_time: str
    end_time: Optional[str]
    page_views: int
    events: int
    verifications: int
    duration_seconds: int
    pages_visited: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AnalyticsStore:
    """In-memory analytics storage with persistence"""
    
    def __init__(self, max_events: int = 100000):
        self.events: List[AnalyticsEvent] = []
        self.sessions: Dict[str, SessionData] = {}
        self.max_events = max_events
        self.metrics: Dict[str, Any] = defaultdict(int)
        
    def add_event(self, event: AnalyticsEvent):
        """Add event and update aggregates"""
        self.events.append(event)
        
        # Trim if needed
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
            
        # Update session data
        self._update_session(event)
        
        # Update metrics
        self._update_metrics(event)
        
    def _update_session(self, event: AnalyticsEvent):
        """Update session aggregates"""
        session_id = event.session_id
        
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionData(
                session_id=session_id,
                user_id=event.user_id,
                start_time=event.timestamp,
                end_time=event.timestamp,
                page_views=0,
                events=0,
                verifications=0,
                duration_seconds=0,
                pages_visited=[]
            )
            
        session = self.sessions[session_id]
        session.events += 1
        session.end_time = event.timestamp
        
        if event.event == 'page_view':
            session.page_views += 1
            page = event.properties.get('page', '/')
            if page not in session.pages_visited:
                session.pages_visited.append(page)
                
        if event.event == 'verification_complete':
            session.verifications += 1
            
        # Calculate duration
        try:
            start = datetime.fromisoformat(session.start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(session.end_time.replace('Z', '+00:00'))
            session.duration_seconds = int((end - start).total_seconds())
        except:
            pass
            
    def _update_metrics(self, event: AnalyticsEvent):
        """Update global metrics"""
        self.metrics['total_events'] += 1
        self.metrics[f'event_{event.event}'] += 1
        
        if event.event == 'verification_complete':
            verdict = event.properties.get('verdict', 'unknown')
            self.metrics[f'verdict_{verdict}'] += 1
            
    def get_events(
        self,
        event_type: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Query events with filters"""
        filtered = self.events
        
        if event_type:
            filtered = [e for e in filtered if e.event == event_type]
            
        if session_id:
            filtered = [e for e in filtered if e.session_id == session_id]
            
        if user_id:
            filtered = [e for e in filtered if e.user_id == user_id]
            
        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]
            
        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]
            
        return [e.to_dict() for e in filtered[-limit:]]
        
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        if session_id in self.sessions:
            return self.sessions[session_id].to_dict()
        return None
        
    def get_metrics(self) -> Dict:
        """Get aggregated metrics"""
        return dict(self.metrics)


class AnalyticsProcessor:
    """Process and analyze analytics data"""
    
    def __init__(self, store: AnalyticsStore):
        self.store = store
        
    def get_dashboard_stats(self, days: int = 7) -> Dict:
        """Get dashboard statistics"""
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        recent_events = [
            e for e in self.store.events 
            if e.timestamp >= cutoff
        ]
        
        # Calculate stats
        verifications = [e for e in recent_events if e.event == 'verification_complete']
        page_views = [e for e in recent_events if e.event == 'page_view']
        errors = [e for e in recent_events if e.event == 'error']
        
        # Verdict distribution
        verdicts = defaultdict(int)
        for v in verifications:
            verdict = v.properties.get('verdict', 'unknown')
            verdicts[verdict] += 1
            
        # Daily breakdown
        daily = defaultdict(lambda: {'verifications': 0, 'page_views': 0, 'users': set()})
        for e in recent_events:
            try:
                day = e.timestamp[:10]
                daily[day]['users'].add(e.user_id)
                if e.event == 'verification_complete':
                    daily[day]['verifications'] += 1
                elif e.event == 'page_view':
                    daily[day]['page_views'] += 1
            except:
                pass
                
        # Convert daily to serializable format
        daily_stats = {
            day: {
                'verifications': data['verifications'],
                'page_views': data['page_views'],
                'unique_users': len(data['users'])
            }
            for day, data in daily.items()
        }
        
        # Top pages
        page_counts = defaultdict(int)
        for pv in page_views:
            page = pv.properties.get('page', '/')
            page_counts[page] += 1
        top_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'period_days': days,
            'total_verifications': len(verifications),
            'total_page_views': len(page_views),
            'total_errors': len(errors),
            'unique_sessions': len(set(e.session_id for e in recent_events)),
            'unique_users': len(set(e.user_id for e in recent_events)),
            'verdict_distribution': dict(verdicts),
            'daily_stats': daily_stats,
            'top_pages': [{'page': p, 'views': c} for p, c in top_pages],
            'avg_confidence': self._calculate_avg_confidence(verifications),
            'avg_verification_time': self._calculate_avg_duration(verifications)
        }
        
    def _calculate_avg_confidence(self, verifications: List[AnalyticsEvent]) -> float:
        """Calculate average confidence score"""
        confidences = [
            v.properties.get('confidence', 0) 
            for v in verifications
        ]
        return round(sum(confidences) / len(confidences), 2) if confidences else 0
        
    def _calculate_avg_duration(self, verifications: List[AnalyticsEvent]) -> float:
        """Calculate average verification duration"""
        durations = [
            v.properties.get('duration', 0) 
            for v in verifications
        ]
        return round(sum(durations) / len(durations), 2) if durations else 0
        
    def get_funnel_analysis(self) -> Dict:
        """Analyze user conversion funnel"""
        # Define funnel stages
        stages = [
            ('page_view', 'Visited'),
            ('verification_started', 'Started Verification'),
            ('verification_complete', 'Completed Verification'),
            ('signup', 'Signed Up'),
            ('plan_upgrade', 'Upgraded Plan')
        ]
        
        # Count users at each stage
        user_stages = defaultdict(set)
        for event in self.store.events:
            for stage_event, _ in stages:
                if event.event == stage_event:
                    user_stages[stage_event].add(event.user_id)
                    
        funnel = []
        prev_count = None
        for stage_event, stage_name in stages:
            count = len(user_stages[stage_event])
            conversion = round((count / prev_count * 100), 1) if prev_count and prev_count > 0 else 100
            funnel.append({
                'stage': stage_name,
                'event': stage_event,
                'users': count,
                'conversion_rate': conversion
            })
            prev_count = count if count > 0 else prev_count
            
        return {'funnel': funnel}
        
    def get_user_journey(self, user_id: str) -> Dict:
        """Get user's event journey"""
        user_events = [
            e for e in self.store.events 
            if e.user_id == user_id
        ]
        
        # Sort by timestamp
        user_events.sort(key=lambda x: x.timestamp)
        
        return {
            'user_id': user_id,
            'total_events': len(user_events),
            'first_seen': user_events[0].timestamp if user_events else None,
            'last_seen': user_events[-1].timestamp if user_events else None,
            'events': [
                {
                    'event': e.event,
                    'timestamp': e.timestamp,
                    'page': e.properties.get('page'),
                }
                for e in user_events[-100:]  # Last 100 events
            ]
        }


# Global instances
analytics_store = AnalyticsStore()
analytics_processor = AnalyticsProcessor(analytics_store)


def process_analytics_batch(batch: Dict) -> Dict:
    """Process incoming analytics batch from client"""
    received_at = datetime.utcnow().isoformat()
    events = batch.get('events', [])
    metadata = batch.get('metadata', {})
    
    processed = 0
    errors = 0
    
    for event_data in events:
        try:
            event = AnalyticsEvent(
                event=event_data.get('event', 'unknown'),
                properties=event_data.get('properties', {}),
                session_id=event_data.get('properties', {}).get('sessionId', metadata.get('sessionId', '')),
                user_id=event_data.get('properties', {}).get('userId', metadata.get('userId', '')),
                timestamp=event_data.get('properties', {}).get('timestamp', received_at),
                received_at=received_at
            )
            analytics_store.add_event(event)
            processed += 1
        except Exception as e:
            logger.error(f"Failed to process event: {e}")
            errors += 1
            
    return {
        'success': True,
        'processed': processed,
        'errors': errors,
        'received_at': received_at
    }


def get_analytics_dashboard(days: int = 7) -> Dict:
    """Get analytics dashboard data"""
    return analytics_processor.get_dashboard_stats(days)


def get_funnel() -> Dict:
    """Get conversion funnel analysis"""
    return analytics_processor.get_funnel_analysis()


def get_user_analytics(user_id: str) -> Dict:
    """Get analytics for specific user"""
    return analytics_processor.get_user_journey(user_id)


# FastAPI routes (add to main API server)
"""
from analytics_backend import process_analytics_batch, get_analytics_dashboard, get_funnel

@app.post("/api/v1/analytics")
async def receive_analytics(batch: dict):
    return process_analytics_batch(batch)

@app.get("/api/v1/analytics/dashboard")
async def analytics_dashboard(days: int = 7):
    return get_analytics_dashboard(days)

@app.get("/api/v1/analytics/funnel")
async def analytics_funnel():
    return get_funnel()
"""
