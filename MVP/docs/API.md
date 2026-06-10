# API do MVP

A API usa autenticação de sessão. O usuário precisa estar logado para consumir os endpoints.

## Sugerir agendamento com IA

`POST /api/ai/schedule`

### Payload

```json
{
  "service_id": 1,
  "start_date": "2026-04-20",
  "days": 7,
  "top_n": 6
}
```

### Resposta

```json
{
  "service": {"id": 1, "name": "Diagnóstico eletrônico"},
  "prediction": {
    "service_id": 1,
    "service_name": "Diagnóstico eletrônico",
    "predicted_minutes": 60,
    "confidence": 0.72,
    "source": "histórico de 5 OS recentes + estimativa cadastrada"
  },
  "suggestions": [
    {
      "start": "2026-04-20T08:00",
      "end": "2026-04-20T09:00",
      "date_label": "20/04/2026",
      "time_label": "08:00 - 09:00",
      "technician_id": 3,
      "technician_name": "Marcos Silva",
      "predicted_minutes": 60,
      "score": 124.1,
      "reason": "duração prevista: 60 min; carga do técnico no dia: 0 min; especialidade compatível com o serviço"
    }
  ]
}
```

## Listar veículos por cliente

`GET /api/vehicles/by-client/<client_id>`

### Resposta

```json
[
  {"id": 1, "label": "ABC1D23 - Volkswagen Golf TSI", "plate": "ABC1D23"}
]
```

## Sugerir reposição de estoque

`GET /api/ai/restock`

### Resposta

```json
{
  "suggestions": [
    {
      "product_id": 3,
      "product_name": "Aditivo de radiador",
      "current_quantity": 3,
      "min_quantity": 4,
      "suggested_purchase_quantity": 5,
      "reason": "estoque igual ou abaixo do mínimo cadastrado"
    }
  ]
}
```

## Verificar conflito de agenda

`POST /api/appointments/check-conflict`

### Payload

```json
{
  "technician_id": 3,
  "start": "2026-04-20T08:00",
  "end": "2026-04-20T09:00"
}
```

### Resposta

```json
{
  "has_conflict": false,
  "conflicts": []
}
```
