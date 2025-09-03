// Mock data generator for development and testing

const MOCK_CONTENT_TEMPLATES = {
  finance: [
    {
      category: 'Finance',
      subreddit: 'investing',
      summary: 'Tesla stock surges 15% after strong Q3 delivery numbers exceed analyst expectations.',
      keyPoints: ['Strong Q3', 'Exceeded expectations', 'Stock surge'],
      sentiment: 'Bullish',
      chartData: {
        title: 'TSLA Stock Movement',
        labels: ['6h', '4h', '2h', 'Now'],
        data: [100, 105, 110, 115],
        label: 'Stock Price'
      }
    },
    {
      category: 'Finance',
      subreddit: 'wallstreetbets',
      summary: 'GameStop announces NFT marketplace partnership with major gaming companies.',
      keyPoints: ['NFT marketplace', 'Gaming partnerships', 'Transformation'],
      sentiment: 'Bullish',
      chartData: {
        title: 'GME Mentions',
        labels: ['12h', '8h', '4h', 'Now'],
        data: [20, 35, 50, 70],
        label: 'Reddit Mentions'
      }
    },
    {
      category: 'Finance',
      subreddit: 'stocks',
      summary: 'Apple reaches $3 trillion market cap milestone driven by strong iPhone 15 pre-orders.',
      keyPoints: ['$3T market cap', 'iPhone 15', 'Strong pre-orders'],
      sentiment: 'Positive',
      chartData: {
        title: 'AAPL Sentiment',
        labels: ['24h', '18h', '12h', '6h', 'Now'],
        data: [85, 87, 89, 91, 93],
        label: 'Sentiment Score'
      }
    }
  ],
  technology: [
    {
      category: 'Technology',
      subreddit: 'technology',
      summary: 'OpenAI releases GPT-5 with multimodal capabilities and 10x performance improvement.',
      keyPoints: ['GPT-5 release', 'Multimodal', '10x faster'],
      sentiment: 'Positive',
      chartData: {
        title: 'AI Discussion Trend',
        labels: ['6h', '4h', '2h', 'Now'],
        data: [200, 450, 680, 900],
        label: 'Discussion Volume'
      }
    },
    {
      category: 'Technology',
      subreddit: 'programming',
      summary: 'Meta announces open-source Llama 3 model that outperforms GPT-4 on key benchmarks.',
      keyPoints: ['Llama 3', 'Open source', 'Beats GPT-4'],
      sentiment: 'Positive',
      chartData: {
        title: 'Developer Interest',
        labels: ['8h', '6h', '4h', '2h', 'Now'],
        data: [30, 55, 85, 120, 150],
        label: 'GitHub Stars'
      }
    }
  ],
  lifestyle: [
    {
      category: 'Life & Health',
      subreddit: 'productivity',
      summary: 'Study shows 4-day work week increases productivity by 37% while reducing employee stress.',
      keyPoints: ['4-day work week', '37% productivity', 'Less stress'],
      sentiment: 'Positive',
      chartData: {
        title: 'Productivity Metrics',
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        data: [100, 115, 125, 137],
        label: 'Productivity Index'
      }
    },
    {
      category: 'Life & Health',
      subreddit: 'fitness',
      summary: 'Research reveals 15-minute daily walks reduce risk of heart disease by 30%.',
      keyPoints: ['15-min walks', '30% risk reduction', 'Heart health'],
      sentiment: 'Positive',
      chartData: {
        title: 'Health Benefits Timeline',
        labels: ['Week 1', 'Month 1', 'Month 3', 'Month 6'],
        data: [5, 15, 25, 30],
        label: 'Risk Reduction %'
      }
    }
  ],
  gaming: [
    {
      category: 'Gaming',
      subreddit: 'gaming',
      summary: 'Baldurs Gate 3 wins Game of the Year at The Game Awards 2023.',
      keyPoints: ['Baldurs Gate 3', 'GOTY winner', 'Game Awards'],
      sentiment: 'Positive',
      chartData: {
        title: 'Player Count',
        labels: ['Launch', 'Month 1', 'Month 3', 'Now'],
        data: [500000, 800000, 1200000, 1500000],
        label: 'Active Players'
      }
    }
  ]
};

