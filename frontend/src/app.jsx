import React, { useState } from 'react';
import { fetchUserRepos, fetchUserStats, fetchRepoDetails } from './api';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  PointElement,
  LineElement
} from 'chart.js';
import { Pie, Line } from 'react-chartjs-2';
import {
  FaGithub,
  FaStar,
  FaCodeBranch,
  FaExclamationCircle,
  FaSearch,
  FaCode
} from 'react-icons/fa';

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  PointElement,
  LineElement
);

function App() {
  const [username, setUsername] = useState('');
  const [searchedUsername, setSearchedUsername] = useState('');
  const [repos, setRepos] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [repoDetails, setRepoDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    setSearchedUsername(username);
    setSelectedRepo(null);
    setRepoDetails(null);
    setLoading(true);
    setError('');

    try {
      const [reposData, statsData] = await Promise.all([
        fetchUserRepos(username),
        fetchUserStats(username)
      ]);

      setRepos(reposData.repositories);
      setStats(statsData);
    } catch (err) {
      setError(`Failed to fetch data: ${err.response?.data?.detail || err.message}`);
      setRepos([]);
      setStats(null);
    } finally {
      setLoading(false);
    }
  };

  const getRepoDetails = async (repoName) => {
    setRepoDetails(null);
    setLoading(true);

    try {
      const details = await fetchRepoDetails(searchedUsername, repoName);
      setRepoDetails(details);
      setSelectedRepo(repoName);
    } catch (err) {
      setError(`Failed to fetch repository details: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getLanguageChartData = () => {
    if (!stats || !stats.language_distribution) return null;

    const languages = Object.keys(stats.language_distribution);
    const counts = Object.values(stats.language_distribution);

    const colorMap = {
      JavaScript: '#f1e05a',
      Python: '#3572A5',
      Java: '#b07219',
      TypeScript: '#2b7489',
      C: '#555555',
      'C++': '#f34b7d',
      'C#': '#178600',
      PHP: '#4F5D95',
      Ruby: '#701516',
      Go: '#00ADD8',
      Rust: '#dea584'
    };

    const backgroundColors = languages.map(lang =>
      colorMap[lang] || `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`
    );

    return {
      labels: languages,
      datasets: [
        {
          data: counts,
          backgroundColor: backgroundColors,
          borderWidth: 1
        }
      ]
    };
  };

  const getTimelineChartData = () => {
    if (!stats || !stats.timeline || stats.timeline.length === 0) return null;

    return {
      labels: stats.timeline.map(item => item.date),
      datasets: [
        {
          label: 'Repositories',
          data: stats.timeline.map(item => item.repos),
          fill: false,
          borderColor: '#3498db',
          tension: 0.1
        }
      ]
    };
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gray-800 text-white p-4">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <FaGithub className="text-3xl mr-2" />
            <h1 className="text-2xl font-bold">CrispHub Analytics</h1>
          </div>

          <form onSubmit={handleSearch} className="flex">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter GitHub username"
              className="px-4 py-2 rounded-l text-black"
            />
            <button
              type="submit"
              className="bg-blue-500 px-4 py-2 rounded-r flex items-center"
            >
              <FaSearch className="mr-2" /> Search
            </button>
          </form>
        </div>
      </header>

      <main className="container mx-auto p-4">
        {loading && (
          <div className="loading flex justify-center items-center py-4">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        )}

        {error && (
          <div className="error flex items-center text-red-600 py-4">
            <FaExclamationCircle className="mr-2" /> {error}
          </div>
        )}

        {/* Content rendering logic */}
        {/* You can continue your components and close all remaining tags */}
      </main>
    </div>
  );
}

export default App;
