import axios from 'axios';

// URL de base de l'API
const API_BASE_URL = 'http://localhost:8000';

// Créer une instance axios avec la configuration de base
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Service pour gérer les appels API
const apiService = {
  // Vérifier la santé de l'API
  healthCheck: async () => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      console.error('Erreur health check:', error);
      throw error;
    }
  },

  // Créer ou récupérer un joueur
  createPlayer: async (playerName) => {
    try {
      const response = await api.post('/players/', {
        player_name: playerName,
      });
      return response.data;
    } catch (error) {
      console.error('Erreur création joueur:', error);
      throw error;
    }
  },

  // Récupérer les infos d'un joueur
  getPlayer: async (playerName) => {
    try {
      const response = await api.get(`/players/${playerName}`);
      return response.data;
    } catch (error) {
      console.error('Erreur récupération joueur:', error);
      throw error;
    }
  },

  // Jouer une partie
  playGame: async (playerName, playerChoice) => {
    try {
      const response = await api.post('/play/', {
        player_name: playerName,
        player_choice: playerChoice,
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du jeu:', error);
      throw error;
    }
  },

  // Récupérer le classement
  getLeaderboard: async (limit = 10) => {
    try {
      const response = await api.get(`/leaderboard/?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Erreur récupération classement:', error);
      throw error;
    }
  },

  // Récupérer l'historique d'un joueur
  getPlayerHistory: async (playerName, limit = 20) => {
    try {
      const response = await api.get(`/history/${playerName}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Erreur récupération historique:', error);
      throw error;
    }
  },
};

export default apiService;