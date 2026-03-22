const mongoose = require('mongoose');

const activitySchema = new mongoose.Schema({
  user_id: { type: String, required: true, index: true },
  website: { type: String, required: true },
  duration: { type: Number, required: true },
  timestamp: { type: Date, required: true, index: -1 },
  device: { type: String, required: true },
  notifications: { type: Number, default: 0 },
  tab_switches: { type: Number, default: 0 }
});

// Compound index for fast retrieval of latest user activities
activitySchema.index({ user_id: 1, timestamp: -1 });

module.exports = mongoose.model('Activity', activitySchema);
