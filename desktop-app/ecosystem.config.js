module.exports = {
  apps: [
    {
      name: 'verity-desktop-server',
      script: 'scripts/run_server_and_test.js',
      cwd: __dirname,
      env: {
        PORT: 3004,
        SHOW_BROWSER: '0',
        NODE_ENV: 'production'
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 3000
    }
  ]
}
