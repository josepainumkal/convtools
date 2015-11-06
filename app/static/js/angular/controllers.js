var datasetShareApp = angular.module('datasetShareApp', ['ngFileUpload']);

datasetShareApp.controller('DatasetShareCtrl', ['$scope', '$log', 'Upload', '$timeout',
  function ($scope, $log, Upload, $timeout) {
    $scope.modelRunName = "Yo mama";
    $scope.modelRunDescription = "Some good dro data";
    $scope.modelRunUUID = mrUUID;

    $scope.uploadPic = function(file) 
    {
      file.upload = Upload.upload({
          url: 'https://angular-file-upload-cors-srv.appspot.com/upload',
          data: {
            file: file, username: $scope.username
          }
      });
      
      file.upload.then(function (response) {
        $timeout(function () {
          file.result = response.data;
          });  
        }, function (response) {
          if (response.status > 0)
          {
            $scope.errorMsg = response.status + ': ' + response.data;
          }
        }, function(evt) {
          // Math.min is IE hack to prevent 200% from being displayed
          file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
        });
    };
}]);
