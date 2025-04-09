import {useEffect, useRef, useState} from "react";
import {fetchChatResponse} from "../../services/api.jsx";
import "../../Gemini.css"

const Gemini = ({data}) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState(""); // State for user input
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
                // Handle list responses (e.g., top odds)
                const formattedResponse = response.response.map((item, index) => (
                    `${index + 1}. ${item.home_team} vs ${item.away_team} - Odds: ${JSON.stringify(item.odds)}`
                )).join("\n");
                setMessages((prev) => [...prev, {sender: "bot", text: formattedResponse}]);
            } else if (typeof response.response === "object") {
                // Handle JSON responses (e.g., arbitrage opportunities)
                setMessages((prev) => [
                    ...prev,
                    {sender: "bot", text: "Here are the details:"},
                    {sender: "bot", text: JSON.stringify(response.response, null, 2)},
                ]);
            } else {
                // Handle plain text responses
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
        <div className="chat-popup">
            <div className="chat-header">
                <h2>💬 Betting Insights</h2>
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
    );
};

export default Gemini;