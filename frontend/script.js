function changeValue(id, amount) {

  const input = document.getElementById(id);

  let value = parseInt(input.value);

  value = value + amount;

  // Prevent negative values
  if (value < 0) {
    value = 0;
  }

  input.value = value;
}

function getRecommendation() {

  let soil = document.getElementById("soil").value;
  let crop = document.getElementById("crop").value;

  document.getElementById("result").innerHTML = `

    <div class="card">

      <h2>🌾 Recommendation</h2>

      <p><b>Soil Type:</b> ${soil}</p>

      <p><b>Crop Type:</b> ${crop}</p>

      <h3>Recommended Fertilizer</h3>
      <p>Urea</p>

      <h3>Confidence</h3>
      <p>86%</p>

      <h3>Estimated Dosage</h3>
      <p>45 kg/hectare</p>

    </div>

  `;
}
