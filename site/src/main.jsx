import {StrictMode} from 'react'
import ChatBot from 'react-chatbotify';
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Navbar from './components/layout/Navbar/Navbar.jsx'
import ApiTestBlock from "./components/features/ApiTestBlock.jsx";
import OddsViewer from './components/features/OddsViewer.jsx';
import Gemini from "./components/features/Gemini.jsx";

createRoot(document.getElementById('root')).render(
    <StrictMode>
        {/*<Graph />*/}
        {/*<Navbar/>*/}
        <div>
            This is a test component
            {/* <ApiTestBlock /> */}
            <OddsViewer/>
        </div>
        <div>
            <Gemini/>
        </div>
    </StrictMode>,
)

