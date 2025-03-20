/**
 * Format duration from seconds to MM:SS format
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration string
 */
export const formatDuration = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, "0")}`;
};

/**
 * Format file path to get just the filename
 * @param {string} filePath - Full file path
 * @returns {string} Just the filename
 */
export const getFileName = (filePath) => {
    if (!filePath) return "";
    const parts = filePath.split(/[/\\]/);
    return parts[parts.length - 1];
};
