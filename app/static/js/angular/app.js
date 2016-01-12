var datasetShareApp = 
  angular.module('datasetShareApp', ['ngFileUpload', 'ui.date'])
         .config( ['$httpProvider', function ($httpProvider) {
            $httpProvider.defaults.useXDomain = true;
            $httpProvider.defaults.withCredentials = true;
         }]);
