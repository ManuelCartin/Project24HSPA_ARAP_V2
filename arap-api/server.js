require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');

const telemetryRoutes = require('./routes/telemetryRoutes');
const circuitRoutes = require('./routes/circuitRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

// Rutas
app.use('/api/v1/telemetry', telemetryRoutes);
app.use('/api/v1/circuit', circuitRoutes);

// Ruta de comprobación
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    message: 'ARAP API está funcionando'
  });
});

// Manejo central de errores
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({
    error: 'Error interno del servidor'
  });
});

// Conexión a MongoDB y arranque
async function startServer() {
  try {
    await connectDB();

    app.listen(PORT, () => {
      console.log(`ARAP API disponible en http://localhost:${PORT}`);
    });
  } catch (error) {
    console.error('No se pudo iniciar ARAP API:', error.message);
    process.exit(1);
  }
}

startServer();
