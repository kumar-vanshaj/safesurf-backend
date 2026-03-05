
const token = localStorage.getItem("jwt");

if (!token) {
  window.location.href = "/";
}

fetch("https://safesurf-backend.onrender.com/activities", {
  headers: {
    "Authorization": "Bearer " + token
  }
})
.then(res => res.json())
.then(data => {
  const table = document.getElementById("activityTable");

  data.forEach(row => {
    const tr = document.createElement("tr");

    tr.innerHTML = `
      <td>${row[0]}</td>
      <td>${row[1].toFixed(2)}</td>
      <td>${row[2]}</td>
    `;

    table.appendChild(tr);
  });
})
.catch(err => console.error("Dashboard error:", err));

document.getElementById("logout").addEventListener("click", () => {
  localStorage.removeItem("jwt");
  window.location.href = "/";
});
