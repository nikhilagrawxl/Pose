import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PoseDirector from "./pages/PoseDirector";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PoseDirector />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
