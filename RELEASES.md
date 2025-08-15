# Release Notes

## Version 1.0.8 (2025-08-15)

### ✨ New Features & Enhancements

*   **Groq API Integration**: The application now uses the Groq API for fast and efficient language model inference, replacing the previous OpenAI integration.
*   **Unified README**: The project now features a single, comprehensive `README.md` in the root directory, providing clear setup and usage instructions for both the backend and frontend. The old frontend-specific README has been removed.
*   **Improved Documentation**: The "About" and "Developer" sections in the application's UI have been updated with improved documentation and personalized developer details.
*   **Custom Twitter Error Page**: A new, user-friendly error page has been added for the Twitter link in the developer's social media section, providing a more engaging user experience.
*   **Hugging Face Icon**: The social media links in the "About Developer" section now include a Hugging Face icon, replacing the previous Telegram icon.

### 🐛 Bug Fixes & Refinements

*   **Frontend Connectivity**: Resolved an issue where the frontend would not connect to the backend due to a missing `VITE_API_URL` environment variable.
*   **Groq Model Update**: Fixed a bug where the application was using a decommissioned Groq model (`mixtral-8x7b-32768`). It has been updated to a supported model (`llama3-8b-8192`).
*   **DuckDuckGo Rate Limit**: Temporarily removed the DuckDuckGo search tool from the agent to prevent rate limit errors from disrupting the user experience.
*   **Code Quality**: Cleaned up unused variables and imports in the frontend components (`ChatPage.jsx` and `App.jsx`) to improve code quality and remove `eslint` warnings.

### Git History

*   **Rewritten History**: The Git commit history has been rewritten to a single initial commit, removing all previous history and contributors.
