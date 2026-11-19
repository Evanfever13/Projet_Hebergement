const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;
const templatesPath = path.join(__dirname, 'templates');

app.use(express.static(templatesPath));

app.get('/config.js', (req, res) => {
  const apiUrl = (
    process.env.API_URL ||
    process.env.VITE_API_URL ||
    ''
  ).replace(/\/+$/, '');

  res.type('application/javascript');
  res.send(`window.APP_CONFIG = Object.freeze({ apiUrl: ${JSON.stringify(apiUrl)} });`);
});

app.get('/', (req, res) => {
  res.sendFile(path.join(templatesPath, 'index.html'));
});

app.get('/ticket', (req, res) => {
  res.sendFile(path.join(templatesPath, 'ticket.html'));
});

if (require.main === module) {
  app.listen(port, () => {
    console.log(`Le serveur tourne sur le port ${port}`);
  });
}

module.exports = app;
