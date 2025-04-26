import {fetchSports, fetchCurrentGames, fetchGameOdds} from '../services/api.jsx'; // Import your function

describe('fetchSports', () => {
    it('should fetch sports data from the real API', async () => {
        const result = await fetchSports();

        expect(result).toBeDefined(); // Ensure data is returned
        expect(Array.isArray(result)).toBe(true); // Ensure the result is an array
        if (result.length > 0) {
            expect(result[0]).toHaveProperty('active'); // Ensure each item has an 'id'
            expect(result[0]).toHaveProperty('key'); // Ensure each item has a 'name'
        }
    });
});

describe('fetchCurrentGames', () => {
    it('should fetch current games', async () => {
        const result = await fetchCurrentGames('basketball_nba');

        expect(result).toBeDefined();
        if (result.length > 0) {
            expect(result[0]).toHaveProperty('id');
            expect(result[0]).toHaveProperty('sport_title');
        }
    })
});

describe('fetchOdds', () => {
    it('should fetch odds for an upcoming game', async () => {
        const games = await fetchCurrentGames('basketball_nba');
        const result = fetchGameOdds('basketball_nba', games[0].id, 'player_points');
        expect(result).toBeDefined();
        if (result.length > 0) {
            expect(result[0]).toHaveProperty('away-team');
            expect(result[0]).toHaveProperty('home-team');
        }
    })
})