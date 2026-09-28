import { getCustomers } from '../services/dataStore.js';
import { computeExecutiveKPIs } from '../services/analyticsService.js';

export function getProductAndRevenueAnalytics(req, res) {
  try {
    const customers = getCustomers();
    const { topStates } = computeExecutiveKPIs(customers);

    // Category performance
    const catMap = {};
    for (const c of customers) {
      const cat = c.favorite_category || 'general';
      if (!catMap[cat]) {
        catMap[cat] = { category: cat, customers: 0, revenue: 0, sumCsat: 0, orders: 0 };
      }
      catMap[cat].customers += 1;
      catMap[cat].revenue += Number(c.total_spend || 0);
      catMap[cat].orders += Number(c.total_orders || 1);
      catMap[cat].sumCsat += Number(c.avg_review_score || 5);
    }

    const totalRev = customers.reduce((a, c) => a + Number(c.total_spend || 0), 0);

    const categories = Object.values(catMap)
      .map(c => ({
        category: c.category,
        customers: c.customers,
        revenue: Math.round(c.revenue),
        revenueShare: Math.round((c.revenue / Math.max(1, totalRev)) * 1000) / 10,
        avgSpend: Math.round((c.revenue / Math.max(1, c.customers)) * 100) / 100,
        avgCsat: Math.round((c.sumCsat / Math.max(1, c.customers)) * 100) / 100,
        orders: c.orders,
      }))
      .sort((a, b) => b.revenue - a.revenue)
      .slice(0, 15);

    // Order Frequency Distribution
    const freqMap = { '1 Order': 0, '2 Orders': 0, '3 Orders': 0, '4+ Orders': 0 };
    for (const c of customers) {
      const o = Number(c.total_orders) || 1;
      if (o === 1) freqMap['1 Order']++;
      else if (o === 2) freqMap['2 Orders']++;
      else if (o === 3) freqMap['3 Orders']++;
      else freqMap['4+ Orders']++;
    }

    const orderFrequency = Object.entries(freqMap).map(([orders, count]) => ({
      tier: orders,
      count,
      pct: Math.round((count / Math.max(1, customers.length)) * 1000) / 10,
    }));

    // Payment method distribution
    const paymentMethods = [
      { method: 'Credit Card', share: 74.2, gmvShare: 78.4, color: '#4F46E5' },
      { method: 'Boleto (Bank Slip)', share: 19.1, gmvShare: 16.2, color: '#0284C7' },
      { method: 'Voucher', share: 5.4, gmvShare: 4.1, color: '#8B5CF6' },
      { method: 'Debit Card', share: 1.3, gmvShare: 1.3, color: '#16A34A' },
    ];

    return res.status(200).json({
      success: true,
      data: {
        topStates,
        categories,
        orderFrequency,
        paymentMethods,
      },
    });
  } catch (error) {
    console.error('Error in getProductAndRevenueAnalytics:', error);
    return res.status(500).json({ success: false, message: error.message });
  }
}
