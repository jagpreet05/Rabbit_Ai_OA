/**
 * StatusMessage — displays success, error, or loading feedback to the user.
 * Props:
 *   loading  {boolean}
 *   success  {object|null}  — API response object
 *   error    {string|null}  — error message
 */
export default function StatusMessage({ loading, success, error }) {
  if (loading) {
    return (
      <div className="status status--loading" role="status" aria-live="polite">
        ⏳ Analyzing your data and sending email… This may take a moment.
      </div>
    );
  }

  if (error) {
    return (
      <div className="status status--error" role="alert">
        ❌ {error}
      </div>
    );
  }

  if (success) {
    return (
      <div className="status status--success" role="status">
        ✅ {success.message} ({success.rows_analyzed} rows analyzed)
        <br />
        <span style={{ fontSize: "0.85rem", opacity: 0.85 }}>
          Sent to: {success.recipient}
        </span>
      </div>
    );
  }

  return null;
}
