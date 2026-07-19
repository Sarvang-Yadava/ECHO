from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.models.digital_twin import Simulation
from app.schemas.twin import SimulationPrediction, SimulationRequest
from app.services.simulator import predict_scenario

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=SimulationPrediction)
def simulate(payload: SimulationRequest, current_user: CurrentUser, db: DbSession) -> SimulationPrediction:
    scenario = payload.model_dump(mode="json")
    prediction = predict_scenario(current_user, scenario)
    simulation = Simulation(user_id=current_user.id, scenario=scenario, prediction=prediction)
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    return SimulationPrediction(
        knowledge_score=float(prediction.get("knowledge_score", 0)),
        confidence=float(prediction.get("confidence", 0)),
        academic_health=float(prediction.get("academic_health", 0)),
        recommended_study_load=float(prediction.get("recommended_study_load", 0)),
        explanation=str(prediction.get("explanation", "")),
        model_version=str(prediction.get("model_version", "heuristic-v2")),
        expected_exam_score=float(prediction.get("expected_exam_score", 0)),
        memory_retention=float(prediction.get("memory_retention", 0)),
        stress=float(prediction.get("stress", 0)),
    )
