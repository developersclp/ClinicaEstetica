from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from database import get_db, get_brazil_time
from models.paciente import Paciente
from models.anamnese import Anamnese
from models.modelo_anamnese import ModeloAnamnese
from schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse, PacienteListResponse
from services.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])


@router.get("", response_model=List[PacienteListResponse])
def listar_pacientes(
    busca: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Paciente)
    if busca:
        query = query.filter(Paciente.nome.ilike(f"%{busca}%"))
    pacientes = query.order_by(Paciente.nome).all()

    # Pre-calculate warnings
    today = get_brazil_time().replace(hour=0, minute=0, second=0, microsecond=0)
    todas_finalizadas = db.query(Anamnese).join(ModeloAnamnese).filter(
        Anamnese.status == "finalizada",
        ModeloAnamnese.tempo_eficiencia.isnot(None),
        Anamnese.finalizada_at.isnot(None)
    ).all()

    pacientes_com_aviso = set()
    for a in todas_finalizadas:
        data_finalizada = a.finalizada_at.replace(hour=0, minute=0, second=0, microsecond=0)
        if data_finalizada.tzinfo:
            data_finalizada = data_finalizada.astimezone(today.tzinfo).replace(hour=0, minute=0, second=0, microsecond=0)
        diff_days = (today - data_finalizada).days
        dias_restantes = a.modelo.tempo_eficiencia - diff_days
        if -20 <= dias_restantes <= 5:
            pacientes_com_aviso.add(a.paciente_id)

    result = []
    for p in pacientes:
        total = db.query(func.count(Anamnese.id)).filter(Anamnese.paciente_id == p.id).scalar()
        result.append(PacienteListResponse(
            id=p.id,
            nome=p.nome,
            cpf=p.cpf,
            telefone=p.telefone,
            genero=p.genero,
            created_at=p.created_at,
            total_anamneses=total or 0,
            tem_aviso_eficiencia=(p.id in pacientes_com_aviso),
        ))
    return result


@router.post("", response_model=PacienteResponse)
def criar_paciente(
    paciente: PacienteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Paciente).filter(Paciente.cpf == paciente.cpf).first()
    if existing:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    db_paciente = Paciente(**paciente.model_dump())
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    return PacienteResponse(
        **{k: v for k, v in db_paciente.__dict__.items() if not k.startswith("_")},
        total_anamneses=0,
    )


@router.get("/{paciente_id}", response_model=PacienteResponse)
def obter_paciente(
    paciente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    total = db.query(func.count(Anamnese.id)).filter(Anamnese.paciente_id == paciente.id).scalar()
    return PacienteResponse(
        **{k: v for k, v in paciente.__dict__.items() if not k.startswith("_")},
        total_anamneses=total or 0,
    )


@router.put("/{paciente_id}", response_model=PacienteResponse)
def atualizar_paciente(
    paciente_id: int,
    data: PacienteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(paciente, key, value)
    db.commit()
    db.refresh(paciente)
    total = db.query(func.count(Anamnese.id)).filter(Anamnese.paciente_id == paciente.id).scalar()
    return PacienteResponse(
        **{k: v for k, v in paciente.__dict__.items() if not k.startswith("_")},
        total_anamneses=total or 0,
    )
