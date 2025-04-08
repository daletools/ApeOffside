import {StrictMode} from 'react'
import ChatBot from 'react-chatbotify';
import {createRoot} from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import Navbar from './components/layout/Navbar/Navbar.jsx'
import ApiTestBlock from "./components/features/ApiTestBlock.jsx";
import OddsViewer from './components/features/OddsViewer.jsx';
import Gemini from "./components/features/Gemini.jsx";
import LiveOddsGraph from "./components/features/Graph.jsx";
import PlayerBlockContainer from "./components/layout/PlayerBlockContainer.jsx";
import InsightsSelector from "./components/features/InsightsSelector.jsx";
import { BrowserRouter } from 'react-router-dom';


createRoot(document.getElementById('root')).render(
    <StrictMode>
        {/*<BrowserRouter>*/}
        {/*<Navbar/>*/}
            <div className="main-content">
        <div>
            <InsightsSelector />
            <PlayerBlockContainer />
            This is a test component
            {/* <ApiTestBlock /> */}
            <OddsViewer/>
        </div>
        <div>
            <Gemini/>
        </div>
                </div>
            {/*</BrowserRouter>*/}
    </StrictMode>,
)

