import { BrowserRouter as Router, Routes, Route } from 'react-router-dom' // Removed Link
import './App.css'
import Chat from './screens/chat/ChatPage'
import TwitterErrorPage from './screens/TwitterErrorPage';
import { ToastContainer } from 'react-toastify'; // Removed toast
import 'react-toastify/dist/ReactToastify.css';
function App() {
  return (
    <main className="main-content">
      <ToastContainer position="top-center" autoClose={3000} />
      <Router>

        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/twitter-error" element={<TwitterErrorPage />} />
        </Routes>


      </Router>
    </main>
  )
}

export default App
