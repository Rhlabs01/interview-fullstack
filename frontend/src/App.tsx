import { BrowserRouter, Route, Routes } from "react-router-dom";
import StatusBar from "./components/StatusBar";
import DashboardPage from "./pages/DashboardPage";
import LoginPage from "./pages/LoginPage";
import MedicationsPage from "./pages/MedicationsPage";
import PatientPage from "./pages/PatientPage";
import VisitPage from "./pages/VisitPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="bg-gray-50 min-h-screen pb-12">
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/medications" element={<MedicationsPage />} />
          <Route path="/patients/:id" element={<PatientPage />} />
          <Route path="/patients/:id/visits/:visitId" element={<VisitPage />} />
        </Routes>
        <StatusBar />
      </div>
    </BrowserRouter>
  );
}
