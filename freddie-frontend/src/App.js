// App.js
import React from "react";
import { HashRouter as Router, Routes, Route, Link } from "react-router-dom";
import MusicRecommendationUI from "./components/MusicRecommendationUI";
import StartPage from "./components/StartPage";
import Library from "./components/Library";

function App() {
    return (
        <Router>
            <div className="App flex flex-col min-h-screen">
                <header className="bg-blue-800 text-white p-4 flex justify-between items-center sticky top-0 z-10">
                    <div>
                        <h1 className="text-2xl font-bold">Freddie</h1>
                        <p className="text-sm">DJ Assistant</p>
                    </div>
                    <nav>
                        <Link to="/" className="mr-4 hover:underline">
                            Start
                        </Link>
                        <Link to="/ui" className="mr-4 hover:underline">
                            UI
                        </Link>
                        <Link to="/library" className="hover:underline">
                            Library
                        </Link>
                    </nav>
                </header>
                <main className="container mx-auto py-4 flex-grow">
                    <Routes>
                        {/* Default route: if metadata exists, show UI, else show StartPage */}
                        <Route path="/" element={<StartPage />} />
                        <Route path="/ui" element={<MusicRecommendationUI />} />
                        <Route path="/library" element={<Library />} />
                    </Routes>
                </main>
                <footer className="bg-gray-100 p-4 text-center text-gray-600 text-sm mt-auto">
                    <p>
                        © {new Date().getFullYear()} Freddie DJ Tool.
                        Open-source project.
                    </p>
                    <p>
                        <a
                            href="https://github.com/yourusername/freddie"
                            className="text-blue-600 hover:underline"
                        >
                            GitHub Repository
                        </a>
                    </p>
                </footer>
            </div>
        </Router>
    );
}

export default App;
