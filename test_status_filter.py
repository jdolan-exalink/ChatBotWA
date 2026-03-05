#!/usr/bin/env python3
"""
Test para verificar que los filtros de estado/broadcast funcionan correctamente
"""

import json

def test_webhook_filters():
    """
    Test de los filtros de estado/broadcast sin necesidad de base de datos
    """
    
    # Simulamos el código del webhook para probar los filtros
    test_cases = [
        {
            "name": "Mensaje normal en chat privado",
            "data": {
                "from": "551199999999@c.us",
                "body": "Hola",
                "fromMe": False
            },
            "should_ignore": False,
            "reason": "Debe procesar mensaje normal"
        },
        {
            "name": "Mensaje propio (fromMe=True)",
            "data": {
                "from": "551199999999@c.us",
                "body": "Respuesta del bot",
                "fromMe": True
            },
            "should_ignore": True,
            "reason": "Debe ignorar mensajes propios"
        },
        {
            "name": "Mensaje en estado de WhatsApp (status@broadcast)",
            "data": {
                "from": "status@broadcast",
                "body": "Texto en estado",
                "fromMe": False
            },
            "should_ignore": True,
            "reason": "Debe ignorar estados de broadcast"
        },
        {
            "name": "Mensaje en estado (status@ pattern)",
            "data": {
                "from": "554733333333@status",
                "body": "Otro estado",
                "fromMe": False
            },
            "should_ignore": True,
            "reason": "Debe ignorar patrones status@"
        },
        {
            "name": "Mensaje con texto 'estado'",
            "data": {
                "from": "551199999999@c.us",
                "body": "estado",
                "fromMe": False
            },
            "should_ignore": True,
            "reason": "Debe ignorar texto 'estado'"
        },
        {
            "name": "Mensaje con texto 'ESTADOS'",
            "data": {
                "from": "551199999999@c.us",
                "body": "ESTADOS",
                "fromMe": False
            },
            "should_ignore": True,
            "reason": "Debe ignorar texto 'estados' (case insensitive)"
        },
        {
            "name": "Mensaje con texto 'status'",
            "data": {
                "from": "551199999999@c.us",
                "body": "status",
                "fromMe": False
            },
            "should_ignore": True,
            "reason": "Debe ignorar texto 'status'"
        },
        {
            "name": "Mensaje normal que contiene palabra 'estado'",
            "data": {
                "from": "551199999999@c.us",
                "body": "¿Cuál es el estado del consultorio?",
                "fromMe": False
            },
            "should_ignore": False,
            "reason": "Debe procesar mensaje que CONTIENE 'estado' pero no ES exactamente 'estado'"
        },
        {
            "name": "Grupo de WhatsApp",
            "data": {
                "from": "551199999999-1234567890@g.us",
                "body": "Hola grupo",
                "fromMe": False
            },
            "should_ignore": True,
            "reason": "Debe ignorar mensajes de grupo (@g.us)"
        },
    ]
    
    results = []
    passed = 0
    failed = 0
    
    for test in test_cases:
        msg = test["data"]
        chat_id = msg.get("from")
        text = msg.get("body")
        
        # Aplicar los mismos filtros del webhook
        ignored = False
        filter_reason = None
        
        if msg.get("fromMe") is True:
            ignored = True
            filter_reason = "from_me"
        elif isinstance(chat_id, str) and ("status@" in chat_id or "@status" in chat_id or "broadcast" in chat_id):
            ignored = True
            filter_reason = "status_or_broadcast"
        elif isinstance(chat_id, str) and "@g.us" in chat_id:
            ignored = True
            filter_reason = "group_message"
        elif isinstance(text, str) and text.strip().lower() in {"estado", "estados", "status"}:
            ignored = True
            filter_reason = "status_text"
        
        # Verificar resultado
        expected = test["should_ignore"]
        passed_test = (ignored == expected)
        
        status = "✅ PASS" if passed_test else "❌ FAIL"
        if passed_test:
            passed += 1
        else:
            failed += 1
        
        result = {
            "test": test["name"],
            "status": status,
            "expected_ignore": expected,
            "actual_ignore": ignored,
            "filter_reason": filter_reason,
            "reason": test["reason"]
        }
        results.append(result)
        
        print(f"\n{status} - {test['name']}")
        print(f"   → {test['reason']}")
        print(f"   → Debe ignorarse: {expected}, Se ignoró: {ignored}")
        if filter_reason:
            print(f"   → Filtro aplicado: {filter_reason}")
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"RÉSUMEN: {passed} pasadas, {failed} fallidas de {len(test_cases)} tests")
    print(f"{'='*60}")
    
    return failed == 0  # Retorna True si todos pasaron

if __name__ == "__main__":
    success = test_webhook_filters()
    exit(0 if success else 1)
