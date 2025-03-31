import React, { useState, useRef, useEffect } from "react";
import { fetchChatResponse } from "../../services/api.jsx";
import "../../Gemini.css"; // Import CSS Style

const Gemini = () => {
    const [isOpen, setIsOpen] = useState(false); // Toggle chat window
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]); // Store all messages
    const [loading, setLoading] = useState(false);

    // Dont refresh the page
    const handleRefresh = async (e) => {
        e.preventDefault();
    };

    const chatResponseRef = useRef(null); // Reference for chat response container

    const toggleChat = () => setIsOpen(!isOpen);

    const handleChange = (e) => {
        setMessage(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!message.trim()) {
            return; // Prevent sending empty messages
        }

        const userMessage = { sender: "user", text: message }; // User message object
        setMessages((prevMessages) => [...prevMessages, userMessage]); // Add user message to chat history
        setMessage("");
        setLoading(true);

        try {
            const data = await fetchChatResponse(message);
            const botMessage = { sender: "bot", text: data.response }; // Bot response
            setMessages((prevMessages) => [...prevMessages, botMessage]); // Add bot message to chat history
        } catch (error) {
            console.error("Error fetching chat response:", error);
            const errorMessage = { sender: "bot", text: "Something went wrong. Please try again later." };
            setMessages((prevMessages) => [...prevMessages, errorMessage]); // Add error message to chat history
        } finally {
            setLoading(false);
        }
    };

    // Auto-scroll to bottom when the chatbot is opened or messages are updated
    useEffect(() => {
        if (isOpen && chatResponseRef.current) {
            chatResponseRef.current.scrollTop = chatResponseRef.current.scrollHeight; // Scroll to bottom
        }
    }, [isOpen, messages]); // Trigger scrolling when "isOpen" or "messages" change

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
                    <div className="chat-response" ref={chatResponseRef}>
                        {/* Render all messages */}
                        {messages.map((msg, idx) => (
                            <p
                                key={idx}
                                className={msg.sender === "user" ? "user-message" : "bot-message"}
                            >
                                <strong>{msg.sender === "user" ? "You: " : "Bot: "}</strong>
                                {msg.text}
                            </p>
                        ))}
                        {loading && <p>Loading...</p>}
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
                </div>
            )}
        </div>
    );
};

export default Gemini;