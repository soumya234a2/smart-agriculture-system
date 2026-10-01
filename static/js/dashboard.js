async function loadSensor() {
  const res = await fetch("/api/sensor");
  const data = await res.json();
  document.getElementById("v-moisture").textContent = `${data.soil_moisture_pct}%`;
  document.getElementById("v-ph").textContent = data.soil_ph;
}

async function loadWeather() {
  const res = await fetch("/api/weather");
  const data = await res.json();
  document.getElementById("v-temp").textContent = `${data.temperature_c}°C`;
  document.getElementById("v-humidity").textContent = `${data.humidity_pct}%`;
}

async function loadHealthTrend() {
  const res = await fetch("/api/health-trend");
  const data = await res.json();
  const ctx = document.getElementById("healthChart");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.days,
      datasets: [{
        label: "Crop Health Index",
        data: data.health_index,
        borderColor: "#2e7d32",
        backgroundColor: "rgba(46,125,50,0.15)",
        tension: 0.35,
        fill: true,
      }],
    },
    options: {
      scales: { y: { min: 0, max: 100 } },
      plugins: { legend: { display: false } },
    },
  });
}

document.getElementById("fert-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = new FormData(e.target);
  const body = Object.fromEntries(form.entries());
  const res = await fetch("/api/recommend-fertilizer", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  const box = document.getElementById("fert-result");
  if (data.status === "balanced") {
    box.textContent = data.message;
  } else {
    box.innerHTML = data.recommendations
      .map(r => `<div>${r.fertilizer}: <strong>${r.dosage_kg_per_ha} kg/ha</strong> (covers ${r.nutrient} deficit of ${r.deficit_kg_per_ha} kg/ha)</div>`)
      .join("");
  }
});

document.getElementById("simulate-leaf").addEventListener("click", async () => {
  // Randomised leaf-image feature vector, standing in for OpenCV output
  // extracted from an actual uploaded photo.
  const sample = {
    mean_r: 90 + Math.random() * 60,
    mean_g: 70 + Math.random() * 60,
    mean_b: 40 + Math.random() * 40,
    texture_var: 0.1 + Math.random() * 0.4,
    lesion_ratio: Math.random() * 0.4,
    edge_density: 0.1 + Math.random() * 0.4,
  };
  const res = await fetch("/api/predict-disease", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sample),
  });
  const data = await res.json();
  const box = document.getElementById("disease-result");
  box.innerHTML = `<strong>${data.label}</strong> (${(data.confidence * 100).toFixed(1)}% confidence)<br/>` +
    data.top_3.map(t => `${t.label}: ${(t.confidence * 100).toFixed(1)}%`).join(" · ");
});

loadSensor();
loadWeather();
loadHealthTrend();
setInterval(loadSensor, 8000);
setInterval(loadWeather, 30000);
