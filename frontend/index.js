const express = require('express');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;
const templatesPath = path.join(__dirname, 'templates');

app.use(express.static(templatesPath));

app.get('/', (req, res) => {
  res.sendFile(path.join(templatesPath, 'index.html'));
});

app.get('/ticket', (req, res) => {
  res.sendFile(path.join(templatesPath, 'ticket.html'));
});

app.listen(port, () => {
  console.log(`Le serveur tourne sur le port ${port}`);
});