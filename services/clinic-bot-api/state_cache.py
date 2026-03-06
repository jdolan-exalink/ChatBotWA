#!/usr/bin/env python3
"""
State Cache - Caché eficiente de estados de conversación
Proporciona caché de corta duración para ConversationState de BD
"""
import time
import logging
from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
from models import ConversationState
from conversation_manager import ConversationManager

logger = logging.getLogger(__name__)


class ConversationStateCache:
    """
    Caché de estados de conversación con TTL (Time To Live).
    
    Beneficios:
    - Reduce carga en BD para chats muy activos
    - Previene memory leaks (TTL automático)
    - Siempre garantiza datos frescos después de TTL
    
    TTL por defecto: 300 segundos (5 minutos)
    """
    
    def __init__(self, max_ttl_sec: int = 300):
        """
        Inicializa el caché.
        
        Args:
            max_ttl_sec: Segundos máximos que una entrada permanece en caché
        """
        self._cache: Dict[str, Tuple[ConversationState, float]] = {}
        self._max_ttl = max_ttl_sec
        self._stats = {"hits": 0, "misses": 0, "invalidations": 0}
        logger.info(f"[STATE_CACHE] Inicializado con TTL={max_ttl_sec}s")
    
    def get(self, db: Session, phone_number: str) -> Optional[ConversationState]:
        """
        Obtiene estado de conversación del caché o de BD.
        
        Estrategia:
        1. Si está en caché y NO expiró (< TTL) → retornar caché
        2. Si expiró o no existe → traer de BD y actualizar caché
        
        Args:
            db: Session de SQLAlchemy
            phone_number: Número de teléfono (+5493424123456@c.us)
        
        Returns:
            ConversationState o None si no existe
        """
        now = time.time()
        
        # Chequear caché
        if phone_number in self._cache:
            conv, cached_at = self._cache[phone_number]
            age = now - cached_at
            
            if age < self._max_ttl:
                # ✅ Caché aún válido
                self._stats["hits"] += 1
                age_ms = int(age * 1000)
                logger.debug(f"[STATE_CACHE] HIT {phone_number} (edad: {age_ms}ms)")
                return conv
            else:
                # ⚠️ Caché expirado, limpiar
                del self._cache[phone_number]
                logger.debug(f"[STATE_CACHE] Caché expirado para {phone_number} (>{self._max_ttl}s)")
        
        # ❌ No en caché, traer de BD
        self._stats["misses"] += 1
        conv = ConversationManager.get_conversation(db, phone_number)
        
        if conv:
            # Actualizar caché
            self._cache[phone_number] = (conv, now)
            logger.debug(f"[STATE_CACHE] MISS {phone_number} - Traído de BD")
        else:
            logger.debug(f"[STATE_CACHE] {phone_number} no existe en BD")
        
        return conv
    
    def invalidate(self, phone_number: str):
        """
        Marca una entrada como inválida (sin validar desde BD).
        
        Usar cuando se hace cambio en BD y queremos asegurar
        que la próxima lectura trae datos frescos.
        
        Args:
            phone_number: Número de teléfono
        """
        if phone_number in self._cache:
            del self._cache[phone_number]
            self._stats["invalidations"] += 1
            logger.info(f"[STATE_CACHE] Invalidado: {phone_number}")
    
    def cleanup_expired(self) -> int:
        """
        Limpia entradas expiradas del caché.
        
        Ejecutar periódicamente (e.g., cada 5 minutos) para
        evitar memory leaks si hay muchos chats únicos.
        
        Returns:
            Cantidad de entradas eliminadas
        """
        now = time.time()
        expired_keys = [
            k for k, (_, cached_at) in self._cache.items()
            if now - cached_at > self._max_ttl
        ]
        
        for k in expired_keys:
            del self._cache[k]
        
        if expired_keys:
            logger.info(f"[STATE_CACHE] Limpieza: {len(expired_keys)} entradas expiradas eliminadas")
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Retorna cantidad de entradas en caché"""
        return len(self._cache)
    
    def stats(self) -> dict:
        """Retorna estadísticas de caché (hits, misses, invalidations)"""
        return self._stats.copy()
    
    def reset_stats(self):
        """Resetea estadísticas"""
        self._stats = {"hits": 0, "misses": 0, "invalidations": 0}
    
    def __repr__(self) -> str:
        """Representación en strings"""
        stats = self.stats()
        total = stats["hits"] + stats["misses"]
        hit_rate = 100 * stats["hits"] / total if total > 0 else 0
        return (
            f"StateCache(size={self.size()}, "
            f"hits={stats['hits']}, "
            f"misses={stats['misses']}, "
            f"hit_rate={hit_rate:.1f}%, "
            f"invalidations={stats['invalidations']})"
        )


# Instancia global del caché (se inicializa en app.py)
_state_cache: Optional[ConversationStateCache] = None


def get_state_cache() -> ConversationStateCache:
    """Obtiene instancia global del caché"""
    global _state_cache
    if not _state_cache:
        _state_cache = ConversationStateCache(max_ttl_sec=300)
    return _state_cache


def init_state_cache(max_ttl_sec: int = 300):
    """Inicializa caché global"""
    global _state_cache
    _state_cache = ConversationStateCache(max_ttl_sec=max_ttl_sec)
    logger.info(f"[STATE_CACHE] Sistema de caché inicializado (TTL={max_ttl_sec}s)")
