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
            style={{
                height: '100vh',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                //background: 'linear-gradient(135deg, #1b1530 0%, #f7c948 100%)',
                background: 'conic-gradient(from 40deg, white 55%, #f7c948 50%, #1b1530)', //edges around the white square
                //background: 'radial-gradient(circle, white 0%, #1b1530 80%)', //white circle gradient with black
                //background: 'radial-gradient(circle, white 0%, #f7c948 80%, #1b1530 100%)', //yellow circle gradient with black corners
                //background: 'linear-gradient(circle, white 0%, #1b1530 90%)',
                /*background: `radial-gradient(circle, white 0%, #f7c948 50%, #1b1530 100%),
                radial-gradient(circle, black 10%, transparent 10%) 0 0,
                radial-gradient(circle, black 10%, transparent 10%) 50% 50%`,
                backgroundSize: '100% 100%, 50px 50px, 50px 50px',
                backgroundRepeat: 'no-repeat, repeat, repeat',*/
                overflow: 'hidden'
            }}
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
            {/*<h3 style={{fontFamily: 'Courier New, monospace', fontSize: '1.2rem'}}>{displayedText}</h3>*/}
            <h3 style={{color: 'black', fontFamily: 'Copperplate fantasy, serif', letterSpacing: '1px', fontSize: '1.2rem'}}>{displayedText}</h3>


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