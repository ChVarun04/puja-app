import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import AdminLayout from "./components/AdminLayout";
import Dashboard from "./pages/Dashboard";
import Deities from "./pages/Deities";
import Categories from "./pages/Categories";
import Media from "./pages/Media";

function Protected({ children }) {
  return localStorage.getItem("admin_token") ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Protected><AdminLayout /></Protected>}>
        <Route index element={<Dashboard />} />
        <Route path="deities" element={<Deities />} />
        <Route path="categories" element={<Categories />} />
        <Route path="media" element={<Media />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}