// preload.js
const { contextBridge, ipcRenderer } = require("electron");
const fs = require("fs");
const path = require("path");

contextBridge.exposeInMainWorld("electron", {
    fs: fs,
    path: path,
    ipcRenderer: ipcRenderer,
});
