'use strict'
var gulp = require('gulp')
var Tools = require('gulp-frontend-tools')

var config = {
  project: {
    app_root: '{{ _.project_root }}/frontend/',
    dist_root: '{{ _.project_root }}/modeltranslation_rosetta/static/modeltranslation_rosetta/',
    static_root: '/static/',
  },
  webpack: {
    entry_root: "{{ project.app_root }}",
    commonChunk: false,
    config: {
      externals: {
        jquery: 'django.jQuery'
      },
    },
  }
}

Tools(gulp, config).run()
