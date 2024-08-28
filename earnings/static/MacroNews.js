const { useState, useEffect } = React;
const styled = styled.default;

import React from 'react';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
`;

const Header = styled.header`
  background-color: #000;
  color: #fff;
  padding: 20px 0;
  text-align: center;
`;

const Logo = styled.div`
  font-size: 48px;
  font-weight: bold;
  font-style: italic;
  cursor: pointer;
`;

const NewsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 30px;
`;

const NewsColumn = styled.div`
  width: calc(33.33% - 5px);
`;

const NewsItem = styled.div`
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 15px;
  margin-bottom: 10px;
`;

const NewsMeta = styled.div`
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  font-style: italic;
`;

const NewsTitle = styled.div`
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
  line-height: 1.2;

  a {
    color: #000;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
`;

const NewsSummary = styled.div`
  font-size: 14px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  line-clamp: 6;
`;

const Title = styled.h1`
  font-size: 36px;
  text-align: center;
  margin: 30px 0;
  border-bottom: 2px solid #000;
  padding-bottom: 10px;
`;

const Divider = styled.div`
  border-top: 1px solid #ddd;
  margin: 10px 0;
`;

const MacroNews = () => {
  const [macroNews, setMacroNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMacroNews = async () => {
      try {
        const response = await fetch('/macro-news');
        if (!response.ok) {
          throw new Error('Failed to fetch macro news');
        }
        const data = await response.json();
        setMacroNews(data.macro_news);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMacroNews();
  }, []);

  if (loading) {
    return <p>Loading macro-economic news...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <>
      <Title>Macro-Economic News</Title>
      
      <NewsContainer>
        {macroNews && macroNews.length > 0 ? (
          <NewsColumns>
            {macroNews.map((news, index) => (
              <NewsItem key={index}>
                <NewsMeta>
                  By {news.source} | {news.time_published}
                </NewsMeta>
                <NewsTitle>
                  <a href={news.url} target="_blank" rel="noopener noreferrer">{news.title}</a>
                </NewsTitle>
                <Divider />
                <NewsSummary>
                  {news.summary.length > 250
                    ? `${news.summary.slice(0, 250)}...`
                    : news.summary
                  }
                </NewsSummary>
              </NewsItem>
            ))}
          </NewsColumns>
        ) : (
          <p>No macro-economic news available at the moment.</p>
        )}
      </NewsContainer>
    </>
  );
};

// Don't render immediately, we'll do it when the link is clicked
// ReactDOM.render(<MacroNews />, document.getElementById('root'));