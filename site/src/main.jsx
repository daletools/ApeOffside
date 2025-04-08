import {StrictMode} from 'react'
import {createRoot} from 'react-dom/client'
import './index.css'
import OddsViewer from './components/features/OddsViewer.jsx';
import Gemini from "./components/features/Gemini.jsx";
import PlayerBlockContainer from "./components/layout/PlayerBlockContainer.jsx";
import InsightsSelector from "./components/features/InsightsSelector.jsx";


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

