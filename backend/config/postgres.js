// ============================================================
// FILE: backend/config/postgres.js
// PURPOSE: Direct Postgres client using `pg` Pool for remote DB access
// NOTE: Use via env vars or `DATABASE_URL`. TLS/SSL options supported.
// ============================================================

const { Pool } = require('pg');

const connectionString = process.env.DATABASE_URL || null;

const poolConfig = connectionString ? { connectionString } : {
  host: process.env.POSTGRES_HOST || process.env.PGHOST || 'localhost',
  port: process.env.POSTGRES_PORT ? parseInt(process.env.POSTGRES_PORT, 10) : (process.env.PGPORT ? parseInt(process.env.PGPORT, 10) : 5432),
  database: process.env.POSTGRES_DB || process.env.PGDATABASE || process.env.DB_NAME,
  user: process.env.POSTGRES_USER || process.env.PGUSER || process.env.DB_USER,
  password: process.env.POSTGRES_PASSWORD || process.env.PGPASSWORD || process.env.DB_PASSWORD,
};

// SSL handling: allow enabling via POSTGRES_SSL=true and optional CA
if ((process.env.POSTGRES_SSL || process.env.PGSSLMODE || '').toLowerCase() === 'require' || process.env.POSTGRES_SSL === 'true') {
  poolConfig.ssl = {
    rejectUnauthorized: process.env.DB_SSL_REJECT_UNAUTHORIZED !== '0' && process.env.DB_SSL_REJECT_UNAUTHORIZED !== 'false',
  };
  // optional CA bundle
  if (process.env.POSTGRES_SSL_ROOT_CERT) {
    poolConfig.ssl.ca = process.env.POSTGRES_SSL_ROOT_CERT;
  }
}

const pool = new Pool(poolConfig);

const query = async (text, params) => {
  const client = await pool.connect();
  try {
    const res = await client.query(text, params);
    return res.rows;
  } finally {
    client.release();
  }
};

const isConnected = async () => {
  try {
    const rows = await query('SELECT 1 as ok');
    return Array.isArray(rows);
  } catch (err) {
    return false;
  }
};

module.exports = {
  pool,
  query,
  isConnected,
};
