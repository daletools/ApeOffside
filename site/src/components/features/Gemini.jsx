import {useState, useEffect, useRef} from "react";
import {fetchChatResponse} from "../../services/api.jsx";
import "../../Gemini.css";

const Gemini = ({data}) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState(""); // State for user input
    const [isChatOpen, setIsChatOpen] = useState(false); // State to toggle chat visibility
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (data) {
            const {playerName, trends} = data;

            const insightsMessage = `
                Betting Insights for ${playerName}:
                ${Object.entries(trends || {})
                .map(([bookmaker, trend]) => `
                    ${bookmaker}:
                      Over: ${trend.over?.direction || "N/A"} (${trend.over?.percentChange?.toFixed(2) || "N/A"}%)
                      Under: ${trend.under?.direction || "N/A"} (${trend.under?.percentChange?.toFixed(2) || "N/A"}%)
                    `)
                .join("\n")}
            `;

            setMessages((prev) => [...prev, {sender: "bot", text: insightsMessage}]);
        }
    }, [data]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({behavior: "smooth"});
        }
    }, [messages]);

    const handleSendMessage = async (event) => {
        event.preventDefault();
        if (input.trim() === "") return;

        const userMessage = input.trim();
        setMessages((prev) => [...prev, {sender: "user", text: userMessage}]);
        setInput("");

        try {
            const response = await fetchChatResponse(userMessage);

            if (Array.isArray(response.response)) {
                const formattedResponse = response.response.map((item, index) => (
                    `${index + 1}. ${item.home_team} vs ${item.away_team} - Odds: ${JSON.stringify(item.odds)}`
                )).join("\n");
                setMessages((prev) => [...prev, {sender: "bot", text: formattedResponse}]);
            } else if (typeof response.response === "object") {
                setMessages((prev) => [
                    ...prev,
                    {sender: "bot", text: "Here are the details:"},
                    {sender: "bot", text: JSON.stringify(response.response, null, 2)},
                ]);
            } else {
                setMessages((prev) => [...prev, {sender: "bot", text: response.response}]);
            }
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                {sender: "bot", text: "An error occurred while fetching the response."},
            ]);
        }
    };

    return (
        <>
            {/* Floating Chat Icon */}
            {!isChatOpen && (
                <button
                    className="chat-bubble"
                    onClick={() => setIsChatOpen(true)}
                    aria-label="Open Chat"
                >
                    💬
                </button>
            )}

            {/* Chat Window */}
            {isChatOpen && (
                <div className="chat-popup">
                    <div className="chat-header">
                        <h2>💬 Betting Insights</h2>
                        <button
                            className="close-button"
                            onClick={() => setIsChatOpen(false)}
                            aria-label="Close Chat"
                        >
                            ✖
                        </button>
                    </div>
                    <div className="chat-response">
                        {messages.map((msg, idx) => (
                            <p key={idx} className={msg.sender === "user" ? "user-message" : "bot-message"}>
                                <strong>{msg.sender === "user" ? "You: " : "Bot: "}</strong>
                                {msg.text}
                            </p>
                        ))}
                        <div ref={messagesEndRef}></div>
                    </div>
                    <form className="chat-form" onSubmit={handleSendMessage}>
                        <input
                            type="text"
                            className="chat-input"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message..."
                        />
                        <button type="submit" className="send-button">Send</button>
                    </form>
                </div>
            )}
        </>
    );
};

export default Gemini;