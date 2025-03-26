import React, {useState} from "react";
import {fetchChatResponse} from "../../services/api.jsx";

const Chatbot = () => {
    const [message, setMessage] = useState("");
    const [response, setResponse] = useState("");
    const [loading, setLoading] = useState(false);

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
        <div>
            <h2>💰 Vinny "The Odds" Calvano</h2>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={message}
                    onChange={handleChange}
                    placeholder="Ask me a question!"
                />
                <button type="submit" disabled={loading}>
                    Send
                </button>
            </form>
            {loading ? (
                <p>Loading...</p>
            ) : response ? (
                <p>{response}</p>
            ) : null}
        </div>
    );
};

export default Chatbot;