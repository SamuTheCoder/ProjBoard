import { Routes, Route } from "react-router-dom";
import { AuthPage } from "./pages/AuthPage";
import { ProjectsPage } from "./pages/ProjectsPage";

function App() {
    return (
        <Routes>
            <Route path="/" element={<AuthPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
        </Routes>
    );
}

export default App;
