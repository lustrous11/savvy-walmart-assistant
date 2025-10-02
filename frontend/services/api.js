import axios from 'axios';

// IMPORTANT: Make sure this is your computer's correct IP address
const API_BASE_URL = 'http://192.168.1.9:8000'; // A single URL for your local server

// // --- User & Profile Functions (Mocked for now) ---
// export const updateUserProfile = (userId, profileData) => {
//   console.log('Updating profile for user:', userId);
//   return Promise.resolve({ data: { message: "Profile updated (mocked)." } });
// };
export const getShoppingList = (userId) => {
  return axios.get(`${API_BASE_URL}/shopping-list/${userId}`);
};

export const addMissingIngredientsToList = (userId, recipeId) => {
  return axios.post(`${API_BASE_URL}/shopping-list/${userId}/${recipeId}`);
};

// In api.js

// This function now makes a real API call to your backend
export const updateUserProfile = (userId, profileData) => {
  return axios.patch(`${API_BASE_URL}/users/${userId}/profile`, profileData);
};

// In api.js

export const getMissingIngredients = (userId, recipeId) => {
  return axios.get(`${API_BASE_URL}/smart-cart/${userId}/${recipeId}`);
};

// In api.js

export const getRecipeDetails = (recipeId) => {
  return axios.get(`${API_BASE_URL}/recipe/${recipeId}`);
};

// --- Pantry Functions (Using real API calls) ---
export const getPantryItems = (userId) => {
  // This now makes a real network request
  return axios.get(`${API_BASE_URL}/pantry/${userId}`);
};

export const addPantryItem = (userId, itemData) => {
  // This now makes a real network request
  return axios.post(`${API_BASE_URL}/pantry/${userId}`, itemData);
};

export const deletePantryItem = (itemId) => {
  // This now makes a real network request
  return axios.delete(`${API_BASE_URL}/pantry/item/${itemId}`);
};


// --- Recommendation Functions ---
export const getRecommendations = (userId, queryText) => {
    return axios.post(`${API_BASE_URL}/recommend`, {
        user_id: userId,
        query_text: queryText,
    });
};