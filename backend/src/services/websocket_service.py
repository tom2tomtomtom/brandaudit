"""
WebSocket service for real-time progress updates during brand analysis
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import current_app


class ProgressTracker:
    """Track analysis progress with detailed stages and time estimation"""
    
    def __init__(self, analysis_id: str, total_stages: int = 8):
        self.analysis_id = analysis_id
        self.total_stages = total_stages
        self.current_stage = 0
        self.stage_progress = 0
        self.overall_progress = 0
        self.start_time = datetime.utcnow()
        self.stage_start_time = datetime.utcnow()
        self.estimated_completion = None
        self.current_step_name = ""
        self.current_substep = ""
        self.error_message = None
        self.status = "starting"
        
        # Define analysis stages with estimated durations (in seconds)
        self.stages = [
            {
                "id": "llm_analysis",
                "name": "Multi-Pass Strategic Analysis",
                "description": "GPT-4 generating comprehensive brand intelligence",
                "estimated_duration": 180,
                "substeps": [
                    "Executive Summary & Market Position",
                    "Competitive Intelligence Deep-Dive", 
                    "Strategic Challenges & Growth Opportunities",
                    "Cultural Position & Social Impact",
                    "Thought Starters & Strategic Provocations",
                    "Agency Partnership Opportunities",
                    "Strategic Recommendations"
                ]
            },
            {
                "id": "news_analysis",
                "name": "News & Market Intelligence",
                "description": "Gathering recent news and market sentiment",
                "estimated_duration": 20,
                "substeps": ["Fetching recent news", "Analyzing sentiment", "Processing market data"]
            },
            {
                "id": "brand_data",
                "name": "Brand Asset Discovery",
                "description": "Retrieving logos, colors, and brand assets",
                "estimated_duration": 15,
                "substeps": ["Searching brand database", "Fetching brand assets", "Processing visual data"]
            },
            {
                "id": "visual_analysis",
                "name": "Visual Brand Analysis",
                "description": "Capturing screenshots and analyzing visual identity",
                "estimated_duration": 45,
                "substeps": ["Capturing website screenshots", "Analyzing visual elements", "Extracting color palette"]
            },
            {
                "id": "competitor_analysis",
                "name": "Competitive Intelligence",
                "description": "Identifying and analyzing key competitors",
                "estimated_duration": 60,
                "substeps": ["Identifying competitors", "Analyzing competitor strategies", "Comparative analysis"]
            },
            {
                "id": "campaign_analysis",
                "name": "Campaign Discovery",
                "description": "Finding recent marketing campaigns and messaging",
                "estimated_duration": 30,
                "substeps": ["Searching for campaigns", "Analyzing messaging", "Extracting insights"]
            },
            {
                "id": "strategic_synthesis",
                "name": "Strategic Synthesis",
                "description": "Generating actionable recommendations",
                "estimated_duration": 30,
                "substeps": ["Synthesizing data", "Generating insights", "Creating recommendations"]
            },
            {
                "id": "presentation",
                "name": "Report Generation",
                "description": "Creating professional presentation slides",
                "estimated_duration": 20,
                "substeps": ["Formatting data", "Generating slides", "Finalizing report"]
            }
        ]
    
    def get_current_stage(self) -> Dict[str, Any]:
        """Get current stage information"""
        if self.current_stage >= len(self.stages):
            return self.stages[-1]
        return self.stages[self.current_stage]
    
    def calculate_overall_progress(self) -> int:
        """Calculate overall progress percentage"""
        if self.current_stage >= len(self.stages):
            return 100
        
        # Progress from completed stages
        completed_progress = (self.current_stage / len(self.stages)) * 100
        
        # Progress from current stage
        current_stage_weight = (1 / len(self.stages)) * 100
        current_stage_progress = (self.stage_progress / 100) * current_stage_weight
        
        return min(100, int(completed_progress + current_stage_progress))
    
    def estimate_time_remaining(self) -> Optional[int]:
        """Estimate time remaining in seconds"""
        if self.current_stage >= len(self.stages):
            return 0
        
        elapsed_time = (datetime.utcnow() - self.start_time).total_seconds()
        
        if self.overall_progress <= 0:
            # Use total estimated duration
            total_estimated = sum(stage["estimated_duration"] for stage in self.stages)
            return total_estimated
        
        # Calculate based on current progress
        estimated_total_time = elapsed_time / (self.overall_progress / 100)
        remaining_time = estimated_total_time - elapsed_time
        
        return max(0, int(remaining_time))
    
    def update_stage(self, stage_index: int, stage_progress: int = 0, substep: str = ""):
        """Update current stage and progress"""
        self.current_stage = stage_index
        self.stage_progress = stage_progress
        self.stage_start_time = datetime.utcnow()
        self.current_substep = substep
        
        current_stage = self.get_current_stage()
        self.current_step_name = current_stage["name"]
        self.overall_progress = self.calculate_overall_progress()
        
        if stage_index >= len(self.stages):
            self.status = "completed"
            self.overall_progress = 100
        else:
            self.status = "processing"
    
    def update_substep(self, substep: str, progress: int = None):
        """Update current substep"""
        self.current_substep = substep
        if progress is not None:
            self.stage_progress = progress
            self.overall_progress = self.calculate_overall_progress()
    
    def set_error(self, error_message: str):
        """Set error state"""
        self.error_message = error_message
        self.status = "error"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        current_stage = self.get_current_stage()
        time_remaining = self.estimate_time_remaining()
        
        return {
            "analysis_id": self.analysis_id,
            "status": self.status,
            "overall_progress": self.overall_progress,
            "current_stage": self.current_stage,
            "stage_progress": self.stage_progress,
            "current_step_name": self.current_step_name,
            "current_substep": self.current_substep,
            "current_stage_info": current_stage,
            "time_remaining": time_remaining,
            "estimated_completion": (datetime.utcnow() + timedelta(seconds=time_remaining)).isoformat() if time_remaining else None,
            "error_message": self.error_message,
            "elapsed_time": int((datetime.utcnow() - self.start_time).total_seconds()),
            "stages": self.stages
        }


class WebSocketService:
    """Service for managing WebSocket connections and progress updates"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.progress_trackers: Dict[str, ProgressTracker] = {}
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        """Setup WebSocket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            try:
                current_app.logger.info(f"Client connected")
            except RuntimeError:
                print("🔌 Client connected")
            emit('connected', {'status': 'Connected to analysis server'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            try:
                current_app.logger.info(f"Client disconnected")
            except RuntimeError:
                print("🔌 Client disconnected")

        @self.socketio.on('join_analysis')
        def handle_join_analysis(data):
            analysis_id = data.get('analysis_id')
            if analysis_id:
                join_room(analysis_id)
                try:
                    current_app.logger.info(f"Client joined analysis room: {analysis_id}")
                except RuntimeError:
                    print(f"🏠 Client joined analysis room: {analysis_id}")

                # Send current progress if tracker exists
                if analysis_id in self.progress_trackers:
                    tracker = self.progress_trackers[analysis_id]
                    emit('progress_update', tracker.to_dict())

        @self.socketio.on('leave_analysis')
        def handle_leave_analysis(data):
            analysis_id = data.get('analysis_id')
            if analysis_id:
                leave_room(analysis_id)
                try:
                    current_app.logger.info(f"Client left analysis room: {analysis_id}")
                except RuntimeError:
                    print(f"🚪 Client left analysis room: {analysis_id}")
    
    def create_progress_tracker(self, analysis_id: str) -> ProgressTracker:
        """Create a new progress tracker for an analysis"""
        tracker = ProgressTracker(analysis_id)
        self.progress_trackers[analysis_id] = tracker
        return tracker
    
    def get_progress_tracker(self, analysis_id: str) -> Optional[ProgressTracker]:
        """Get existing progress tracker"""
        return self.progress_trackers.get(analysis_id)
    
    def emit_progress_update(self, analysis_id: str, tracker: ProgressTracker = None):
        """Emit progress update to all clients in the analysis room"""
        if not tracker:
            tracker = self.progress_trackers.get(analysis_id)

        if tracker:
            progress_data = tracker.to_dict()
            self.socketio.emit('progress_update', progress_data, room=analysis_id)
            try:
                current_app.logger.info(f"Progress update sent for {analysis_id}: {tracker.overall_progress}%")
            except RuntimeError:
                # Working outside of application context - use print instead
                print(f"🔌 Progress update sent for {analysis_id}: {tracker.overall_progress}%")
    
    def emit_stage_update(self, analysis_id: str, stage_index: int, stage_progress: int = 0, substep: str = ""):
        """Update stage and emit progress"""
        tracker = self.progress_trackers.get(analysis_id)
        if tracker:
            tracker.update_stage(stage_index, stage_progress, substep)
            self.emit_progress_update(analysis_id, tracker)
    
    def emit_substep_update(self, analysis_id: str, substep: str, progress: int = None):
        """Update substep and emit progress"""
        tracker = self.progress_trackers.get(analysis_id)
        if tracker:
            tracker.update_substep(substep, progress)
            self.emit_progress_update(analysis_id, tracker)
    
    def emit_error(self, analysis_id: str, error_message: str):
        """Emit error state"""
        tracker = self.progress_trackers.get(analysis_id)
        if tracker:
            tracker.set_error(error_message)
            self.emit_progress_update(analysis_id, tracker)
    
    def emit_completion(self, analysis_id: str):
        """Emit completion state"""
        tracker = self.progress_trackers.get(analysis_id)
        if tracker:
            tracker.update_stage(len(tracker.stages), 100, "Analysis Complete!")
            self.emit_progress_update(analysis_id, tracker)
            
            # Clean up tracker after a delay
            def cleanup():
                time.sleep(60)  # Keep for 1 minute after completion
                if analysis_id in self.progress_trackers:
                    del self.progress_trackers[analysis_id]
            
            import threading
            cleanup_thread = threading.Thread(target=cleanup)
            cleanup_thread.daemon = True
            cleanup_thread.start()


# Global WebSocket service instance
websocket_service: Optional[WebSocketService] = None


def init_websocket_service(socketio: SocketIO) -> WebSocketService:
    """Initialize the WebSocket service"""
    global websocket_service
    websocket_service = WebSocketService(socketio)
    return websocket_service


def get_websocket_service() -> Optional[WebSocketService]:
    """Get the global WebSocket service instance"""
    return websocket_service
