import { useState } from "react";
import UploadForm from "./components/UploadForm";
import StatusMessage from "./components/StatusMessage";

export default function App() {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);

  return (
    <div className="card">
      <div className="card__header">
        <h1>📊 Sales Insight Automator</h1>
        <p>
          Upload your sales data and get an AI-generated summary delivered
          straight to your inbox.
        </p>
      </div>

      <UploadForm
        onSuccess={setSuccess}
        onError={setError}
        setLoading={setLoading}
      />

      <StatusMessage loading={loading} success={success} error={error} />
    </div>
  );
}
