import { useState, useEffect } from 'react';
const WelcomeScreen = () => {

    const fullText = "Primal Picks.  Precision Profits.";
    const [displayedText, setDisplayedText] = useState('');

    useEffect(() => {
        let currentIndex = 0;
        const interval = setInterval(() => {
            if (currentIndex < fullText.length) {
                setDisplayedText(fullText.slice(0, currentIndex + 1));
                currentIndex++;
            } else {
                clearInterval(interval);
            }
        }, 100);

        return () => clearInterval(interval);
    }, []);

    return (
        //background: 'linear-gradient(135deg, #1b1530 0%, #f7c948 100%)'
        <div
            /*style={{
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            background: 'linear-gradient(135deg, #1b1530 0%, #f7c948 100%)',
            overflow: 'hidden'
        }}*/
        >
            <img
                src="/ApeOffsideLogo.png"
                alt="Logo"
                style={{
                    width: '500px',
                    height: '500px',
                    animation: 'popIn 1s ease forwards'
                }}
                />
            <h3 style={{fontFamily: 'Courier New, monospace', fontSize: '1.2rem'}}>{displayedText}</h3>

            <style>
                {`
                @keyframes popIn {
                0% {
                transform: scale(0);
                opacity: 0; 
                }
                60% {
                transform: scale(1.2);
                opacity: 1;
                }
                100% {
                transform: scale(1);
                }
                }
                `}
            </style>
        </div>
    )
}

export default WelcomeScreen;