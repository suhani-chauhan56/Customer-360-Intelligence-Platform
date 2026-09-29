const express = require('express');
const router = express.Router();
const customerController = require('../controllers/customerController');

router.get('/', customerController.getCustomersList);
router.get('/:id', customerController.getCustomerDetails);
router.get('/:id/dossier', customerController.getCustomerPdfDossier);

module.exports = router;
