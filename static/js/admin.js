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
    // The server usually replies with JSON, but a host level failure such
    // as a proxy timeout can return plain text or HTML instead, so the
    // body is read as text first and only parsed as JSON if it looks like it.
    const text = await res.text();
    let data = {};
    try {
      data = JSON.parse(text);
    } catch (parseErr) {
      data = {};
    }
    if (res.ok) {
      statusEl.textContent = "Thành công, đã xử lý " + data.rows_processed + " dòng.";
    } else {
      statusEl.textContent = "Lỗi: " + (data.detail || data.error || text || res.status);
    }
  } catch (err) {
    statusEl.textContent = "Lỗi kết nối: " + err.message;
  }
});
