const path = require('path');


module.exports = {
  mode: 'development',
  entry: './frontend/app.js',
  output: {
    path: path.resolve(__dirname, "./modeltranslation_rosetta/static/modeltranslation_rosetta/js/"),
    filename: 'app.js',
  },
  externals: {
    jquery: 'jQuery'
  }
};