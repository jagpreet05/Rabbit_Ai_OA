import { useState } from "react";
import { uploadSalesFile } from "../api/client";

/**
 * UploadForm — handles file selection, email input, form submission.
 * Props:
 *   onSuccess(data) — called with the API response on success
 *   onError(message) — called with an error message string on failure
 *   setLoading(bool) — lifts loading state to parent
 */
export default function UploadForm({ onSuccess, onError, setLoading }) {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !email) return;

    setLoading(true);
    onSuccess(null); // clear previous result
    onError(null);

    try {
      const data = await uploadSalesFile(file, email);
      onSuccess(data);
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        "Something went wrong. Please try again.";
      onError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form__group">
        <label htmlFor="sales-file">Sales File (CSV or XLSX)</label>
        <input
          id="sales-file"
          type="file"
          accept=".csv,.xlsx,.xls"
          required
          onChange={(e) => setFile(e.target.files[0] ?? null)}
        />
      </div>

      <div className="form__group">
        <label htmlFor="email">Recipient Email</label>
        <input
          id="email"
          type="email"
          placeholder="you@example.com"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      <button
        className="btn"
        type="submit"
        disabled={!file || !email}
      >
        Analyze &amp; Send Summary
      </button>
    </form>
  );
}
