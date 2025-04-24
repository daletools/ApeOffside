import React, {
    useState,
    useRef,
    forwardRef,
    useImperativeHandle,
    useEffect
} from 'react';
import { fetchChatResponse, fetchInsightsAPI } from "../../services/api.jsx";
import "../../Gemini.css";

const Gemini = forwardRef((props, ref) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [prompts, setPrompts] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Function exposed to parent component via ref
    const analyzePlayer = async (playerData) => {
        if (!playerData) return;

        // Add user message to chat
        setMessages(prev => [...prev, {
            sender: 'user',
            text: `I'd like insights on ${playerData.playerName}'s odds for this game.`,
            timestamp: new Date()
        }]);

        setIsChatOpen(true);
        setIsLoading(true);

        try {
            const response = await fetchInsightsAPI(playerData);
            const analysisText = response.data?.analysis ||
                response.analysis ||
                "No analysis available";

            setMessages(prev => [...prev, {
                sender: 'bot',
                text: analysisText,
                timestamp: new Date()
            }]);
        } catch (error) {
            console.error("Error fetching insights:", error);
            setMessages(prev => [...prev, {
                sender: 'bot',
                text: "Sorry, I couldn't analyze those odds. Please try again later.",
                timestamp: new Date()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    // Make analyzePlayer available to parent component
    useImperativeHandle(ref, () => ({
        analyzePlayer
    }));

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
        }
    }, [messages]);

    // Handle prompt selection
    const handlePromptSelect = async (promptType) => {
        setIsLoading(true);

        // Find the prompt text to display in the chat
        const selectedPrompt = prompts.find(p => p.id === promptType);
        if (selectedPrompt) {
            setMessages(prev => [...prev, { sender: "user", text: selectedPrompt.text }]);
        }

        try {
            const response = await fetchChatResponse('', promptType);

            if (response.prompts) {
                setPrompts(response.prompts);
                setMessages(prev => [...prev, { sender: "bot", text: response.response }]);
            } else if (response.data) {
                setMessages(prev => [...prev, {
                    sender: "bot",
                    text: response.response + (response.data ? response.data : '')
                }]);
                setPrompts([]);
            } else if (response.info) {
                setMessages(prev => [
                    ...prev,
                    { sender: "bot", text: response.response },
                    { sender: "bot", text: response.info }
                ]);
                setPrompts([]);
            } else {
                setMessages(prev => [...prev, { sender: "bot", text: response.response }]);
                setPrompts([]);
            }
        } catch (error) {
            setMessages(prev => [
                ...prev,
                { sender: "bot", text: "An error occurred while processing your request." }
            ]);
            setPrompts([]);
        } finally {
            setIsLoading(false);
        }
    };

    // Handle regular message submission
    const handleSendMessage = async (event) => {
        event.preventDefault();
        if (input.trim() === "") return;

        const userMessage = input.trim();
        setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetchChatResponse(userMessage);

            if (response.prompts) {
                setPrompts(response.prompts);
                setMessages(prev => [...prev, { sender: "bot", text: response.response }]);
            } else if (response.data) {
                setMessages(prev => [...prev, {
                    sender: "bot",
                    text: response.response + (response.data ? response.data : '')
                }]);
                setPrompts([]);
            } else if (Array.isArray(response.response)) {
                const formattedResponse = response.response.map((item, index) => (
                    `${index + 1}. ${item.home_team} vs ${item.away_team} - Odds: ${JSON.stringify(item.odds)}`
                )).join("\n");
                setMessages((prev) => [...prev, { sender: "bot", text: formattedResponse }]);
                setPrompts([]);
            } else if (typeof response.response === "object") {
                setMessages((prev) => [
                    ...prev,
                    { sender: "bot", text: "Here are the details:" },
                    { sender: "bot", text: JSON.stringify(response.response, null, 2) },
                ]);
                setPrompts([]);
            } else {
                setMessages((prev) => [...prev, { sender: "bot", text: response.response }]);
                setPrompts([]);
            }
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                { sender: "bot", text: "An error occurred while fetching the response." },
            ]);
            setPrompts([]);
        } finally {
            setIsLoading(false);
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
                            <div key={idx} className={msg.sender === "user" ? "user-message" : "bot-message"}>
                                <strong>{msg.sender === "user" ? "You: " : "Bot: "}</strong>
                                {msg.sender === "bot" && (msg.text.includes("<") && msg.text.includes(">"))
                                    ? <div dangerouslySetInnerHTML={{ __html: msg.text }}/>
                                    : msg.text}
                            </div>
                        ))}

                        {/* Loading indicator */}
                        {isLoading && (
                            <div className="bot-message">
                                <div className="loading-dots">
                                    <span>.</span><span>.</span><span>.</span>
                                </div>
                            </div>
                        )}

                        {/* Premade prompts */}
                        {prompts.length > 0 && (
                            <div className="prompt-buttons">
                                <p><strong>Quick options:</strong></p>
                                {prompts.map((prompt) => (
                                    <button
                                        key={prompt.id}
                                        className="prompt-button"
                                        onClick={() => handlePromptSelect(prompt.id)}
                                        disabled={isLoading}
                                    >
                                        {prompt.text}
                                    </button>
                                ))}
                            </div>
                        )}

                        <div ref={messagesEndRef}></div>
                    </div>
                    <form className="chat-form" onSubmit={handleSendMessage}>
                        <input
                            type="text"
                            className="chat-input"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type your message..."
                            disabled={isLoading}
                        />
                        <button type="submit" className="send-button" disabled={isLoading}>
                            Send
                        </button>
                    </form>
                </div>
            )}
        </>
    );
});

export default Gemini;