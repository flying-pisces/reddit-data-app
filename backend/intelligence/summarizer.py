"""
AI-powered content summarization for Reddit posts
Generates concise, one-sentence summaries optimized for mobile consumption
"""

import re
import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# For local LLM integration (future)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# For sentiment analysis
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

@dataclass
class SummarizedContent:
    """Enhanced content with AI-generated insights"""
    original_id: str
    summary_sentence: str
    key_points: List[str]
    sentiment: str
    confidence: float
    complexity_score: int  # 1-5 scale
    category: str
    tickers_mentioned: List[str]
    action_items: List[str]
    chart_data: Optional[Dict]
    generation_time: float

class ContentSummarizer:
    """
    AI-powered content summarizer that transforms lengthy Reddit posts 
    into digestible insights for fast-paced users
    """
    
    def __init__(self, model_type: str = 'local'):
        self.model_type = model_type
        self.logger = logging.getLogger(__name__)
        
        # Initialize sentiment analyzer
        self.sentiment_analyzer = self._setup_sentiment_analyzer()
        
        # Initialize OpenAI if available and configured
        if model_type == 'openai' and OPENAI_AVAILABLE:
            self._setup_openai()
        
        # Regex patterns for different content types
        self.ticker_pattern = re.compile(r'\$([A-Z]{1,5})\b')
        self.price_pattern = re.compile(r'\$?(\d+(?:\.\d{2})?)\s*(?:dollars?|USD|per share)')
        self.percentage_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*%')
        
        # Financial keywords for enhanced processing
        self.financial_keywords = {
            'bullish': ['moon', 'rocket', 'bull', 'up', 'gain', 'surge', 'climb'],
            'bearish': ['crash', 'bear', 'down', 'drop', 'fall', 'decline', 'dump'],
            'neutral': ['hold', 'stable', 'flat', 'sideways', 'range'],
            'speculative': ['yolo', 'diamond hands', 'hodl', 'ape', 'squeeze', 'gamma']
        }
    
    def _setup_sentiment_analyzer(self):
        """Setup sentiment analysis component"""
        if TEXTBLOB_AVAILABLE:
            return TextBlob
        else:
            self.logger.warning("TextBlob not available, using rule-based sentiment")
            return None
    
    def _setup_openai(self):
        """Setup OpenAI API if credentials available"""
        try:
            # OpenAI API key should be in environment or config
            openai.api_key = os.getenv('OPENAI_API_KEY')
            if not openai.api_key:
                self.logger.warning("OpenAI API key not found, falling back to local processing")
                self.model_type = 'local'
        except Exception as e:
            self.logger.error(f"OpenAI setup failed: {e}")
            self.model_type = 'local'
    
    async def summarize_post(self, post_data: Dict) -> SummarizedContent:
        """
        Main summarization method that processes a Reddit post
        and returns enhanced, digestible content
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Extract text content
            full_text = self._extract_content(post_data)
            
            # Generate summary based on available model
            if self.model_type == 'openai' and OPENAI_AVAILABLE:
                summary_data = await self._summarize_with_openai(full_text, post_data)
            else:
                summary_data = await self._summarize_locally(full_text, post_data)
            
            # Extract financial data
            financial_data = self._extract_financial_info(full_text)
            
            # Generate chart data for visualization
            chart_data = self._generate_chart_data(post_data, financial_data)
            
            # Calculate complexity score
            complexity = self._calculate_complexity(full_text)
            
            generation_time = asyncio.get_event_loop().time() - start_time
            
            return SummarizedContent(
                original_id=post_data.get('id', ''),
                summary_sentence=summary_data['summary'],
                key_points=summary_data['key_points'],
                sentiment=summary_data['sentiment'],
                confidence=summary_data['confidence'],
                complexity_score=complexity,
                category=post_data.get('category', 'general'),
                tickers_mentioned=financial_data['tickers'],
                action_items=summary_data.get('action_items', []),
                chart_data=chart_data,
                generation_time=generation_time
            )
            
        except Exception as e:
            self.logger.error(f"Summarization failed for post {post_data.get('id')}: {e}")
            return self._create_fallback_summary(post_data)
    
    def _extract_content(self, post_data: Dict) -> str:
        """Extract and clean text content from post"""
        title = post_data.get('title', '')
        selftext = post_data.get('selftext', '')
        
        # Combine title and body with priority to title
        full_text = f"{title}. {selftext}".strip()
        
        # Clean markdown and formatting
        full_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', full_text)  # Links
        full_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', full_text)  # Bold
        full_text = re.sub(r'\*([^*]+)\*', r'\1', full_text)  # Italic
        full_text = re.sub(r'\n+', ' ', full_text)  # Multiple newlines
        full_text = re.sub(r'\s+', ' ', full_text).strip()  # Multiple spaces
        
        return full_text
    
    async def _summarize_with_openai(self, text: str, post_data: Dict) -> Dict:
        """Use OpenAI API for high-quality summarization"""
        try:
            prompt = self._create_openai_prompt(text, post_data.get('subreddit', ''))
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing Reddit posts into digestible insights for busy users."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            self.logger.error(f"OpenAI summarization failed: {e}")
            return await self._summarize_locally(text, post_data)
    
    async def _summarize_locally(self, text: str, post_data: Dict) -> Dict:
        """Local summarization using rule-based approach"""
        # Extract key sentences using simple scoring
        sentences = self._split_into_sentences(text)
        scored_sentences = self._score_sentences(sentences, post_data.get('subreddit', ''))
        
        # Generate summary from top sentence
        best_sentence = max(scored_sentences, key=lambda x: x[1]) if scored_sentences else ("", 0)
        summary = self._refine_summary(best_sentence[0], post_data)
        
        # Extract key points
        key_points = self._extract_key_points(text, post_data.get('subreddit', ''))
        
        # Determine sentiment
        sentiment_data = self._analyze_sentiment(text)
        
        return {
            'summary': summary,
            'key_points': key_points,
            'sentiment': sentiment_data['sentiment'],
            'confidence': sentiment_data['confidence'],
            'action_items': self._extract_action_items(text)
        }
    
    def _create_openai_prompt(self, text: str, subreddit: str) -> str:
        """Create optimized prompt for OpenAI"""
        return f"""
        Summarize this Reddit post from r/{subreddit} into ONE clear sentence that captures the main point.
        Then list 2-3 key points as short phrases.
        Finally, determine the sentiment (Bullish/Bearish/Neutral/Positive/Negative).

        Post content: {text[:1000]}

        Format your response as:
        Summary: [One sentence summary]
        Key Points: [point1, point2, point3]
        Sentiment: [sentiment]
        """
    
    def _parse_ai_response(self, response: str) -> Dict:
        """Parse structured AI response"""
        lines = response.strip().split('\n')
        
        summary = ""
        key_points = []
        sentiment = "Neutral"
        
        for line in lines:
            if line.startswith('Summary:'):
                summary = line.replace('Summary:', '').strip()
            elif line.startswith('Key Points:'):
                points_text = line.replace('Key Points:', '').strip()
                key_points = [p.strip() for p in points_text.split(',') if p.strip()]
            elif line.startswith('Sentiment:'):
                sentiment = line.replace('Sentiment:', '').strip()
        
        return {
            'summary': summary or "Unable to generate summary",
            'key_points': key_points[:3],  # Limit to 3 points
            'sentiment': sentiment,
            'confidence': 0.8,  # High confidence for AI-generated content
            'action_items': []
        }
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _score_sentences(self, sentences: List[str], subreddit: str) -> List[Tuple[str, float]]:
        """Score sentences based on importance indicators"""
        scored = []
        
        for sentence in sentences:
            score = 0.0
            sentence_lower = sentence.lower()
            
            # Length score (prefer medium-length sentences)
            length_score = min(len(sentence) / 100, 1.0) if len(sentence) < 200 else 0.5
            score += length_score * 0.2
            
            # Financial keywords
            for sentiment, keywords in self.financial_keywords.items():
                matches = sum(1 for kw in keywords if kw in sentence_lower)
                score += matches * 0.3
            
            # Ticker mentions
            ticker_matches = len(self.ticker_pattern.findall(sentence))
            score += ticker_matches * 0.4
            
            # Numbers and percentages (important for financial content)
            if re.search(r'\d+', sentence):
                score += 0.2
            if re.search(r'\d+(?:\.\d+)?%', sentence):
                score += 0.3
            
            # Position in text (first sentences often more important)
            position_penalty = sentences.index(sentence) * 0.1
            score = max(0, score - position_penalty)
            
            scored.append((sentence, score))
        
        return scored
    
    def _refine_summary(self, sentence: str, post_data: Dict) -> str:
        """Refine and optimize summary sentence for mobile consumption"""
        if not sentence:
            return f"Discussion in r/{post_data.get('subreddit', 'unknown')} about {post_data.get('title', 'market topics')}."
        
        # Ensure sentence ends with punctuation
        if not sentence.endswith(('.', '!', '?')):
            sentence += '.'
        
        # Limit length for mobile
        if len(sentence) > 120:
            words = sentence.split()
            while len(' '.join(words)) > 117 and len(words) > 5:
                words.pop()
            sentence = ' '.join(words) + '...'
        
        return sentence
    
    def _extract_key_points(self, text: str, subreddit: str) -> List[str]:
        """Extract 2-3 key points from the content"""
        key_points = []
        
        # Extract tickers
        tickers = self.ticker_pattern.findall(text)
        if tickers:
            key_points.append(f"${tickers[0]}" if len(tickers) == 1 else f"{len(tickers)} stocks")
        
        # Extract percentages
        percentages = self.percentage_pattern.findall(text)
        if percentages:
            key_points.append(f"{percentages[0]}% change")
        
        # Extract sentiment keywords
        text_lower = text.lower()
        for sentiment, keywords in self.financial_keywords.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if matches:
                key_points.append(matches[0].title())
                break
        
        # Ensure we have at least one point
        if not key_points:
            if 'investing' in subreddit.lower() or 'stock' in subreddit.lower():
                key_points.append("Investment discussion")
            else:
                key_points.append(f"r/{subreddit} content")
        
        return key_points[:3]
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment with confidence score"""
        if self.sentiment_analyzer:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = "Positive" if polarity < 0.5 else "Bullish"
            elif polarity < -0.1:
                sentiment = "Negative" if polarity > -0.5 else "Bearish"
            else:
                sentiment = "Neutral"
            
            confidence = min(abs(polarity) * 2, 1.0)
        else:
            # Rule-based sentiment
            text_lower = text.lower()
            positive_count = sum(1 for kw in self.financial_keywords['bullish'] if kw in text_lower)
            negative_count = sum(1 for kw in self.financial_keywords['bearish'] if kw in text_lower)
            
            if positive_count > negative_count:
                sentiment = "Bullish"
                confidence = min(positive_count / 10, 0.8)
            elif negative_count > positive_count:
                sentiment = "Bearish"
                confidence = min(negative_count / 10, 0.8)
            else:
                sentiment = "Neutral"
                confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence
        }
    
    def _extract_financial_info(self, text: str) -> Dict:
        """Extract financial data for chart generation"""
        tickers = list(set(self.ticker_pattern.findall(text)))
        prices = [float(m) for m in self.price_pattern.findall(text)]
        percentages = [float(m) for m in self.percentage_pattern.findall(text)]
        
        return {
            'tickers': tickers[:5],  # Limit to 5 tickers
            'prices': prices[:3],
            'percentages': percentages[:3]
        }
    
    def _generate_chart_data(self, post_data: Dict, financial_data: Dict) -> Optional[Dict]:
        """Generate chart data for visualization"""
        if not financial_data['percentages'] and not financial_data['prices']:
            return None
        
        # Create simple trend data
        if financial_data['percentages']:
            values = financial_data['percentages']
            labels = [f"Point {i+1}" for i in range(len(values))]
        elif financial_data['prices']:
            values = financial_data['prices']
            labels = [f"${v:.2f}" for v in values]
        else:
            # Generate mock trend based on sentiment
            values = [100, 102, 105, 108] if 'bullish' in post_data.get('sentiment', '').lower() else [100, 98, 95, 92]
            labels = ['Start', '1hr', '2hr', 'Now']
        
        return {
            'title': f"{financial_data['tickers'][0]} Trend" if financial_data['tickers'] else 'Activity Trend',
            'labels': labels,
            'data': values,
            'label': 'Value'
        }
    
    def _calculate_complexity(self, text: str) -> int:
        """Calculate content complexity on 1-5 scale"""
        word_count = len(text.split())
        sentence_count = len(self._split_into_sentences(text))
        
        # Average words per sentence
        avg_sentence_length = word_count / max(sentence_count, 1)
        
        # Technical terms count
        technical_terms = len(re.findall(r'\b(?:ROI|EBITDA|P/E|EPS|beta|volatility|derivatives|options)\b', text, re.I))
        
        complexity = 1
        if avg_sentence_length > 15: complexity += 1
        if word_count > 100: complexity += 1
        if technical_terms > 2: complexity += 1
        if len(self.ticker_pattern.findall(text)) > 3: complexity += 1
        
        return min(complexity, 5)
    
    def _extract_action_items(self, text: str) -> List[str]:
        """Extract actionable insights"""
        actions = []
        text_lower = text.lower()
        
        if 'buy' in text_lower: actions.append('Consider buying')
        if 'sell' in text_lower: actions.append('Consider selling')
        if 'hold' in text_lower: actions.append('Hold position')
        if 'watch' in text_lower or 'monitor' in text_lower: actions.append('Monitor closely')
        
        return actions[:2]
    
    def _create_fallback_summary(self, post_data: Dict) -> SummarizedContent:
        """Create basic summary when AI processing fails"""
        title = post_data.get('title', 'Reddit discussion')
        subreddit = post_data.get('subreddit', 'unknown')
        
        return SummarizedContent(
            original_id=post_data.get('id', ''),
            summary_sentence=f"Discussion in r/{subreddit}: {title[:60]}{'...' if len(title) > 60 else ''}",
            key_points=[f"r/{subreddit}", "Community discussion"],
            sentiment="Neutral",
            confidence=0.3,
            complexity_score=2,
            category=post_data.get('category', 'general'),
            tickers_mentioned=[],
            action_items=[],
            chart_data=None,
            generation_time=0.1
        )

# Batch processing for multiple posts
async def batch_summarize(posts: List[Dict], summarizer: ContentSummarizer = None) -> List[SummarizedContent]:
    """Process multiple posts efficiently"""
    if not summarizer:
        summarizer = ContentSummarizer()
    
    tasks = [summarizer.summarize_post(post) for post in posts]
    return await asyncio.gather(*tasks, return_exceptions=True)