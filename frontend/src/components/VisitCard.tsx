import { Link } from "react-router-dom";
import { formatDate } from "../dates";

interface VisitCardProps {
  visit: {
    id: string;
    visit_date: string;
    chief_complaint: string;
    clinician_name?: string;
  };
  patientId: string;
}

export default function VisitCard({ visit, patientId }: VisitCardProps) {
  return (
    <Link to={`/patients/${patientId}/visits/${visit.id}`}>
      <div className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow cursor-pointer border border-gray-100">
        <div className="flex justify-between items-start">
          <div>
            <p className="font-medium text-gray-900">
              {visit.chief_complaint || "No chief complaint"}
            </p>
            {visit.clinician_name && (
              <p className="text-sm text-gray-500 mt-1">{visit.clinician_name}</p>
            )}
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">
              {formatDate(visit.visit_date, {
                weekday: "short",
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </p>
          </div>
        </div>
      </div>
    </Link>
  );
}
