import React, {useState, useRef, useEffect} from "react";
import {fetchChatResponse} from "../../services/api.jsx";
import "../../Gemini.css"; // Import CSS Style

const Gemini = () => {
    const [isOpen, setIsOpen] = useState(false); // Toggle chat window
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]); // Chat messages
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null); // Create a reference for the last message

    const toggleChat = () => {
        // Show default prompt when chat is opened
        if (!isOpen && messages.length === 0) {
            setMessages([{sender: "bot", text: "How can I help you win big?!"}]);
        }
        setIsOpen(!isOpen);
    };

    const handleChange = (e) => {
        setMessage(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!message.trim()) return;

        const userMessage = {sender: "user", text: message};
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        setMessage("");
        setLoading(true);

        try {
            const data = await fetchChatResponse(message); // API call to backend
            const botMessage = {sender: "bot", text: data.response};
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error("Error fetching chat response:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                {sender: "bot", text: "Something went wrong. Please try again later."},
            ]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Scroll to the last message whenever 'messages' changes
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({behavior: "smooth"});
        }
    }, [messages]);

    return (
        <div className="chat-container">
            <div className="chat-button" onClick={toggleChat}>
                💬
            </div>

            {isOpen && (
                <div className="chat-popup">
                    <div className="chat-header">
                        <h2>💬 Rambling Gambling ChatBot</h2>
                        <button className="close-button" onClick={toggleChat}>
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
                        {loading && <p>Loading...</p>}
                        {/* Dummy div for scrolling */}
                        <div ref={messagesEndRef}/>
                    </div>
                    <form onSubmit={handleSubmit}>
                        <input
                            className="chat-input"
                            type="text"
                            value={message}
                            onChange={handleChange}
                            placeholder="Ask your question..."
                        />
                        <button
                            className="send-button"
                            type="submit"
                            disabled={loading}>
                            {loading ? "Sending..." : "Send"}
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
};

export default Gemini;