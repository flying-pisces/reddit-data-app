import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  ExternalLink,
  TrendingUp,
  MessageCircle,
  ArrowUp,
  Clock,
  User,
  BarChart3,
  Heart,
  Share2
} from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const CardContainer = styled(motion.div)`
  width: 350px;
  height: 550px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  overflow: hidden;
  position: relative;
  color: #333;
  cursor: grab;
  user-select: none;
  
  &:active {
    cursor: grabbing;
  }
  
  ${props => props.isBackground && `
    opacity: 0.7;
    transform: scale(0.95);
  `}
`;

const CardHeader = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px 20px;
  color: white;
  position: relative;
  
  .category {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    opacity: 0.9;
    margin-bottom: 4px;
  }
  
  .source {
    font-size: 0.85rem;
    opacity: 0.8;
    display: flex;
    align-items: center;
    gap: 8px;
  }
`;

const SwipeIndicator = styled(motion.div)`
  position: absolute;
  top: 50%;
  right: 16px;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 8px;
  backdrop-filter: blur(10px);
  
  ${props => props.direction === 'left' && `
    background: rgba(220, 38, 127, 0.8);
    left: 16px;
    right: auto;
  `}
  
  ${props => props.direction === 'right' && `
    background: rgba(34, 197, 94, 0.8);
  `}
  
  ${props => props.direction === 'up' && `
    background: rgba(59, 130, 246, 0.8);
    top: 16px;
    bottom: auto;
  `}
  
  ${props => props.direction === 'down' && `
    background: rgba(156, 163, 175, 0.8);
    bottom: 16px;
    top: auto;
  `}
`;

const CardContent = styled.div`
  padding: 20px;
  height: calc(100% - 80px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const SummarySection = styled.div`
  margin-bottom: 20px;
  
  .summary-text {
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.5;
    color: #1f2937;
    margin-bottom: 12px;
  }
  
  .key-points {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .key-point {
    background: rgba(102, 126, 234, 0.1);
    color: #4f46e5;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }
`;

const ChartSection = styled.div`
  flex: 1;
  margin-bottom: 20px;
  position: relative;
  
  .chart-container {
    height: 120px;
    position: relative;
  }
  
  .chart-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
  
  .metric {
    text-align: center;
    padding: 8px;
    background: rgba(249, 250, 251, 0.8);
    border-radius: 12px;
    
    .value {
      font-size: 1rem;
      font-weight: 700;
      color: #1f2937;
    }
    
    .label {
      font-size: 0.7rem;
      color: #6b7280;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 2px;
    }
  }
`;

const FooterSection = styled.div`
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  
  .engagement-stats {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 0.8rem;
    color: #6b7280;
  }
  
  .engagement-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .stat {
    display: flex;
    align-items: center;
    gap: 4px;
  }
  
  .timestamp {
    font-size: 0.75rem;
    opacity: 0.7;
  }
`;

const ActionButton = styled(motion.button)`
  background: rgba(102, 126, 234, 0.1);
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  color: #4f46e5;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
  }
`;

const NewsCard = ({ content, swipeDirection, isBackground = false }) => {
  const [showDetails, setShowDetails] = useState(false);

  // Chart configuration
  const chartData = {
    labels: content.chartData?.labels || ['6h', '3h', '1h', 'now'],
    datasets: [
      {
        label: content.chartData?.label || 'Activity',
        data: content.chartData?.data || [10, 25, 45, 60],
        borderColor: 'rgba(102, 126, 234, 0.8)',
        backgroundColor: 'rgba(102, 126, 234, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 5
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        borderWidth: 1
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          display: false
        },
        ticks: {
          font: {
            size: 10
          },
          color: '#9ca3af'
        }
      },
      y: {
        display: false,
        grid: {
          display: false
        }
      }
    },
    elements: {
      point: {
        backgroundColor: '#667eea'
      }
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));
    
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'bullish':
      case 'positive':
        return '#10b981';
      case 'bearish':
      case 'negative':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <CardContainer 
      isBackground={isBackground}
      initial={{ scale: 1, rotate: 0 }}
      animate={{ scale: 1, rotate: 0 }}
    >
      {/* Swipe Direction Indicator */}
      {swipeDirection && (
        <SwipeIndicator
          direction={swipeDirection}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0, opacity: 0 }}
        >
          {swipeDirection === 'left' && <Heart size={16} />}
          {swipeDirection === 'right' && <Share2 size={16} />}
          {swipeDirection === 'up' && <ExternalLink size={16} />}
          {swipeDirection === 'down' && <ArrowUp size={16} style={{ transform: 'rotate(180deg)' }} />}
        </SwipeIndicator>
      )}

      <CardHeader>
        <div className="category">{content.category}</div>
        <div className="source">
          <User size={12} />
          r/{content.subreddit}
        </div>
      </CardHeader>

      <CardContent>
        <SummarySection>
          <div className="summary-text">{content.summary}</div>
          <div className="key-points">
            {content.keyPoints?.map((point, index) => (
              <span key={index} className="key-point">
                {point}
              </span>
            ))}
          </div>
        </SummarySection>

        <ChartSection>
          <div className="chart-title">
            <BarChart3 size={14} />
            {content.chartData?.title || 'Engagement Trend'}
          </div>
          <div className="chart-container">
            <Line data={chartData} options={chartOptions} />
          </div>
        </ChartSection>

        <MetricsGrid>
          <div className="metric">
            <div className="value" style={{ color: getSentimentColor(content.sentiment) }}>
              {content.sentiment || 'Neutral'}
            </div>
            <div className="label">Sentiment</div>
          </div>
          <div className="metric">
            <div className="value">{content.relevanceScore || '85'}%</div>
            <div className="label">Relevance</div>
          </div>
          <div className="metric">
            <div className="value">{content.engagementScore || '92'}</div>
            <div className="label">Engagement</div>
          </div>
        </MetricsGrid>

        <FooterSection>
          <div className="engagement-stats">
            <div className="engagement-left">
              <div className="stat">
                <ArrowUp size={12} />
                {content.upvotes || 0}
              </div>
              <div className="stat">
                <MessageCircle size={12} />
                {content.comments || 0}
              </div>
              <div className="stat">
                <TrendingUp size={12} />
                {content.trendingScore || 0}%
              </div>
            </div>
            <div className="timestamp">
              <Clock size={10} style={{ marginRight: 4, display: 'inline' }} />
              {formatTimeAgo(content.timestamp)}
            </div>
          </div>
          
          <ActionButton
            onClick={(e) => {
              e.stopPropagation();
              window.open(content.originalUrl, '_blank');
            }}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <ExternalLink size={12} />
            View Original
          </ActionButton>
        </FooterSection>
      </CardContent>
    </CardContainer>
  );
};

export default NewsCard;