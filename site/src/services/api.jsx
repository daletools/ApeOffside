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

export const fetchChatResponse = async (message) => {
    // Using GET request to fetch chat response
    try {
        const response = await api.get(`/insights/chatbot/?message=${message}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching chat response:", error);
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
