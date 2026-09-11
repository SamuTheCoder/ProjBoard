import { Routes, Route } from "react-router-dom";
import { AuthPage } from "./pages/AuthPage/AuthPage";
import { ProjectsPage } from "./pages/ProjectsPage/ProjectsPage";
import { ProjectDashboard } from "./pages/ProjectDashboard/ProjectDashboard";
import { MyTasksPage } from "./pages/MyTasksPage/MyTasksPage";

function App() {
    return (
        <Routes>
            <Route path="/" element={<AuthPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/projects/:projectId" element={<ProjectDashboard />} />
            <Route path="/tasks" element={<MyTasksPage />} />
        </Routes>
    );
}

export default App;
