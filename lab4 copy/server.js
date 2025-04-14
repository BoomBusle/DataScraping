const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(bodyParser.json());

let newsStorage = [];
let idCounter = 1;

app.get('/news', (req, res) => {
  res.status(200).json(newsStorage);
});

app.get('/news/:id', (req, res) => {
  const news = newsStorage.find(n => n.id === Number(req.params.id));
  if (news) {
    res.json(news);
  } else {
    res.status(404).json({ message: 'Новина не знайдена' });
  }
});

app.post('/news', (req, res) => {
  const newsData = { id: idCounter++, ...req.body };
  newsStorage.push(newsData);
  console.log('Додано новину:', newsData);
  res.status(201).json(newsData);
});

app.put('/news/:id', (req, res) => {
  const index = newsStorage.findIndex(n => n.id === Number(req.params.id));
  if (index !== -1) {
    newsStorage[index] = { ...newsStorage[index], ...req.body };
    res.json(newsStorage[index]);
  } else {
    res.status(404).json({ message: 'Новина не знайдена' });
  }
});

app.delete('/news/:id', (req, res) => {
  const index = newsStorage.findIndex(n => n.id === Number(req.params.id));
  if (index !== -1) {
    const deleted = newsStorage.splice(index, 1);
    res.json(deleted[0]);
  } else {
    res.status(404).json({ message: 'Новина не знайдена' });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Сервер працює на http://localhost:${PORT}`);
});