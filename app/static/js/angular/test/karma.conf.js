module.exports = function(config){
  config.set({

    basePath : '../',

    files : [
      '../../bower_components/angular/angular.js',
      '../../bower_components/angular-mocks/angular-mocks.js',
      '../../js/**/*.js',
      'test/unit/**/*.js'
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['Chrome', 'Firefox', 'IE', 'Safari'],

    plugins : [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-safari-launcher',
            'karma-jasmine'
            ],

    junitReporter : {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }

  });
};
