from src.extensions import db, cache
from src.models.user_model import Analysis
from src.celery_app import celery
from datetime import datetime


@celery.task
def perform_analysis_task(analysis_id):
    # This is a dummy task. In a real application, this would perform
    # complex analysis, LLM calls, external API requests, etc.
    print(f"Starting analysis for ID: {analysis_id}")

    # Simulate work
    import time

    time.sleep(5)

    with celery.app.app_context():
        analysis = Analysis.query.get(analysis_id)
        if analysis:
            analysis.status = "completed"
            analysis.results = {"summary": "Dummy analysis completed successfully."}
            db.session.commit()
            print(f"Analysis {analysis_id} completed.")
        else:
            print(f"Analysis {analysis_id} not found.")


def start_analysis(analysis_data):
    # Create a new analysis record in the database
    new_analysis = Analysis(
        id=analysis_data["id"],
        user_id=analysis_data["user_id"],
        company_name=analysis_data["company_name"],
        website=analysis_data["website"],
        status="pending",
        progress=0,
        analysis_options=analysis_data.get("analysis_options", {}),
    )
    db.session.add(new_analysis)
    db.session.commit()

    # Dispatch the analysis task to Celery
    perform_analysis_task.delay(new_analysis.id)

    return new_analysis


@cache.cached(timeout=60)
def get_cached_data(key):
    print(f"Fetching data for key: {key} (from cache or fresh)")
    # Simulate a slow operation or external API call
    import time

    time.sleep(2)
    return {
        "data": f"This is cached data for {key}",
        "timestamp": datetime.utcnow().isoformat(),
    }
