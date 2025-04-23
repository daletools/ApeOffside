import {useState, useEffect, useRef, useImperativeHandle, forwardRef} from "react";
import {fetchChatResponse} from "../../services/api.jsx";
import "../../Gemini.css";

const Gemini = (data) => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState(""); // State for user input
    const [isChatOpen, setIsChatOpen] = useState(false); // State to toggle chat visibility
    const [prompts, setPrompts] = useState([]); // State for premade prompts
    const [isLoading, setIsLoading] = useState(false); // State for loading indicator
    const messagesEndRef = useRef(null);
    const textareaRef = useRef(null); // Ref for the textarea element

    useEffect(() => {
        console.log("Gemini received:", data);
        if (!data) return;

        let analysis = data.data || {};

        if (analysis.type === 'player_analysis_request') {

            let response = JSON.stringify(analysis.data);

            setMessages(prev => [...prev, {
                sender: 'bot',
                text: response,
                timestamp: new Date()
            }]);
            setIsChatOpen(true);
        }
    }, [data]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({behavior: "smooth"});
        }
    }, [messages]);

    // Initialize textarea height when chat is opened
    useEffect(() => {
        if (isChatOpen && textareaRef.current) {
            // Reset to default height
            textareaRef.current.style.height = 'auto';
        }
    }, [isChatOpen]);

    // Fetch prompts when chat is opened
    useEffect(() => {
        const fetchPrompts = async () => {
            if (isChatOpen && messages.length === 0) {
                setIsLoading(true);
                try {
                    // Fetch initial greeting and prompts
                    const response = await fetchChatResponse('', '');
                    if (response.prompts) {
                        setPrompts(response.prompts);
                    }
                    if (response.response) {
                        setMessages([{sender: "bot", text: response.response}]);
                    }
                } catch (error) {
                    console.error("Error fetching prompts:", error);
                    setMessages([{sender: "bot", text: "Welcome! How can I help you today?"}]);
                } finally {
                    setIsLoading(false);
                }
            }
        };

        fetchPrompts();
    }, [isChatOpen]);

    // Handle prompt selection
    const handlePromptSelect = async (promptType) => {
        setIsLoading(true);

        // Find the prompt text to display in the chat
        const selectedPrompt = prompts.find(p => p.id === promptType);
        if (selectedPrompt) {
            setMessages(prev => [...prev, {sender: "user", text: selectedPrompt.text}]);
        }

        try {
            const response = await fetchChatResponse('', promptType);

            // Check if response contains new prompts (for nested prompts)
            if (response.prompts) {
                setPrompts(response.prompts);
                setMessages(prev => [...prev, {sender: "bot", text: response.response}]);
            } else if (response.data) {
                // For responses with HTML data (like tables)
                setMessages(prev => [...prev, {
                    sender: "bot", 
                    text: response.response + (response.data ? response.data : '')
                }]);
                // Clear prompts after selection
                setPrompts([]);
            } else if (response.info) {
                // For responses with additional info
                setMessages(prev => [
                    ...prev, 
                    {sender: "bot", text: response.response},
                    {sender: "bot", text: response.info}
                ]);
                // Clear prompts after selection
                setPrompts([]);
            } else {
                // Standard text response
                setMessages(prev => [...prev, {sender: "bot", text: response.response}]);
                // Clear prompts after selection
                setPrompts([]);
            }
        } catch (error) {
            setMessages(prev => [
                ...prev,
                {sender: "bot", text: "An error occurred while processing your request."}
            ]);
            // Clear prompts on error
            setPrompts([]);
        } finally {
            setIsLoading(false);
        }
    };

    // Function to auto-resize the textarea
    const autoResizeTextarea = () => {
        if (textareaRef.current) {
            // Reset height to auto to get the correct scrollHeight
            textareaRef.current.style.height = 'auto';
            // Set the height to the scrollHeight to expand the textarea
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    };

    // Handle input change and auto-resize
    const handleInputChange = (e) => {
        setInput(e.target.value);
        // Call auto-resize after state update
        setTimeout(autoResizeTextarea, 0);
    };

    const handleSendMessage = async (event) => {
        event.preventDefault();
        if (input.trim() === "") return;

        const userMessage = input.trim();
        setMessages((prev) => [...prev, {sender: "user", text: userMessage}]);
        setInput("");
        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
        setIsLoading(true);

        try {
            const response = await fetchChatResponse(userMessage);

            // Check if response contains new prompts
            if (response.prompts) {
                setPrompts(response.prompts);
                setMessages(prev => [...prev, {sender: "bot", text: response.response}]);
            } else if (response.data) {
                // For responses with HTML data (like tables)
                setMessages(prev => [...prev, {
                    sender: "bot", 
                    text: response.response + (response.data ? response.data : '')
                }]);
                // Clear prompts after selection
                setPrompts([]);
            } else if (Array.isArray(response.response)) {
                const formattedResponse = response.response.map((item, index) => (
                    `${index + 1}. ${item.home_team} vs ${item.away_team} - Odds: ${JSON.stringify(item.odds)}`
                )).join("\n");
                setMessages((prev) => [...prev, {sender: "bot", text: formattedResponse}]);
                // Clear prompts after response
                setPrompts([]);
            } else if (typeof response.response === "object") {
                setMessages((prev) => [
                    ...prev,
                    {sender: "bot", text: "Here are the details:"},
                    {sender: "bot", text: JSON.stringify(response.response, null, 2)},
                ]);
                // Clear prompts after response
                setPrompts([]);
            } else {
                setMessages((prev) => [...prev, {sender: "bot", text: response.response}]);
                // Clear prompts after response
                setPrompts([]);
            }
        } catch (error) {
            setMessages((prev) => [
                ...prev,
                {sender: "bot", text: "An error occurred while fetching the response."},
            ]);
            // Clear prompts on error
            setPrompts([]);
        } finally {
            setIsLoading(false);
        }
    };

    const handlePlayerInsights = async (data) => {
        const response = `Analyzing ${data.playerName}...\n` +
            `Current trends:\n${
                Object.entries(data.trends).map(([bm, trend]) =>
                    `${bm}: Over ${trend.over.direction} ${trend.over.percentChange.toFixed(1)}%`
                ).join('\n')
            }`;

        setMessages(prev => [...prev, {
            sender: 'bot',
            text: response
        }]);
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
                                    ? <div dangerouslySetInnerHTML={{__html: msg.text}}/>
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

                        {/* Premade prompts - show whenever available */}
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
                        <textarea
                            ref={textareaRef}
                            className="chat-input"
                            value={input}
                            onChange={handleInputChange}
                            placeholder="Type your message..."
                            disabled={isLoading}
                            rows="1"
                        />
                        <button type="submit" className="send-button" disabled={isLoading}>
                            Send
                        </button>
                    </form>
                </div>
            )}
        </>
    );
};

export default Gemini;
