import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

interface Wound {
  id: string;
  location: string;
  wound_type: string;
  description: string;
  status: string;
  assessment_count: number;
  clinician_name: string;
  created_at: string;
}

export default function WoundsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [wounds, setWounds] = useState<Wound[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [activeJob, setActiveJob] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    location: "",
    wound_type: "pressure_ulcer",
    description: "",
  });

  useEffect(() => {
    const clinicianId = localStorage.getItem("clinicianId");
    if (!clinicianId) {
      void navigate("/");
      return;
    }
    loadWounds();
  }, [id, navigate]);

  useEffect(() => {
    if (!activeJob) return;

    const interval = setInterval(async () => {
      const res = await fetch(`/api/jobs/${activeJob}`);
      const data = await res.json();

      if (data.job) {
        setJobStatus(data.job.status);

        if (data.job.status === "completed" || data.job.status === "failed") {
          clearInterval(interval);
          setActiveJob(null);
          loadWounds();
        }
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [activeJob]);

  const loadWounds = async () => {
    try {
      const res = await fetch(`/api/patients/${id}/wounds`);
      const data = await res.json();
      setWounds(data.wounds || []);
    } catch (e) {
      console.error("Failed to load wounds:", e);
    }
    setLoading(false);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setCreating(true);

    const clinicianId = localStorage.getItem("clinicianId");

    try {
      const res = await fetch(`/api/patients/${id}/wounds`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          clinician_id: clinicianId,
          ...formData,
        }),
      });

      const data = await res.json();

      if (data.wound) {
        setActiveJob(data.job_id);
        setJobStatus("pending");
        setShowForm(false);
        setFormData({
          location: "",
          wound_type: "pressure_ulcer",
          description: "",
        });
        loadWounds();
      }
    } catch (e) {
      console.error("Failed to create wound:", e);
    }
    setCreating(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-8 pb-24">
      <Link to={`/patients/${id}`} className="text-blue-600 hover:underline text-sm">
        ← Back to Patient
      </Link>

      <div className="flex justify-between items-center mt-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Wound Care</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm"
        >
          {showForm ? "Cancel" : "Document Wound"}
        </button>
      </div>

      {activeJob && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
            <span className="text-blue-800 text-sm font-medium">
              AI Assessment {jobStatus === "processing" ? "in progress..." : "queued..."}
            </span>
          </div>
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">New Wound Documentation</h2>

          <div className="grid gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full border rounded-lg px-3 py-2"
                placeholder="e.g., Left heel, Sacrum, Right lower leg"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Wound Type</label>
              <select
                value={formData.wound_type}
                onChange={(e) => setFormData({ ...formData, wound_type: e.target.value })}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="pressure_ulcer">Pressure Ulcer</option>
                <option value="diabetic_ulcer">Diabetic Ulcer</option>
                <option value="venous_ulcer">Venous Ulcer</option>
                <option value="surgical">Surgical Wound</option>
                <option value="laceration">Laceration</option>
                <option value="burn">Burn</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full border rounded-lg px-3 py-2"
                placeholder="Describe the wound appearance, surrounding skin, drainage..."
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={creating}
            className="mt-4 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {creating ? "Creating..." : "Create & Analyze"}
          </button>
        </form>
      )}

      <div className="grid gap-4">
        {wounds.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">No wounds documented for this patient.</p>
          </div>
        ) : (
          wounds.map((wound) => (
            <Link key={wound.id} to={`/patients/${id}/wounds/${wound.id}`}>
              <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow border border-gray-100">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-900">{wound.location}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {wound.wound_type.replace(/_/g, " ")} · {wound.assessment_count} assessment
                      {wound.assessment_count !== 1 ? "s" : ""}
                    </p>
                    {wound.description && (
                      <p className="text-sm text-gray-500 mt-1 line-clamp-1">{wound.description}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <span
                      className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        wound.status === "active"
                          ? "bg-yellow-100 text-yellow-800"
                          : wound.status === "healed"
                            ? "bg-green-100 text-green-800"
                            : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {wound.status}
                    </span>
                    <p className="text-sm text-gray-500 mt-1">{formatDate(wound.created_at)}</p>
                  </div>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>
    </main>
  );
}
