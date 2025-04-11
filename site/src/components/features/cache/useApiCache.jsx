

const cache = {};

export const getCachedData = (key) => {
  const entry = cache[key];
  if (!entry) return null;

  const isExpired = Date.now() - entry.timestamp > 60 * 1000;
  if (isExpired) return null;

  console.log(`[CACHE] ✅ Returning cached data for "${key}" (${Date.now() - entry.timestamp}ms old)`);
  return entry.data;
};

export const setCachedData = (key, data) => {
  cache[key] = {
    data,
    timestamp: Date.now(),
  };
  console.log(`[CACHE] 💾 Stored fresh data for "${key}"`);
};
