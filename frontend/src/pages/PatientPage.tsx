import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import VisitCard from "../components/VisitCard";
import { calculateAge, formatDate } from "../dates";

interface PatientWithClinician {
  id: string;
  name: string;
  dob: string;
  mrn: string;
  assigned_clinician_id: string;
  clinician_name: string;
  clinician_specialty: string;
}

interface Visit {
  id: string;
  visit_date: string;
  chief_complaint: string;
  clinician_name: string;
}

export default function PatientPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<PatientWithClinician | null>(null);
  const [visits, setVisits] = useState<Visit[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const clinicianId = localStorage.getItem("clinicianId");
    if (!clinicianId) {
      void navigate("/");
      return;
    }
    if (!id) {
      return;
    }

    const loadData = async () => {
      try {
        const [patientRes, visitsRes] = await Promise.all([
          fetch(`/api/patients/${id}`),
          fetch(`/api/patients/${id}/visits`),
        ]);

        const patientData = await patientRes.json();
        const visitsData = await visitsRes.json();

        setPatient(patientData.patient || null);
        setVisits(visitsData.visits || []);
      } catch (e) {
        console.error("Failed to load data:", e);
      }
      setLoading(false);
    };

    void loadData();
  }, [id, navigate]);

  if (loading) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-gray-500">Loading...</p>
      </main>
    );
  }

  if (!patient || !id) {
    return (
      <main className="max-w-4xl mx-auto p-8">
        <p className="text-red-600">Patient not found</p>
        <Link to="/dashboard" className="text-blue-600 hover:underline mt-4 inline-block">
          ← Back to Dashboard
        </Link>
      </main>
    );
  }

  return (
    <main className="max-w-4xl mx-auto p-8">
      <Link to="/dashboard" className="text-blue-600 hover:underline text-sm">
        ← Back to Dashboard
      </Link>

      <div className="mt-4 mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{patient.name}</h1>
        <div className="flex gap-4 mt-2 text-gray-600">
          <span>MRN: {patient.mrn}</span>
          <span>•</span>
          <span>{calculateAge(patient.dob)} years old</span>
          <span>•</span>
          <span>
            DOB:{" "}
            {formatDate(patient.dob, {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </span>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Assigned Clinician</h2>
        <p className="text-gray-700">{patient.clinician_name}</p>
        <p className="text-gray-500 text-sm">{patient.clinician_specialty}</p>
      </div>

      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Visits ({visits.length})</h2>

        {visits.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">No visits recorded.</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {visits.map((visit) => (
              <VisitCard key={visit.id} visit={visit} patientId={id} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
