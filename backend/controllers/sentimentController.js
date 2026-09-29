
const dataService = require('../services/dataService');
const sentimentService = require('../services/sentimentService');

const getSentimentOverview = async (req, res, next) => {
  try {
    const customers = dataService.getCustomers();
    const overview = sentimentService.computeSentimentOverview();
    const ratingDistribution = sentimentService.computeRatingDistribution();
    const polarityDistribution = sentimentService.computeSentimentPolarityPie();
    const trend = sentimentService.computeLongitudinalSentimentTrend();
    const themes = sentimentService.extractNegativeThemes(5);
    const segmentSatisfaction = sentimentService.computeSentimentBySegment(customers);
    const categorySatisfaction = sentimentService.computeCategorySatisfaction(customers);

    res.json({
      success: true,
      data: {
        overview,
        rating_distribution: ratingDistribution,
        polarity_distribution: polarityDistribution,
        longitudinal_trend: trend,
        negative_themes: themes,
        segment_satisfaction: segmentSatisfaction,
        category_satisfaction: categorySatisfaction,
      },
    });
  } catch (error) {
    next(error);
  }
};

const searchReviews = async (req, res, next) => {
  try {
    const stars = req.query.stars ? req.query.stars.split(',').map(Number) : [1, 2];
    const onlyComments = req.query.only_comments === 'true';

    const reviews = sentimentService.searchReviews({ stars, only_comments: onlyComments });

    res.json({
      success: true,
      data: reviews,
      total_matched: reviews.length,
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getSentimentOverview,
  searchReviews,
};
