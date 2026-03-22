const express = require('express');
const router = express.Router();
const axios = require('axios');

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Trigger model training route
router.post('/train', async (req, res) => {
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/train`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.message, details: "Failed to connect to AI Service" });
  }
});

// Get prediction for user
router.get('/predict/:user_id', async (req, res) => {
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/predict/${req.params.user_id}`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Get global stats
router.get('/stats/global', async (req, res) => {
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/stats/global`);
    res.json(response.data);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
