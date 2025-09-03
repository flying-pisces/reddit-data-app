/**
 * Subscription Management System
 * Handles freemium tiers and payment processing
 */

import { RevenueCat } from 'react-native-purchases';

class SubscriptionManager {
  constructor() {
    this.tiers = {
      FREE: {
        name: 'Free',
        price: 0,
        dailyLimit: 20,
        features: ['Basic insights', '3 categories', 'Daily limit']
      },
      PRO: {
        name: 'Pro',
        price: 4.99,
        productId: 'reddit_insight_pro_monthly',
        dailyLimit: Infinity,
        features: ['Unlimited insights', 'All categories', 'Priority updates', 'No ads']
      },
      PREMIUM: {
        name: 'Premium',
        price: 9.99,
        productId: 'reddit_insight_premium_monthly',
        dailyLimit: Infinity,
        features: ['Everything in Pro', 'AI predictions', 'Portfolio tracking', 'API access', 'Custom alerts']
      },
      ENTERPRISE: {
        name: 'Enterprise',
        price: 'Custom',
        features: ['API access', 'Custom data feeds', 'Dedicated support', 'SLA guarantee']
      }
    };
  }

  async initialize(apiKey) {
    // Initialize RevenueCat
    await RevenueCat.configure(apiKey);
    
    // Check current subscription
    const purchaserInfo = await RevenueCat.getPurchaserInfo();
    return this.getSubscriptionTier(purchaserInfo);
  }

  async purchaseSubscription(tier) {
    try {
      const productId = this.tiers[tier].productId;
      const purchase = await RevenueCat.purchaseProduct(productId);
      
      // Track conversion
      this.trackRevenue(tier, this.tiers[tier].price);
      
      return {
        success: true,
        tier: tier,
        expiresAt: purchase.expirationDate
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  getSubscriptionTier(purchaserInfo) {
    if (purchaserInfo.entitlements.active['premium']) return 'PREMIUM';
    if (purchaserInfo.entitlements.active['pro']) return 'PRO';
    return 'FREE';
  }

  async checkDailyLimit(userId, currentTier) {
    const tier = this.tiers[currentTier];
    const usage = await this.getDailyUsage(userId);
    
    if (usage >= tier.dailyLimit) {
      return {
        limitReached: true,
        message: `Daily limit of ${tier.dailyLimit} insights reached. Upgrade to Pro for unlimited access!`,
        upgradeOptions: ['PRO', 'PREMIUM']
      };
    }
    
    return { limitReached: false, remaining: tier.dailyLimit - usage };
  }

  async getDailyUsage(userId) {
    // Get from AsyncStorage or API
    const key = `usage_${userId}_${new Date().toDateString()}`;
    const usage = await AsyncStorage.getItem(key);
    return parseInt(usage || '0');
  }

  async incrementUsage(userId) {
    const key = `usage_${userId}_${new Date().toDateString()}`;
    const current = await this.getDailyUsage(userId);
    await AsyncStorage.setItem(key, (current + 1).toString());
  }

  trackRevenue(tier, amount) {
    // Track in analytics
    console.log(`💰 New ${tier} subscription: $${amount}`);
    
    // Send to your backend for metrics
    fetch('/api/revenue', {
      method: 'POST',
      body: JSON.stringify({
        tier,
        amount,
        timestamp: Date.now(),
        platform: 'ios'
      })
    });
  }

  // Calculate potential revenue
  calculateProjectedRevenue(users, conversionRate = 0.05) {
    const payingUsers = users * conversionRate;
    const proUsers = payingUsers * 0.7; // 70% choose Pro
    const premiumUsers = payingUsers * 0.3; // 30% choose Premium
    
    const monthlyRevenue = (proUsers * 4.99) + (premiumUsers * 9.99);
    const yearlyRevenue = monthlyRevenue * 12;
    
    return {
      monthlyRevenue,
      yearlyRevenue,
      payingUsers,
      projectedGrowth: {
        '6_months': yearlyRevenue * 0.5,
        '1_year': yearlyRevenue,
        '2_years': yearlyRevenue * 3, // Assuming growth
        '3_years': yearlyRevenue * 8  // Exponential growth
      }
    };
  }
}

export default new SubscriptionManager();

// Revenue Examples:
// 1,000 users → $250/month → $3,000/year
// 10,000 users → $2,500/month → $30,000/year  
// 100,000 users → $25,000/month → $300,000/year
// 1M users → $250,000/month → $3M/year