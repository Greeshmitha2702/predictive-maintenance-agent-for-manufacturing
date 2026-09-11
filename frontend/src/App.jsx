import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Header from "./components/Header";
import Welcome from "./pages/Welcome";
import Dashboard from "./pages/Dashboard";
import Analysis from "./pages/Analysis";
import About from "./pages/About";
import History from "./pages/History";

import "./App.css";

function App() {
  // Store the machine prediction result.
  // Both Dashboard and Analysis can use this result.
  const [predictionResult, setPredictionResult] = useState(null);

  return (
    <BrowserRouter>
      <div className="app">

        <Header />

        <Routes>

          {/* Welcome page */}
          <Route path="/" element={<Welcome />} />

          {/* Dashboard receives the prediction result and its setter */}
          <Route
            path="/dashboard"
            element={
              <Dashboard
                predictionResult={predictionResult}
                setPredictionResult={setPredictionResult}
              />
            }
          />

          {/* Analysis receives the same prediction result */}
          <Route
            path="/analysis"
            element={
              <Analysis predictionResult={predictionResult} />
            }
          />
          
          <Route path="/history" element={<History />} />
          
          {/* System information page */}
          <Route path="/about" element={<About />} />

          {/* If an unknown URL is entered, go back to Home */}
          <Route
            path="*"
            element={<Navigate to="/" replace />}
          />

        </Routes>

      </div>
    </BrowserRouter>
  );
}

export default App;