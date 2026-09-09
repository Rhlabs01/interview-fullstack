import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Clinician } from "../types";

export default function LoginPage() {
  const navigate = useNavigate();
  const [clinicians, setClinicians] = useState<Clinician[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadClinicians = async () => {
    try {
      const res = await fetch("/api/clinicians");
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        setClinicians(data.clinicians || []);
        setError(null);
      }
    } catch (e) {
      setError((e as Error).message);
    }
    setLoading(false);
  };

  const seedDatabase = async () => {
    setSeeding(true);
    try {
      const res = await fetch("/api/seed", { method: "POST" });
      const data = await res.json();
      if (data.error) {
        setError(data.error);
      } else {
        await loadClinicians();
      }
    } catch (e) {
      setError((e as Error).message);
    }
    setSeeding(false);
  };

  const selectClinician = (clinicianId: string) => {
    localStorage.setItem("clinicianId", clinicianId);
    void navigate("/dashboard");
  };

  useEffect(() => {
    void loadClinicians();
  }, []);

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Visit Tracker</h1>
          <p className="text-gray-600 mt-2">Select your clinician profile to continue</p>
        </div>

        {loading ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">Loading clinicians...</p>
          </div>
        ) : error ? (
          <div className="bg-white rounded-lg shadow p-8">
            <p className="text-red-600 mb-4">Error: {error}</p>
            <button
              onClick={() => void seedDatabase()}
              disabled={seeding}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {seeding ? "Initializing..." : "Initialize Database"}
            </button>
          </div>
        ) : clinicians.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8">
            <p className="text-gray-600 mb-4">
              No clinicians found. Initialize the database with sample data.
            </p>
            <button
              onClick={() => void seedDatabase()}
              disabled={seeding}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {seeding ? "Initializing..." : "Initialize Database"}
            </button>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow divide-y">
            {clinicians.map((clinician) => (
              <button
                key={clinician.id}
                onClick={() => selectClinician(clinician.id)}
                className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <p className="font-semibold text-gray-900">{clinician.name}</p>
                <p className="text-sm text-gray-500">{clinician.specialty}</p>
              </button>
            ))}
          </div>
        )}

        <p className="text-center text-xs text-gray-400 mt-8">
          Check database status in the bottom bar
        </p>
      </div>
    </main>
  );
}
