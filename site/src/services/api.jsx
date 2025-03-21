import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

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