
const CircuitGeometry = require('../models/CircuitGeometry');

function findByName(name) {
  return CircuitGeometry.findOne({ name }).lean();
}

function findAll() {
  return CircuitGeometry.find({}).lean();
}

module.exports = {
  findByName,
  findAll
};
