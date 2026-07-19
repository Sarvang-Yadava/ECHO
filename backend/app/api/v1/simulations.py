from fastapi import APIRouter, status
from app.api.deps import CurrentUser, DbSession
from app.models.digital_twin import Simulation
from app.schemas.twin import SimulationCreate, SimulationResponse
from app.services.simulator import predict_scenario

router = APIRouter(prefix="/simulations", tags=["simulations"])


@router.post("", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
def create_simulation(payload: SimulationCreate, current_user: CurrentUser, db: DbSession) -> Simulation:
    simulation = Simulation(user_id=current_user.id, scenario=payload.scenario, prediction=predict_scenario(current_user, payload.scenario))
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    return simulation
