import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

interface WoundDetail {
  id: string;
  location: string;
  wound_type: string;
  description: string;
  status: string;
  version: number;
  patient_name: string;
  patient_mrn: string;
  clinician_name: string;
  created_at: string;
  updated_at: string;
}

interface Assessment {
  id: string;
  length_cm: number;
  width_cm: number;
  depth_cm: number;
  tissue_type: string;
  exudate_amount: string;
  healing_stage: string;
  push_score: number;
  ai_generated: boolean;
  notes: string;
  created_at: string;
}

interface Job {
  id: string;
  status: string;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

export default function WoundPage() {
  const { id, woundId } = useParams<{ id: string; woundId: string }>();
  const navigate = useNavigate();
  const [wound, setWound] = useState<WoundDetail | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [description, setDescription] = useState("");
  const [woundStatus, setWoundStatus] = useState("");

  useEffect(() => {
    const clinicianId = localStorage.getItem("clinicianId");
    if (!clinicianId) {
      void navigate("/");
      return;
    }
    loadWound();
  }, [woundId, navigate]);

  const loadWound = async () => {
    try {
      const res = await fetch(`/api/wounds/${woundId}`);
      const data = await res.json();
      if (data.wound) {
        setWound(data.wound);
        setDescription(data.wound.description || "");
        setWoundStatus(data.wound.status);
      }
      setAssessments(data.assessments || []);
      setJobs(data.jobs || []);
    } catch (e) {
      console.error("Failed to load wound:", e);
    }
    setLoading(false);
  };

  const handleSave = async () => {
    if (!wound) return;
    setSaving(true);
    try {
      const res = await fetch(`/api/wounds/${woundId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          description,
          status: woundStatus,
          version: wound.version,
        }),
      });
      const data = await res.json();
      if (data.wound) {
        setWound(data.wound);
        setEditMode(false);
      }
    } catch (e) {
      console.error("Failed to save:", e);
    }
    setSaving(false);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "long",
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

  if (!wound) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-red-600">Wound not found</p>
        <Link
          to={`/patients/${id}/wounds`}
          className="text-blue-600 hover:underline mt-4 inline-block"
        >
          ← Back to Wound Care
        </Link>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-8 pb-24">
      <Link to={`/patients/${id}/wounds`} className="text-blue-600 hover:underline text-sm">
        ← Back to Wound Care
      </Link>

      <div className="mt-4 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{wound.location}</h1>
            <p className="text-gray-600 mt-1">
              {wound.wound_type.replace(/_/g, " ")} · {wound.patient_name} ({wound.patient_mrn})
            </p>
          </div>
          {!editMode && (
            <button
              onClick={() => setEditMode(true)}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              Edit
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">Wound Details</h2>

        {editMode ? (
          <div className="grid gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={woundStatus}
                onChange={(e) => setWoundStatus(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                <option value="active">Active</option>
                <option value="healing">Healing</option>
                <option value="healed">Healed</option>
                <option value="worsening">Worsening</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={4}
                className="w-full border rounded-lg px-3 py-2"
              />
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save Changes"}
              </button>
              <button
                onClick={() => {
                  setEditMode(false);
                  setDescription(wound.description || "");
                  setWoundStatus(wound.status);
                }}
                className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex gap-4 text-sm text-gray-600 mb-3">
              <span
                className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                  wound.status === "active"
                    ? "bg-yellow-100 text-yellow-800"
                    : wound.status === "healed"
                      ? "bg-green-100 text-green-800"
                      : wound.status === "worsening"
                        ? "bg-red-100 text-red-800"
                        : "bg-gray-100 text-gray-800"
                }`}
              >
                {wound.status}
              </span>
              <span>Documented {formatDate(wound.created_at)}</span>
            </div>
            <p className="text-gray-700 whitespace-pre-wrap">
              {wound.description || <span className="text-gray-400 italic">No description</span>}
            </p>
          </div>
        )}
      </div>

      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Assessments ({assessments.length})
        </h2>

        {assessments.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-gray-500">No assessments yet.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {assessments.map((a) => (
              <div key={a.id} className="bg-white rounded-lg shadow p-5">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex items-center gap-2">
                    {a.ai_generated && (
                      <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded font-medium">
                        AI Generated
                      </span>
                    )}
                    <span className="text-sm text-gray-500">{formatDate(a.created_at)}</span>
                  </div>
                  <span className="text-lg font-bold text-gray-900">PUSH {a.push_score}</span>
                </div>

                <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                  <div>
                    <p className="text-gray-500">Size (L×W×D)</p>
                    <p className="font-medium">
                      {a.length_cm} × {a.width_cm} × {a.depth_cm} cm
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Tissue Type</p>
                    <p className="font-medium capitalize">{a.tissue_type}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Exudate</p>
                    <p className="font-medium capitalize">{a.exudate_amount}</p>
                  </div>
                </div>

                <div className="text-sm mb-2">
                  <span className="text-gray-500">Healing Stage: </span>
                  <span className="font-medium capitalize">{a.healing_stage}</span>
                </div>

                {a.notes && (
                  <p className="text-sm text-gray-600 mt-2 pt-2 border-t">{a.notes}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {jobs.length > 0 && (
        <div className="text-sm text-gray-400 mt-8 pt-6 border-t">
          <h3 className="font-medium text-gray-500 mb-2">AI Job History</h3>
          {jobs.map((job) => (
            <div key={job.id} className="flex justify-between py-1">
              <span>
                {job.status === "completed" ? "✓" : job.status === "failed" ? "✗" : "⋯"}{" "}
                {job.status}
              </span>
              <span>{formatDate(job.created_at)}</span>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
