'use strict';
var gulp = require('gulp');
var initGulpTasks = require('gulp-frontend-tools');

var config = {
    project: {
        app_root: '{{ _.project_root }}/frontend/',
        dist_root: '{{ _.project_root }}/modeltranslation_rosetta/static/modeltranslation_rosetta/',
        static_root: '/static/',
    },
    webpack: {
        resolve: {
            alias: {}
        }
    }
}
initGulpTasks(gulp, config, __dirname);