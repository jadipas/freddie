import React, { useState, useEffect } from "react";
import MusicRecommendationUI from "./components/MusicRecommendationUI";
import StartPage from "./components/StartPage";

function App() {
    const [hasMetadata, setHasMetadata] = useState(false);

    useEffect(() => {
        fetch("/data/audio_metadata.json")
            .then((res) => {
                if (res.ok){
                    console.log(res);
                    setHasMetadata(true);
                }else setHasMetadata(false);
            })
            .catch(() => setHasMetadata(false));
    }, []);

    return (
        <div className="App">
            <header className="bg-blue-600 text-white p-4">
                <h1 className="text-2xl font-bold">
                    Freddie DJ Recommendation Tool
                </h1>
                <p className="text-sm">
                    BPM-based song recommendations for DJs
                </p>
            </header>
            <main className="container mx-auto py-4">
                {hasMetadata ? <MusicRecommendationUI /> : <StartPage />}
            </main>
            <footer className="bg-gray-100 p-4 text-center text-gray-600 text-sm">
                <p>
                    © {new Date().getFullYear()} Freddie DJ Tool. Open-source
                    project.
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
    );
}

export default App;
