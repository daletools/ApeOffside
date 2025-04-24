import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const fetchSports = async () => {
    try {
        const response = await api.get('/core/sports');
        return response.data;
    } catch (error) {
        console.log(`Error fetching sports: ${error}`);
        throw error;
    }
};

export const fetchCurrentGames = async (sport) => {
    try {
        const response = await api.get(`/core/current-games/${sport}`);
        return response.data;
    } catch (error) {
        console.log(`Error fetching current games for ${sport}: ${error}`);
        throw error;
    }
};

export const fetchGameOdds = async (sport, id, market) => {
    try {
        const response = await api.get(`odds/event/${sport}/${id}/${market}`)
        return response.data;
    } catch (error) {
        console.log(`Error fetching game: ${error}`);
    }
}

export const fetchOddsAPI = async (sport) => {
    const response = await api.get(`/odds/${sport}`);
    return response.data;
};

export const fetchInsightsAPI = async (data) => {
    try {
        console.log("Fetching insights via POST", data);
        const response = await api.post('/insights/insights/', data); // POST with JSON body
        return response.data;
    } catch (error) {
        console.error("Error fetching insights:", error);
        throw error; // Re-throw to handle in the component
    }
};

export const fetchChatResponse = async (message, promptType = '') => {
    // Using GET request to fetch chat response
    try {
        let url = '/insights/chatbot/';
        const params = new URLSearchParams();

        if (message) {
            params.append('message', message);
        }

        if (promptType) {
            params.append('prompt_type', promptType);
        }

        const queryString = params.toString();
        if (queryString) {
            url += `?${queryString}`;
        }

        const response = await api.get(url);
        return response.data;
    } catch (error) {
        console.error("Error fetching chat response:", error);
        return { response: "Sorry, there was an error processing your request." };
    }
};

export async function fetchArbitrageOpportunities() {
    const res = await fetch("http://localhost:8000/arbitrage/opportunities/");
    return await res.json();
}

export async function fetchValueBets() {
    const res = await fetch("http://localhost:8000/arbitrage/valuebets/");
    return await res.json();
}

export async function fetchPlayerPropArbitrage(market = "player_points") {
    const res = await fetch(`http://localhost:8000/arbitrage/player-props/?market=${market}`);
    return await res.json();
}
