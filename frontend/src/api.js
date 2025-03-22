import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

export const fetchUserRepos = async (username) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/user/${username}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching repositories:', error);
    throw error;
  }
};

export const fetchRepoDetails = async (username, repo) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/repo/${username}/${repo}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching repository details:', error);
    throw error;
  }
};

export const fetchUserStats = async (username) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stats/${username}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user stats:', error);
    throw error;
  }
};