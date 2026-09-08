module.exports = {
  apps: [
    {
      name: 'phowhisper-server',
      script: 'server.py',
      interpreter: 'python',
      env: {
        SERVER_HOST: '0.0.0.0',
        SERVER_PORT: '8000',
        USE_GPU: '0'
      },
      error_file: './logs/phowhisper-err.log',
      out_file: './logs/phowhisper-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      restart_delay: 4000,
      max_memory_restart: '1G',
      autorestart: true,
      watch: false
    },
    {
      name: 'ai-gateway',
      script: 'gateway.js',
      interpreter: 'node',
      env: {
        PORT: '3000',
        NODE_ENV: 'production'
      },
      error_file: './logs/gateway-err.log',
      out_file: './logs/gateway-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      restart_delay: 2000,
      autorestart: true,
      watch: false
    }
  ]
};
