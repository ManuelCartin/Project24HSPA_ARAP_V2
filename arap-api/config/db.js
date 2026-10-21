require('dotenv').config();
const mongoose = require('mongoose');

async function connectDB() {
  const mongoURI =
    process.env.MONGODB_URI || 'mongodb://127.0.0.1:27017/ARAP_V2';

  await mongoose.connect(mongoURI);

  console.log('MongoDB conectado correctamente');
  console.log(`Base de datos: ${mongoose.connection.name}`);
}

module.exports = connectDB;
