import React, {useState} from "react";
import {fetchChatResponse} from "../../services/api.jsx";
import "../../Gemini.css"; // Import CSS Style

const Gemini = () => {
    const [isOpen, setIsOpen] = useState(false); // Toggle chat window
    const [message, setMessage] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);

    const toggleChat = () => setIsOpen(!isOpen);

    const handleChange = (e) => {
        setMessage(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = await fetchChatResponse(message);
            setResponse(data.response);
        } catch (error) {
            console.error("Error fetching chat response:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-container">
            {/* Circle Button */}
            <div className="chat-button" onClick={toggleChat}>
                💬
            </div>

            {/* Chat Window */}
            {isOpen && (
                <div className="chat-popup">
                    <div className="chat-header">
                        <h2>💬 Rambling Gambling ChatBot</h2>
                        <button className="close-button" onClick={toggleChat}>
                            ✖
                        </button>
                    </div>
                    <form onSubmit={handleSubmit} className="chat-form">
                        <input
                            type="text"
                            value={message}
                            onChange={handleChange}
                            placeholder="Ask your question..."
                            className="chat-input"
                        />
                        <button type="submit" disabled={loading} className="send-button">
                            {loading ? "Sending..." : "Send"}
                        </button>
                    </form>
                    <div className="chat-response">
                        {loading ? (
                            <p>Loading...</p>
                        ) : response ? (
                            <p>{response}</p>
                        ) : null}
                    </div>
                </div>
            )}
        </div>
    );
};

export default Gemini;