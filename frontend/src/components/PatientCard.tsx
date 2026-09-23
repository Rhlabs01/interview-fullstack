import { Link } from "react-router-dom";
import { calculateAge, formatDate } from "../dates";
import type { Patient } from "../types";

interface PatientCardProps {
  patient: Patient;
}

export default function PatientCard({ patient }: PatientCardProps) {
  return (
    <Link to={`/patients/${patient.id}`}>
      <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer border border-gray-100">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="font-semibold text-lg text-gray-900">{patient.name}</h3>
            <p className="text-sm text-gray-500">MRN: {patient.mrn}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">{calculateAge(patient.dob)} years old</p>
            <p className="text-xs text-gray-400">DOB: {formatDate(patient.dob)}</p>
          </div>
        </div>
      </div>
    </Link>
  );
}
