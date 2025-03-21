import React, { useState, useEffect } from "react";

// Use the fs, path, and ipcRenderer from preload
const { fs, path, ipcRenderer } = window.electron;

function loadConfig() {
    try {
        const configPath = path.join(
            ipcRenderer.sendSync("getAppPath"),
            "appConfig.json"
        );
        const data = fs.readFileSync(configPath, "utf8");
        return JSON.parse(data).folderPath;
    } catch {
        return "";
    }
}

function saveConfig(folderPath) {
    const configPath = path.join(
        ipcRenderer.sendSync("getAppPath"),
        "appConfig.json"
    );
    fs.writeFileSync(configPath, JSON.stringify({ folderPath }, null, 2));
}

function Library() {
    const [mediaFiles, setMediaFiles] = useState([]);
    const [folderPath, setFolderPath] = useState(loadConfig());

    useEffect(() => {
        if (!folderPath) return;
        const files = fs.readdirSync(folderPath);
        const filtered = files.filter((file) => {
            const ext = path.extname(file).toLowerCase();
            return ext === ".mp3" || ext === ".mp4";
        });
        setMediaFiles(filtered);
    }, [folderPath]);

    const handleBrowse = async () => {
        const result = await ipcRenderer.invoke("showOpenDialog", {
            properties: ["openDirectory"],
        });
        if (!result.canceled && result.filePaths.length > 0) {
            const newFolder = result.filePaths[0];
            setFolderPath(newFolder);
            saveConfig(newFolder);
        }
    };

    return (
        <div>
            <h2>Library</h2>
            <button onClick={handleBrowse}>Browse Folder</button>
            {mediaFiles.map((file) => {
                const ext = path.extname(file).toLowerCase();
                const fullPath = path.join(folderPath, file);
                if (ext === ".mp3") {
                    return (
                        <audio key={file} controls>
                            <source src={fullPath} type="audio/mpeg" />
                        </audio>
                    );
                } else {
                    return (
                        <video key={file} width="320" height="240" controls>
                            <source src={fullPath} type="video/mp4" />
                        </video>
                    );
                }
            })}
        </div>
    );
}

export default Library;
