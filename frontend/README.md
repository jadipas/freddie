# Freddie DJ Frontend

This is the frontend portion of the Freddie DJ Recommendation Tool. It is a React application that loads song metadata (including BPM and other track details) and provides recommendations based on BPM similarity.

## Project Structure

-   **`/public/data/audio_metadata.json`**: Contains the JSON metadata of your music files.
-   **`/src`**: Main React application files (components, utilities, styles).
-   **`package.json`**: Holds dependencies, scripts, and configuration for the React app.

## Prerequisites

-   [Node.js](https://nodejs.org/) (version 14+ recommended)
-   [npm](https://www.npmjs.com/) (comes with Node.js) or [Yarn](https://yarnpkg.com/)

## Getting Started

1. **Clone/Download** the repository containing this frontend project.
2. **Navigate** to the frontend folder (e.g., `cd freddie/frontend`).
3. **Install Dependencies**:
    ```sh
    npm install
    # or
    yarn
    ```
4. **Verify the Audio Data File**:
   Place `audio_metadata.json` at `public/data/audio_metadata.json` so the app can load track information.
5. **Start the Development Server**:
    ```sh
    npm run start
    # or
    yarn start
    ```
    Open [http://localhost:3000](http://localhost:3000) to view and test.

## Building for Production

```sh
npm run build
# or
yarn build
```

Generates optimized static files in the `build` folder.

## Contributing

Submit pull requests or open issues for improvements.

## License

Specify your license here (e.g., MIT License).
