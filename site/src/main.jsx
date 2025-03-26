import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Navbar from './components/layout/Navbar/Navbar.jsx'
import ApiTestBlock from "./components/features/ApiTestBlock.jsx";
import OddsViewer from './components/features/OddsViewer';
import Chatbot from "./components/features/Chatbot.jsx";

createRoot(document.getElementById('root')).render(
    <StrictMode>
        {/*<Navbar/>*/}
        <div>
            This is a test component
            {/* <ApiTestBlock /> */}
            <OddsViewer/>
            <Chatbot/>
        </div>
    </StrictMode>,
)

