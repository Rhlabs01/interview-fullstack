import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import PatientCard from "../components/PatientCard";
import type { Clinician, Patient } from "../types";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [clinician, setClinician] = useState<Clinician | null>(null);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const clinicianId = localStorage.getItem("clinicianId");
    if (!clinicianId) {
      void navigate("/");
      return;
    }

    const loadData = async () => {
      try {
        const cliniciansRes = await fetch("/api/clinicians");
        const cliniciansData = await cliniciansRes.json();
        const currentClinician = cliniciansData.clinicians?.find(
          (c: Clinician) => c.id === clinicianId,
        );
        setClinician(currentClinician || null);

        const patientsRes = await fetch(`/api/patients?clinicianId=${clinicianId}`);
        const patientsData = await patientsRes.json();
        setPatients(patientsData.patients || []);
      } catch (e) {
        console.error("Failed to load data:", e);
      }
      setLoading(false);
    };

    void loadData();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("clinicianId");
    void navigate("/");
  };

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-8">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Patients</h1>
          {clinician && (
            <p className="text-gray-600 mt-1">
              {clinician.name} • {clinician.specialty}
            </p>
          )}
        </div>
        <div className="flex items-center gap-4 text-sm">
          <Link to="/medications" className="text-blue-600 hover:underline">
            RxNorm Catalog
          </Link>
          <button onClick={handleLogout} className="text-gray-500 hover:text-gray-700">
            Switch Clinician
          </button>
        </div>
      </div>

      {patients.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-500">No patients assigned to you.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {patients.map((patient) => (
            <PatientCard key={patient.id} patient={patient} />
          ))}
        </div>
      )}

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-400">
          {patients.length} patient{patients.length !== 1 ? "s" : ""} assigned
        </p>
      </div>
    </main>
  );
}
