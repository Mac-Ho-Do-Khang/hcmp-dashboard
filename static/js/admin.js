const form = document.getElementById("upload-form");
const statusEl = document.getElementById("admin-status");

form.addEventListener("submit", async (e) => {
  // Sends the selected file to the upload endpoint with the admin token
  // in a header, and shows the result or the error message returned.
  e.preventDefault();
  statusEl.textContent = "Đang upload...";

  const fileInput = document.getElementById("report-file");
  const body = new FormData();
  body.append("report_type", document.getElementById("report-type").value);
  body.append("report_month", document.getElementById("report-month").value);
  body.append("file", fileInput.files[0]);

  try {
    const res = await fetch("/upload", {
      method: "POST",
      headers: { "X-Admin-Token": document.getElementById("admin-token").value },
      body: body,
    });
    const data = await res.json();
    if (res.ok) {
      statusEl.textContent = "Thành công, đã xử lý " + data.rows_processed + " dòng.";
    } else {
      statusEl.textContent = "Lỗi: " + (data.detail || data.error || res.status);
    }
  } catch (err) {
    statusEl.textContent = "Lỗi kết nối: " + err.message;
  }
});
