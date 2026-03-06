"""
Gestor de estados de conversación (State Machine)
Maneja transiciones entre BOT_MENU, COLLECTING_DATA, WAITING_AGENT, IN_AGENT, etc.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import ConversationState, AgentAssignment, User
from schemas import ConversationStateResponse, StartHandoffRequest, CloseHandoffRequest
import json
import uuid
import logging

logger = logging.getLogger(__name__)

# Estados válidos
STATES = {
    "BOT_MENU": "El bot guía con menús",
    "COLLECTING_DATA": "El bot recopila datos",
    "WAITING_AGENT": "Esperando asignación a operador",
    "IN_AGENT": "En conversación con operador",
    "CLOSED": "Ticket cerrado, vuelve a bot",
    "BLACKLISTED": "Número en lista negra"
}


class ConversationManager:
    """Gestor de estados de conversación"""
    
    @staticmethod
    def get_or_create_conversation(
        db: Session,
        phone_number: str,
        initial_state: str = "BOT_MENU"
    ) -> ConversationState:
        """Obtiene o crea una conversación para un número"""
        conv = db.query(ConversationState).filter(
            ConversationState.phone_number == phone_number
        ).first()
        
        if not conv:
            conv = ConversationState(
                phone_number=phone_number,
                current_state=initial_state,
                last_message_at=datetime.utcnow()
            )
            db.add(conv)
            db.commit()
            db.refresh(conv)
            logger.info(f"Conversación creada: {phone_number} (estado: {initial_state})")
        
        return conv
    
    @staticmethod
    @staticmethod
    def get_conversation(db: Session, phone_number: str) -> ConversationState:
        """Obtiene una conversación existente (SIEMPRE fresca de la BD)"""
        # Hacer query fresca sin usar caché de sesión
        conv = db.query(ConversationState).filter(
            ConversationState.phone_number == phone_number
        ).first()
        
        # Si existe, refrescar desde la BD para obtener datos actualizados
        if conv:
            db.refresh(conv)
        
        return conv
    
    @staticmethod
    def update_last_message_time(db: Session, phone_number: str):
        """Actualiza el timestamp del último mensaje"""
        conv = ConversationManager.get_conversation(db, phone_number)
        if conv:
            conv.last_message_at = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def change_state(
        db: Session,
        phone_number: str,
        new_state: str,
        metadata: dict = None
    ) -> ConversationState:
        """Cambia el estado de una conversación"""
        if new_state not in STATES:
            raise ValueError(f"Estado inválido: {new_state}")
        
        conv = ConversationManager.get_or_create_conversation(db, phone_number)
        old_state = conv.current_state
        
        conv.current_state = new_state
        conv.last_message_at = datetime.utcnow()
        
        if metadata:
            conv.extra_data = json.dumps(metadata)
        
        db.commit()
        db.refresh(conv)
        
        logger.info(f"Estado cambiado: {phone_number} ({old_state} → {new_state})")
        return conv
    
    @staticmethod
    def is_handoff_active(db: Session, phone_number: str) -> bool:
        """Verifica si hay handoff activo para un número"""
        conv = ConversationManager.get_conversation(db, phone_number)
        if not conv:
            return False
        
        # Si está en lista negra, no hay chatbot
        if conv.current_state == "BLACKLISTED":
            return True  # Tratar como "no responder normalmente"
        
        # Handoff activo si está esperando operario o el operario está respondiendo
        return conv.handoff_active and conv.current_state in ["WAITING_AGENT", "IN_AGENT"]
    
    @staticmethod
    def start_handoff(
        db: Session,
        request: StartHandoffRequest
    ) -> ConversationState:
        """Inicia un handoff (modo humano por 12 horas)"""
        from datetime import timedelta
        
        phone_number = request.phone_number
        conv = ConversationManager.get_or_create_conversation(db, phone_number)
        
        # Generar ticket
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"
        
        # Actualizar conversación
        # HUMAN_MODE: modo operador por 12 horas
        conv.human_mode = True
        conv.human_mode_expire = datetime.utcnow() + timedelta(hours=12)
        conv.current_state = "WAITING_AGENT"
        conv.handoff_active = True
        conv.handoff_started_at = datetime.utcnow()
        conv.ticket_id = ticket_id
        
        if request.collected_data:
            conv.collected_data = json.dumps(request.collected_data)
        
        if request.agent_id:
            conv.assigned_agent_id = request.agent_id
        
        if request.agent_name:
            conv.assigned_agent_name = request.agent_name
        
        conv.last_message_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conv)
        
        print(f"[HANDOFF] Iniciado para {phone_number}: ticket={ticket_id}, human_mode=True, expire={conv.human_mode_expire}")
        logger.info(f"Handoff iniciado: {phone_number} (ticket: {ticket_id})")
        return conv
    
    @staticmethod
    def assign_agent(
        db: Session,
        phone_number: str,
        agent_id: int,
        agent_name: str
    ) -> ConversationState:
        """Asigna un operario a una conversación en handoff"""
        conv = ConversationManager.get_or_create_conversation(db, phone_number)
        
        if not conv.handoff_active:
            raise ValueError(f"No hay handoff activo para {phone_number}")
        
        conv.assigned_agent_id = agent_id
        conv.assigned_agent_name = agent_name
        conv.current_state = "IN_AGENT"
        conv.last_message_at = datetime.utcnow()
        
        # Crear assignment
        assignment = AgentAssignment(
            conversation_id=conv.id,
            agent_id=agent_id,
            phone_number=phone_number,
            ticket_id=conv.ticket_id or f"TKT-{uuid.uuid4().hex[:8].upper()}",
            status="IN_PROGRESS",
            started_at=datetime.utcnow()
        )
        db.add(assignment)
        db.commit()
        db.refresh(conv)
        
        logger.info(f"Operario asignado: {phone_number} → {agent_name} (ID: {agent_id})")
        return conv
    
    @staticmethod
    def close_handoff(
        db: Session,
        phone_number: str,
        request: CloseHandoffRequest = None
    ) -> ConversationState:
        """Cierra un handoff y vuelve a estado BOT_MENU o CLOSED"""
        conv = ConversationManager.get_or_create_conversation(db, phone_number)
        
        # Actualizar estado
        conv.current_state = "CLOSED"
        conv.handoff_active = False
        conv.closed_at = datetime.utcnow()
        
        if request:
            if request.notes:
                convMetadata = json.loads(conv.extra_data) if conv.extra_data else {}
                convMetadata["close_notes"] = request.notes
                conv.extra_data = json.dumps(convMetadata)
        
        # Cerrar assignment si existe
        assignment = db.query(AgentAssignment).filter(
            AgentAssignment.phone_number == phone_number,
            AgentAssignment.status == "IN_PROGRESS"
        ).first()
        
        if assignment:
            assignment.status = "CLOSED"
            assignment.closed_at = datetime.utcnow()
            if request and request.resolution:
                assignment.resolution = request.resolution
        
        conv.last_message_at = datetime.utcnow()
        db.commit()
        db.refresh(conv)
        
        logger.info(f"Handoff cerrado: {phone_number}")
        return conv
    
    @staticmethod
    def close_by_inactivity(
        db: Session,
        inactivity_minutes: int = 120  # 2 horas por defecto
    ) -> list:
        """Cierra conversaciones inactivas automáticamente"""
        threshold = datetime.utcnow() - timedelta(minutes=inactivity_minutes)
        
        conversations = db.query(ConversationState).filter(
            ConversationState.handoff_active == True,
            ConversationState.current_state.in_(["WAITING_AGENT", "IN_AGENT"]),
            ConversationState.last_message_at < threshold
        ).all()
        
        closed_numbers = []
        for conv in conversations:
            try:
                ConversationManager.close_handoff(db, conv.phone_number)
                closed_numbers.append(conv.phone_number)
                logger.info(f"Conversación cerrada por inactividad: {conv.phone_number}")
            except Exception as e:
                logger.error(f"Error cerrando por inactividad {conv.phone_number}: {e}")
        
        return closed_numbers
    
    @staticmethod
    def collect_data(
        db: Session,
        phone_number: str,
        key: str,
        value: str
    ) -> ConversationState:
        """Agrega datos recolectados a una conversación"""
        conv = ConversationManager.get_or_create_conversation(db, phone_number)
        
        # Parsear datos existentes
        collected = json.loads(conv.collected_data) if conv.collected_data else {}
        
        # Agregar nuevo dato
        collected[key] = value
        conv.collected_data = json.dumps(collected)
        conv.last_message_at = datetime.utcnow()
        
        db.commit()
        db.refresh(conv)
        
        return conv
    
    @staticmethod
    def set_blocked(
        db: Session,
        phone_number: str,
        reason: str
    ) -> ConversationState:
        """Marca una conversación como bloqueada"""
        conv = ConversationManager.get_or_create_conversation(db, phone_number)
        
        conv.current_state = "BLACKLISTED"
        conv.is_blocked = True
        conv.block_reason = reason
        conv.last_message_at = datetime.utcnow()
        
        # Si hay handoff activo, cerrarlo
        if conv.handoff_active:
            ConversationManager.close_handoff(db, phone_number)
        
        db.commit()
        db.refresh(conv)
        
        logger.warning(f"Conversación bloqueada: {phone_number} ({reason})")
        return conv
    
    @staticmethod
    def update_last_message(db: Session, phone_number: str) -> ConversationState:
        """Actualiza el timestamp del último mensaje recibido (para tracking de inactividad)"""
        conv = ConversationManager.get_conversation(db, phone_number)
        
        if conv:
            conv.last_message_at = datetime.utcnow()
            db.commit()
            db.refresh(conv)
            logger.debug(f"Última actividad actualizada: {phone_number}")
        
        return conv
    
    @staticmethod
    def reset_to_menu(db: Session, phone_number: str) -> ConversationState:
        """Resetea una conversación al menú principal"""
        conv = ConversationManager.change_state(db, phone_number, "BOT_MENU")
        conv.collected_data = None
        conv.handoff_active = False
        conv.assigned_agent_id = None
        conv.assigned_agent_name = None
        conv.ticket_id = None
        db.commit()
        db.refresh(conv)
        
        logger.info(f"Conversación reseteada al menú: {phone_number}")
        return conv
    
    @staticmethod
    def to_response(conv: ConversationState) -> ConversationStateResponse:
        """Convierte una conversación a schema de respuesta"""
        return ConversationStateResponse(
            id=conv.id,
            phone_number=conv.phone_number,
            current_state=conv.current_state,
            handoff_active=conv.handoff_active,
            assigned_agent_id=conv.assigned_agent_id,
            assigned_agent_name=conv.assigned_agent_name,
            ticket_id=conv.ticket_id,
            last_message_at=conv.last_message_at,
            handoff_started_at=conv.handoff_started_at,
            closed_at=conv.closed_at,
            is_blocked=conv.is_blocked
        )
    
    @staticmethod
    def should_skip_bot_menu(db: Session, phone_number: str) -> bool:
        """
        Filtro crítico: determina si se debe saltear la lógica de menú
        Retorna True si NO se debe ejecutar menú (handoff activo o bloqueado)
        """
        conv = ConversationManager.get_conversation(db, phone_number)
        
        if not conv:
            print(f"[SKIP_MENU] No existe conversación para {phone_number}")
            return False  # Si no existe, dejar que el bot lo maneje
        
        # Si está bloqueado, no mostrar menú
        if conv.current_state == "BLACKLISTED" or conv.is_blocked:
            print(f"[SKIP_MENU] {phone_number} está bloqueado")
            return True
        
        # Si hay handoff activo, no mostrar menú
        if conv.handoff_active and conv.current_state in ["WAITING_AGENT", "IN_AGENT"]:
            print(f"[SKIP_MENU] {phone_number} en handoff activo (handoff_active={conv.handoff_active}, state={conv.current_state})")
            return True
        
        print(f"[SKIP_MENU] {phone_number} - procesando menú normalmente (handoff_active={conv.handoff_active}, state={conv.current_state})")
        return False

    @staticmethod
    def is_in_human_mode(db: Session, phone_number: str) -> bool:
        """
        Chequea si el usuario está en modo humano (esperando operador).
        Automáticamente expira después de 12 horas.
        """
        conv = ConversationManager.get_conversation(db, phone_number)
        
        if not conv:
            return False
        
        # Si no está en human_mode, retornar False
        if not conv.human_mode:
            return False
        
        # Si human_mode_expire es None o ya pasó, volver a BOT_MODE
        if not conv.human_mode_expire:
            return False
        
        from datetime import datetime as dt
        now = dt.utcnow()
        
        # Si expiró, volver a BOT_MODE automáticamente
        if conv.human_mode_expire < now:
            print(f"[HUMAN_MODE] Expire para {phone_number} - volviendo a BOT_MODE")
            conv.human_mode = False
            conv.human_mode_expire = None
            db.commit()
            return False
        
        # Sigue en HUMAN_MODE
        print(f"[HUMAN_MODE] {phone_number} en modo humano (expire: {conv.human_mode_expire.strftime('%H:%M:%S')})")
        return True
    
    @staticmethod
    def exit_human_mode(db: Session, phone_number: str) -> ConversationState:
        """Salir del modo humano (opción 98)"""
        conv = ConversationManager.get_conversation(db, phone_number)
        
        if conv:
            conv.human_mode = False
            conv.human_mode_expire = None
            db.commit()
            db.refresh(conv)
            print(f"[HUMAN_MODE] {phone_number} salió del modo humano")
        
        return conv
