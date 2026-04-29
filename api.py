from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from reviewer import review_code

app = FastAPI(title="AI Code Reviewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class ReviewRequest(BaseModel):
    code: str
    language: str


@app.post("/api/review")
def review(req: ReviewRequest):
    try:
        result = review_code(req.code, req.language)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "reports": [
            {
                "agent_name": r.agent_name,
                "emoji": r.emoji,
                "summary": r.summary,
                "findings": [
                    {
                        "severity": f.severity,
                        "title": f.title,
                        "description": f.description,
                        "location": f.location,
                    }
                    for f in r.findings
                ],
            }
            for r in result.reports
        ],
        "coordinator": {
            "overall_health": result.coordinator.overall_health,
            "critical_issues": result.coordinator.critical_issues,
            "key_strengths": result.coordinator.key_strengths,
            "recommended_actions": result.coordinator.recommended_actions,
            "narrative": result.coordinator.narrative,
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}
