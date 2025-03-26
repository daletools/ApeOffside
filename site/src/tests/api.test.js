import { fetchSports, fetchCurrentGames, fetchOddsAPI } from '../services/api.jsx'; // Import your function

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
    it('should fetch current games', () => {
        const result = fetchCurrentGames('basketball_nba');

        expect(result).toBeDefined();
        expect(Array.isArray(result)).toBe(true);
        if (result.length > 0) {
            expect(result[0]).toHaveProperty('active');
            expect(result[0]).toHaveProperty('key');
        }
    })
});

// describe('fetchOdds', () => {
//     it('should fetch odd for upcoming games', () => {
//         const result = fetchOddsAPI('basketball_nba');
//         expect(result).toBeDefined();
//         expect(Array.isArray(result)).toBe(true);
//         if (result.length > 0) {
//             expect(result[0]).toHaveProperty('away-team');
//             expect(result[0]).toHaveProperty('home-team');
//         }
//     })
// })