// main.js
const { app, BrowserWindow } = require("electron");
const path = require("path");

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true, 
            nodeIntegration: true, 
        },
    });

    // In development, you might load from localhost; in production, load your built files
    mainWindow.loadURL("http://localhost:3000"); // or mainWindow.loadFile(path.join(__dirname, 'build/index.html'))

    mainWindow.webContents.openDevTools();
}

app.whenReady().then(createWindow);

app.on("window-all-closed", () => {
    // On macOS it’s common to keep the app running until the user quits explicitly
    if (process.platform !== "darwin") {
        app.quit();
    }
});

app.on("activate", () => {
    // On macOS, recreate a window if none are open
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