const SUBREDDIT_CATEGORIES = {
  stocks: 'finance',
  investing: 'finance',
  wallstreetbets: 'finance',
  personalfinance: 'finance',
  cryptocurrency: 'finance',
  technology: 'technology',
  programming: 'technology',
  MachineLearning: 'technology',
  startups: 'technology',
  gadgets: 'technology',
  productivity: 'lifestyle',
  fitness: 'lifestyle',
  getmotivated: 'lifestyle',
  lifeprotips: 'lifestyle',
  nutrition: 'lifestyle',
  gaming: 'gaming',
  pcgaming: 'gaming',
  nintendo: 'gaming',
  playstation: 'gaming',
  xbox: 'gaming'
};

const generateRandomMetrics = () => ({
  upvotes: Math.floor(Math.random() * 5000) + 100,
  comments: Math.floor(Math.random() * 500) + 20,
  trendingScore: Math.floor(Math.random() * 40) + 60,
  relevanceScore: Math.floor(Math.random() * 30) + 70,
  engagementScore: Math.floor(Math.random() * 20) + 80,
  timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
});

const generateChartVariation = (baseChart) => ({
  ...baseChart,
  data: baseChart.data.map(value => 
    Math.max(0, Math.floor(value + (Math.random() - 0.5) * value * 0.3))
  )
});

export const generateMockContent = (userInterests = [], count = 10) => {
  const mockContent = [];
  
  // Get relevant categories based on user interests
  const relevantCategories = userInterests.length > 0 
    ? userInterests 
    : ['finance', 'technology', 'lifestyle', 'gaming'];

  for (let i = 0; i < count; i++) {
    // Pick a random category from user interests
    const category = relevantCategories[Math.floor(Math.random() * relevantCategories.length)];
    const templates = MOCK_CONTENT_TEMPLATES[category] || MOCK_CONTENT_TEMPLATES.finance;
    
    // Pick a random template
    const template = templates[Math.floor(Math.random() * templates.length)];
    
    // Generate variations of the template
    const content = {
      id: `mock_${Date.now()}_${i}`,
      ...template,
      ...generateRandomMetrics(),
      chartData: generateChartVariation(template.chartData),
      originalUrl: `https://reddit.com/r/${template.subreddit}/comments/example${i}/`
    };
    
    mockContent.push(content);
  }
  
  // Sort by relevance and engagement for better user experience
  return mockContent.sort((a, b) => 
    (b.relevanceScore + b.engagementScore) - (a.relevanceScore + a.engagementScore)
  );
};

export const generateDetailedContent = (baseContent) => ({
  ...baseContent,
  fullText: `This is a detailed expansion of: ${baseContent.summary}. Here we would include the full original post content, top comments, related discussions, and additional context that helps users understand the complete story.`,
  topComments: [
    {
      author: 'user123',
      content: 'Great analysis! This aligns with what we\'ve been seeing in the market.',
      upvotes: 45,
      timestamp: new Date(Date.now() - Math.random() * 2 * 60 * 60 * 1000).toISOString()
    },
    {
      author: 'investor_pro',
      content: 'I\'ve been following this trend for months. Finally seeing some validation.',
      upvotes: 32,
      timestamp: new Date(Date.now() - Math.random() * 4 * 60 * 60 * 1000).toISOString()
    }
  ],
  relatedPosts: [
    {
      title: 'Related discussion from r/stocks',
      url: 'https://reddit.com/r/stocks/comments/related1',
      score: 234
    },
    {
      title: 'Follow-up analysis from r/investing',
      url: 'https://reddit.com/r/investing/comments/related2',
      score: 156
    }
  ]
});

// Simulate real-time data updates
export const generateRealTimeUpdate = (existingContent) => ({
  ...existingContent,
  upvotes: existingContent.upvotes + Math.floor(Math.random() * 50),
  comments: existingContent.comments + Math.floor(Math.random() * 10),
  trendingScore: Math.min(100, existingContent.trendingScore + Math.floor(Math.random() * 5)),
  chartData: {
    ...existingContent.chartData,
    data: [
      ...existingContent.chartData.data.slice(1),
      existingContent.chartData.data[existingContent.chartData.data.length - 1] + 
      Math.floor((Math.random() - 0.5) * 20)
    ]
  }
});

export default {
  generateMockContent,
  generateDetailedContent,
  generateRealTimeUpdate
};