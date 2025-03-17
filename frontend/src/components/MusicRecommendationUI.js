import React, { useState, useEffect, useRef } from "react";

const MusicRecommendationUI = () => {
    const [songs, setSongs] = useState([]);
    const [selectedSong, setSelectedSong] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const [numRecommendations, setNumRecommendations] = useState(5);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [uploadFile, setUploadFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadError, setUploadError] = useState(null);
    const [showPlaylistView, setShowPlaylistView] = useState(false);
    const [playlist, setPlaylist] = useState([]);
    const playlistRowRefs = useRef({});

    // Fetch song data from JSON file
    useEffect(() => {
        const fetchSongs = async () => {
            try {
                const response = await fetch("/data/audio_metadata.json");
                if (!response.ok) {
                    throw new Error("Failed to fetch song data");
                }
                const songData = await response.json();
                console.log("Song data loaded:", songData.metadata);
                setSongs(songData.metadata);
            } catch (error) {
                console.error("Error loading song data:", error);
                setSongs([]);
                // Show upload modal when fetch fails
                setShowUploadModal(true);
            }
        };

        fetchSongs();
    }, []);

    // Handle file upload
    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setUploadFile(e.target.files[0]);
            setUploadError(null);
        }
    };

    // Upload and save file
    const handleUpload = async () => {
        if (!uploadFile) {
            setUploadError("Please select a file");
            return;
        }

        // Verify it's a JSON file
        if (!uploadFile.name.endsWith(".json")) {
            setUploadError("Please select a JSON file");
            return;
        }

        setIsUploading(true);
        setUploadError(null);

        try {
            // Create form data for file upload
            const formData = new FormData();
            formData.append("file", uploadFile);

            // Upload the file to server
            const response = await fetch("/api/upload-metadata", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("Failed to upload file");
            }

            // Read the file content to update the UI immediately
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const data = JSON.parse(e.target.result);
                    setSongs(data);
                    setShowUploadModal(false);
                } catch (err) {
                    setUploadError("Invalid JSON format");
                }
            };
            reader.readAsText(uploadFile);
        } catch (error) {
            console.error("Upload failed:", error);
            setUploadError(error.message || "Upload failed");
        } finally {
            setIsUploading(false);
        }
    };

    // Calculate song recommendations based on BPM similarity
    const calculateRecommendations = (selectedSong) => {
        if (!selectedSong) return [];

        const selectedBpm = parseInt(selectedSong.bpm);

        // Calculate BPM difference for each song
        const songsWithDifference = songs
            .filter((song) => song.file_path !== selectedSong.file_path)
            .map((song) => ({
                ...song,
                bpmDifference: Math.abs(parseInt(song.bpm) - selectedBpm),
            }))
            .sort((a, b) => a.bpmDifference - b.bpmDifference);

        // Get top N recommendations
        return songsWithDifference.slice(0, numRecommendations);
    };

    const scrollToSong = (song) => {
        const songElement = playlistRowRefs.current[song.file_path];
        if (songElement) {
            songElement.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
        }
    };

    // Handle song selection
    const handleSongSelect = (song) => {
        setSelectedSong(song);
        const newRecommendations = calculateRecommendations(song);
        setRecommendations(newRecommendations);
        scrollToSong(song);
    };

    const handleSongDoubleClick = (song) => {
        setSongs((prevSongs) => prevSongs.filter((s) => s !== song));
        setPlaylist((prevPlaylist) => [...prevPlaylist, song]);
        setShowPlaylistView(true);
        setTimeout(() => {
            scrollToSong(song);
        }, 0);
    };

    const handleRecommendationClick = (song) => {
        scrollToSong(song);
    };

    // Format duration from seconds to MM:SS
    const formatDuration = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
    };

    // Calculate green intensity for recommended songs
    const getRecommendationColor = (song) => {
        if (!selectedSong || song.file_path === selectedSong.file_path)
            return "bg-white";

        const recommendedSong = recommendations.find(
            (rec) => rec.file_path === song.file_path
        );
        if (!recommendedSong) return "bg-white";

        // Calculate color intensity based on BPM difference
        // Lower difference = more intense green
        const maxDiff =
            recommendations[recommendations.length - 1]?.bpmDifference || 1;
        const minDiff = recommendations[0]?.bpmDifference || 0;
        const range = maxDiff - minDiff || 1;
        const normalizedDiff =
            (recommendedSong.bpmDifference - minDiff) / range;

        // Create a color scale from intense green to light green
        if (normalizedDiff < 0.2) return "bg-green-500";
        if (normalizedDiff < 0.4) return "bg-green-400";
        if (normalizedDiff < 0.6) return "bg-green-300";
        if (normalizedDiff < 0.8) return "bg-green-200";
        return "bg-green-100";
    };

    return (
        <div className="flex flex-col md:flex-row gap-4 p-4 h-screen">
            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full">
                        <h2 className="text-xl font-bold mb-4">
                            Audio Metadata Not Found
                        </h2>
                        <p className="mb-4">
                            The audio metadata file couldn't be loaded. Please
                            upload a JSON file with your music data.
                        </p>
                        <div className="mb-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Upload audio_metadata.json
                            </label>
                            <input
                                type="file"
                                accept=".json"
                                onChange={handleFileChange}
                                className="w-full border border-gray-300 rounded p-2"
                            />
                        </div>

                        {uploadError && (
                            <div className="mb-4 text-red-500">
                                {uploadError}
                            </div>
                        )}

                        <div className="flex justify-end gap-2">
                            <button
                                onClick={handleUpload}
                                disabled={isUploading || !uploadFile}
                                className={`px-4 py-2 rounded ${
                                    isUploading || !uploadFile
                                        ? "bg-gray-300 cursor-not-allowed"
                                        : "bg-blue-500 hover:bg-blue-600 text-white"
                                }`}
                            >
                                {isUploading ? "Uploading..." : "Upload"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Main song list */}
            <div className="w-full md:w-3/4 overflow-y-auto border rounded-lg shadow-md">
                <div className="flex items-center justify-between p-4 text-xl font-bold border-b">
                    <h2>{showPlaylistView ? "Playlist" : "Music Library"}</h2>
                    <button
                        className="bg-blue-500 text-white px-3 py-1 rounded"
                        onClick={() => setShowPlaylistView(!showPlaylistView)}
                    >
                        Change View
                    </button>
                </div>
                {showPlaylistView ? (
                    <div>
                        <h2 className="p-4 text-xl font-bold border-b">
                            Sorted Playlist
                        </h2>
                        <table className="w-full">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="p-2 text-left">Title</th>
                                    <th className="p-2 text-left">Duration</th>
                                    <th className="p-2 text-left">Artist</th>
                                    <th className="p-2 text-left">Genre</th>
                                    <th className="p-2 text-left">BPM</th>
                                </tr>
                            </thead>
                            <tbody>
                                {playlist.map((song, index) => (
                                    <tr
                                        key={index}
                                        ref={(el) =>
                                            (playlistRowRefs.current[
                                                song.file_path
                                            ] = el)
                                        }
                                        className="hover:bg-gray-50 cursor-pointer"
                                        onClick={() => handleSongSelect(song)}
                                    >
                                        <td className="p-2 border-t">
                                            {song.title}
                                        </td>
                                        <td className="p-2 border-t">
                                            {formatDuration(song.duration)}
                                        </td>
                                        <td className="p-2 border-t">
                                            {song.artist}
                                        </td>
                                        <td className="p-2 border-t">
                                            {song.genre}
                                        </td>
                                        <td className="p-2 border-t">
                                            {song.bpm}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div>
                        <table className="w-full">
                            <thead className="bg-gray-100">
                                <tr>
                                    <th className="p-2 text-left">Title</th>
                                    <th className="p-2 text-left">Duration</th>
                                    <th className="p-2 text-left">Artist</th>
                                    <th className="p-2 text-left">Genre</th>
                                    <th className="p-2 text-left">BPM</th>
                                </tr>
                            </thead>
                            <tbody>
                                {songs.map((song, index) => (
                                    <tr
                                        key={index}
                                        ref={(el) =>
                                            (playlistRowRefs.current[
                                                song.file_path
                                            ] = el)
                                        }
                                        className={`hover:bg-gray-50 cursor-pointer ${getRecommendationColor(
                                            song
                                        )}`}
                                        onClick={() => handleSongSelect(song)}
                                        onDoubleClick={() =>
                                            handleSongDoubleClick(song)
                                        }
                                    >
                                        <td className="p-2 border-t">
                                            {song.title}
                                        </td>
                                        <td className="p-2 border-t">
                                            {formatDuration(song.duration)}
                                        </td>
                                        <td className="p-2 border-t">
                                            {song.artist}
                                        </td>
                                        <td className="p-2 border-t">
                                            {song.genre}
                                        </td>
                                        <td className="p-2 border-t">
                                            {song.bpm}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Side panel for recommendations */}
            <div className="w-full md:w-64 border rounded-lg shadow-md">
                <div className="p-4 border-b">
                    <h2 className="text-xl font-bold">Recommendations</h2>
                    <div className="mt-2">
                        <label className="block text-sm font-medium text-gray-700">
                            Number of recommendations:
                        </label>
                        <input
                            type="number"
                            min="1"
                            max="10"
                            value={numRecommendations}
                            onChange={(e) =>
                                setNumRecommendations(parseInt(e.target.value))
                            }
                            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                        />
                    </div>
                </div>

                {selectedSong ? (
                    <div className="p-4">
                        <div className="mb-4">
                            <h3 className="font-semibold">Selected Song:</h3>
                            <p>
                                {selectedSong.title} - {selectedSong.artist}
                            </p>
                            <p className="text-sm text-gray-600">
                                BPM: {selectedSong.bpm}
                            </p>
                        </div>

                        <h3 className="font-semibold mb-2">
                            Top {numRecommendations} Recommendations:
                        </h3>
                        {recommendations.length > 0 ? (
                            <ul className="space-y-2">
                                {recommendations.map((song, index) => (
                                    <li
                                        key={index}
                                        className="p-2 rounded bg-gray-50 hover:bg-gray-100 cursor-pointer"
                                        onClick={() =>
                                            handleRecommendationClick(song)
                                        }
                                    >
                                        <div className="font-medium">
                                            {song.title}
                                        </div>
                                        <div className="text-sm text-gray-600">
                                            {song.artist} - BPM: {song.bpm}
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            Difference: {song.bpmDifference} BPM
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-gray-500">
                                No recommendations available
                            </p>
                        )}
                    </div>
                ) : (
                    <div className="p-4 text-gray-500">
                        Click on a song to see recommendations
                    </div>
                )}
            </div>
        </div>
    );
};

export default MusicRecommendationUI;
