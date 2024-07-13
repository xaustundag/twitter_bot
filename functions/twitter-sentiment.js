const axios = require('axios');
const Sentiment = require('sentiment');
const Twit = require('twit');

const sentiment = new Sentiment();

console.log('CONSUMER_KEY:', process.env.CONSUMER_KEY);
console.log('CONSUMER_SECRET:', process.env.CONSUMER_SECRET);
console.log('ACCESS_TOKEN:', process.env.ACCESS_TOKEN);
console.log('ACCESS_TOKEN_SECRET:', process.env.ACCESS_TOKEN_SECRET);

const twit = new Twit({
  consumer_key: process.env.CONSUMER_KEY,
  consumer_secret: process.env.CONSUMER_SECRET,
  access_token: process.env.ACCESS_TOKEN,
  access_token_secret: process.env.ACCESS_TOKEN_SECRET,
  timeout_ms: 60 * 1000,
  strictSSL: true
});

exports.handler = async (event, context) => {
  const keyword = event.queryStringParameters.keyword;

  if (!keyword) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Keyword query parameter is required' })
    };
  }

  try {
    const { data } = await twit.get('search/tweets', { q: `${keyword} lang:en -filter:retweets`, count: 100 });

    const tweets = data.statuses.map(tweet => tweet.text);
    const sentiments = tweets.map(tweet => sentiment.analyze(tweet));

    const avgSentiment = sentiments.reduce((acc, val) => acc + val.score, 0) / sentiments.length;

    return {
      statusCode: 200,
      body: JSON.stringify({ keyword, avgSentiment, sentiments })
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};
