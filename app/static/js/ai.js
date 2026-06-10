function byId(id) { return document.getElementById(id); }

async function refreshVehiclesByClient() {
  const clientSelect = byId('client_id');
  const vehicleSelect = byId('vehicle_id');
  if (!clientSelect || !vehicleSelect || !clientSelect.value) return;
  const current = vehicleSelect.dataset.current || vehicleSelect.value;
  try {
    const response = await fetch(`/api/vehicles/by-client/${clientSelect.value}`);
    if (!response.ok) return;
    const vehicles = await response.json();
    vehicleSelect.innerHTML = '<option value="">Selecione...</option>';
    vehicles.forEach((vehicle) => {
      const option = document.createElement('option');
      option.value = vehicle.id;
      option.textContent = vehicle.label;
      if (String(vehicle.id) === String(current)) option.selected = true;
      vehicleSelect.appendChild(option);
    });
  } catch (err) {
    console.warn('Não foi possível carregar veículos', err);
  }
}

function fillSuggestion(button) {
  const startInput = byId('scheduled_start');
  const techSelect = byId('technician_id');
  const durationInput = byId('duration_minutes');
  const scoreInput = byId('ai_score');
  const reasonInput = byId('ai_reason');
  if (startInput) startInput.value = button.dataset.start;
  if (techSelect) techSelect.value = button.dataset.technicianId;
  if (durationInput) durationInput.value = button.dataset.duration;
  if (scoreInput) scoreInput.value = button.dataset.score;
  if (reasonInput) reasonInput.value = button.dataset.reason;
  document.querySelectorAll('.ai-card').forEach((card) => card.style.outline = 'none');
  button.closest('.ai-card').style.outline = '2px solid var(--accent)';
}

async function suggestSchedule() {
  const serviceSelect = byId('service_id');
  const results = byId('aiResults');
  const startDate = byId('ai_start_date');
  if (!serviceSelect || !serviceSelect.value || !results) {
    alert('Selecione um serviço para usar a IA.');
    return;
  }
  results.innerHTML = '<div class="muted">Analisando histórico, agenda e técnicos...</div>';
  try {
    const response = await fetch('/api/ai/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_id: serviceSelect.value,
        start_date: startDate ? startDate.value : null,
        days: 7,
        top_n: 6
      })
    });
    const data = await response.json();
    if (!response.ok) {
      results.innerHTML = `<div class="flash danger">${data.error || 'Erro ao consultar IA.'}</div>`;
      return;
    }
    if (!data.suggestions.length) {
      results.innerHTML = '<div class="flash warning">Nenhuma janela disponível no período analisado.</div>';
      return;
    }
    const prediction = data.prediction;
    results.innerHTML = `
      <div class="flash success">
        Serviço: <strong>${data.service.name}</strong> | previsão: <strong>${prediction.predicted_minutes} min</strong> | confiança: <strong>${Math.round(prediction.confidence * 100)}%</strong><br>
        <span class="muted">${prediction.source}</span>
      </div>
      ${data.suggestions.map((item) => `
        <div class="ai-card">
          <div class="ai-card-top">
            <strong>${item.date_label} • ${item.time_label}</strong>
            <span class="ai-score">Score ${item.score}</span>
          </div>
          <div>Técnico: <strong>${item.technician_name}</strong></div>
          <div class="muted">${item.reason}</div>
          <button type="button" class="btn small" data-start="${item.start}" data-technician-id="${item.technician_id}" data-duration="${item.predicted_minutes}" data-score="${item.score}" data-reason="${item.reason}" onclick="fillSuggestion(this)">Usar esta sugestão</button>
        </div>
      `).join('')}
    `;
  } catch (err) {
    results.innerHTML = '<div class="flash danger">Falha ao consultar a IA.</div>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const clientSelect = byId('client_id');
  if (clientSelect) {
    clientSelect.addEventListener('change', refreshVehiclesByClient);
  }
  const aiButton = byId('aiSuggestBtn');
  if (aiButton) {
    aiButton.addEventListener('click', suggestSchedule);
  }
});
