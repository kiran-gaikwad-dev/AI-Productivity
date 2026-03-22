const mongoose = require('mongoose');

const activitySchema = new mongoose.Schema({
  user_id: { type: String, required: true },
  website: { type: String, required: true },
  duration: { type: Number, required: true },
  timestamp: { type: Date, required: true },
  device: { type: String, required: true },
  notifications: { type: Number, default: 0 },
  tab_switches: { type: Number, default: 0 }
});

module.exports = mongoose.model('Activity', activitySchema);
