import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Navbar from './Navbar/Navbar.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
      <Navbar />
      <div>
          This is a test component
      </div>
  </StrictMode>,
)